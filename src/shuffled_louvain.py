# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 2016

Module:
    shuffled_louvain - Louvain community detection with shuffled node sequence

Authors:
    Fabio Saracco, Mika Straka

Description:
    Louvain community detection with shuffled node sequence are performed and
    the community structure with the highest modularity score is returned.
    The igraph.community_multilevel algorithm is used for the community
    detection.

Usage:
    Given an igraph.Graph object ``G``, we want to run ``n`` community
    detections using different permutations of the node sequence of the graph
    in order to find the vertex clustering which returns the maximum
    modularity.  
    
    To import the module, use::

        >>> from src import shuffled_louvain as shulou

    and run ``n``-times the community detection:

        >>> vc = shulou.shuffled_comdet(G, n)

    The membership list of the detected communities can be accessed with::

        >>> vc.membership

.. note::
    
    **Parallel computation**
    Since the community detection can be computationally demanding, the module
    uses the Python `multiprocessing
    <https://docs.python.org/2/library/multiprocessing.html>`_ package to
    execute the computation in parallel.  The number of parallel processes
    depends on the number of CPUs of the work station ( see variable
    ``numprocs`` in method :func:`shuffled_comdet`).

    If the calculation should **not**be performed in parallel, use::

        >>> shulou.shuffled_comdet(G, n, parallel=False)
"""

import multiprocessing as mp
import igraph as ig
import random

# initialize global input and output queues
input_queue = mp.Queue()
output_queue = mp.Queue()


def shuffled_comdet(g, numiter, parallel=True):
    """Run Louvain community detections with shuffled node sequence.

    Perform ``numiter`` Louvain community detections of the input graph ``g``
    and return the VertexClustering object with the highest modularity score.
    The community detections are performed on randomly shuffled node sequence
    and can be run in parallel. The number of processes is determined by the
    number of CPU of the work station (see below).

    :param g: graph for community detection
    :type g: igraph.Graph
    :param numiter: number of reshuffled community detections to run
    :type numiter: int
    :param parallel: if ``True``, the numiter community detections are performed
                in parallel, otherwise in sequence
    :type parallel: bool
    :returns: VertexClustering with highest modularity score
    :rtype: igraph.VertexClustering     
    """
    # get edgelist and nodelist from input graph
    edgelist = [g.es[i].tuple for i in range(len(g.es))]
    nodelist = range(g.vcount())

    # run first community detection:
    loug = g.community_multilevel(return_levels=False)
    mod = g.modularity(loug)
    # print('Modularity of the original order = ', mod)

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

    # create worker processes
    ps = [mp.Process(target=comdet_worker, args=(nodelist, edgelist))
          for i in range(numprocs)]

    # start queues
    p_inqueue.start()
    p_outqueue.start()

    # start workers
    for p in ps:
        p.start()

    # end processes once they are done
    p_inqueue.join()
    for p in ps:
        p.join()
    p_outqueue.join()

    print 'Done.'
    return ig.VertexClustering(g, memship_res[:])


def add2inqueue(n, nprocs):
    """Add input parameters to queue to be processed by workers.

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
