# Louvain Community Detection with shuffled node sequence 

## About
The Louvain community detection is performed for the same graph with shuffled
node sequence and the community structure with the highest modularity score is
returned. The `igraph.community_multilevel` algorithm is used for the community
detection.

## Authors
Fabio Saracco, Mika J. Straka

## Version and Documentation
The newest version and the documentation can be found on
[https://github.com/tsakim/Shuffled_Louvain](https://github.com/tsakim/Shuffled_Louvain).

## Dependencies
The module has been written in *Python 2.7* and uses the following packages:

* [multiprocessing](https://docs.python.org/2/library/multiprocessing.html#module-multiprocessing)
* [igraph](http://igraph.org/python/)
* [random](https://docs.python.org/2/library/random.html)

## Usage
Given an igraph.Graph object ``G``, we want to run ``n`` community detections
in order to find the vertex clustering which returns the maximum modularity.
Each iteration is run on a different permutations of the node sequence of the
graph.

To import the module, use::
```python
>>> from src import suffled_louvain as shulou
```
and run ``n``-times the community detection:
```python
>>> vc = shulou.shuffled_comdet(G, n)
```
The membership list of the detected communities can be accessed with::
```python
>>> vc.membership
```

## Parallel computation
Since the community detection can be computationally demanding, the module uses
the Python
[multiprocessing](https://docs.python.org/2/library/multiprocessing.html)
package to execute the computation in parallel.  The number of parallel
processes depends on the number of CPUs of the work station ( see variable
`numprocs` in method `shuffled_comdet`).

If the calculation should **not** be performed in parallel, use::
```python
>>> shulou.shuffled_comdet(G, n, parallel=False)
```

---
Copyright (c) 2016-2017 Fabio Saracco, Mika J. Straka
