# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 2016

Module:
    shuffled_louvain - Louvain community detection with shuffled node sequence

Authors:
    Fabio Saracco, Mika Straka

Description:
    Louvain community detection with shuffled node sequence are performed and
    the community structure with the highest modularity score are returned.
    The igraph.community_multilevel algorithm is used for the community
    detection.

Usage:
    Be G the igraph.Graph object on which we want to perform a community
    detection and be n the number of iteration we want to run in order to find
    the maximaml modularity.

    Import module:
        $ import shuffled_louvain as shulou

    Run n-times the community detection:
        $ vc = shulou.shuffled_comdet(G, n)

    The membership list of the detected communityes can be accessed with
        # vc.membership

NB Parallel computation:
    The module uses the Python multiprocessing package and the calculation of
    the community structures is executed in parallel. The number of parallel
    processes depends on the number of CPUs of the work station, see variable
    "numprocs" in method "shuffled_comdet".

    If the calculation should NOT be performed in parallel, use
        $ shulou.shuffled_comdet(G, n, parallel=False)
"""

import multiprocessing as mp
import igraph as ig
import random

# initialize global input and output queues
input_queue = mp.Queue()
output_queue = mp.Queue()


def shuffled_comdet(g, numiter, parallel=True):
    """Run 'numiter' Louvain community detections of the graph g in parallel
    with reshuffled node sequence. Return the Vertext clustering object with the
    highest modularity. The number of processes which run in parallel are
    determined by the number of CPU of the work station (see below).

    :param g: igraph.Graph object
    :param numiter: number of reshuffled community detections we want to run
    :type numiter: int
    :param parallel: if True, the numiter community detections are performed
                in parallel. If False, only one worker executes the jobs.
    :return: igraph.VertexClustering based on community detection with highest
                modularity
    """
    # get edgelist and nodelist from input graph
    edgelist = [g.es[i].tuple for i in range(len(g.es))]
    nodelist = range(g.vcount())

    # run first community detection:
    loug = g.community_multilevel(return_levels=False)
    mod = g.modularity(loug)
    print('Modularity of the original order = ', mod)

    # create variables which are shared among all the parallel workers
    mod_res = mp.Value('d', mod)
    memship_res = mp.Array('i', loug.membership)

    # set number of processes run in parallel as nummber of CPUs (+-1 usually)
    if parallel:
        numprocs = mp.cpu_count() - 1
    else:
        numprocs = 1

    # processes which add elements to input and output queue
    p_inqueue = mp.Process(target=add2inqueue, args=(numiter - 1, numprocs))
    p_outqueue = mp.Process(target=outqueue2res,
                            args=(g, numprocs, mod_res, memship_res))
    # start worker processes
    ps = [mp.Process(target=comdet_worker, args=(nodelist, edgelist))
          for i in range(numprocs)]

    # start queues
    p_inqueue.start()
    p_outqueue.start()
    # start workers
    for p in ps:
        p.start()
        # print '......PID:', p.pid

    # end inqueue process once it is done
    p_inqueue.join()
    # end worker processes once they are done
    for p in ps:
        p.join()
    # end outqueue process once it is done
    p_outqueue.join()

    print 'Done.'
    return ig.VertexClustering(g, memship_res[:])


def add2inqueue(n, nprocs):
    """Add input parameters to queue which will be used by workers.

    :param n: number of tasks
    :type n: int
    :param nprocs: number of processes running in parallel
    :type nprocs: int
    """
    # here input are dummy variables to get the workers going
    for i in range(n):
        input_queue.put(i)
    # add 'poison pills' to queue to stop workers once all tasks have been done
    for i in range(nprocs):
        input_queue.put('STOP')


def comdet_worker(nlist, edlist):
    """Tasks for the parallel workers: perform Louvain community detection with
    a shuffled list of nodes and add modularity and membership list to output
    queue. The worker shuts down once he gets the poison pill "STOP" as input.

    :param nlist: list of nodes
    :param edlist: list of edges as tuples (i, j)
    """
    # take elements from input queue and elaborate job until the worker get
    # the 'poison pill' "STOP" as input
    for i in iter(input_queue.get, "STOP"):
        rifrullo = range(len(nlist))
        # shuffle list of nodes
        random.shuffle(rifrullo)
        # get new list of edges
        newedges = get_new_edgelist(edlist, rifrullo)

        # initialize graph and run community detection
        gaux = ig.Graph()
        gaux.add_vertices(nlist)
        gaux.add_edges(newedges)
        lougaux = gaux.community_multilevel(return_levels=False)
        gauxmod = gaux.modularity(lougaux)
        membaux = lougaux.membership
        mshiplistaux = [membaux[rifrullo[i]] for i in range(len(membaux))]

        # put modularity and membership list in the output queue
        output_queue.put((gauxmod, mshiplistaux))
    # add a 'poison pill' to the output queue
    output_queue.put('STOP')


def get_new_edgelist(edlist, rifrullo):
    """Create a new edge list based on the shuffled node lists.

    :param edlist: original edge list
    :type edlist: list of edges as tuples (i, j)
    :param rifrullo: shuffled node sequence
    :type rifrullo: list of integers
    """
    newedges = []
    for j in range(len(edlist)):
        newedges.append((rifrullo[edlist[j][0]], rifrullo[edlist[j][1]]))
    return newedges


def outqueue2res(g, nprocs, mod_res, memship_res):
    """Take output from outqueue and calculate the final results for the
    community detection.

    :param g: igraph.Graph object
    :param nprocs: number of processes running in parallel
    :type nprocs: int
    :param mod_res: highest modularity score
    :param memship_res: membership list corresponding to highest modularity
                            score
    """
    for work in range(nprocs):
        for val in iter(output_queue.get, "STOP"):
            pass
            modaux = val[0]
            if modaux > mod_res.value:
                mod_res.value = modaux
                loug = ig.VertexClustering(g, val[1])
                memship_res[:] = loug.membership
