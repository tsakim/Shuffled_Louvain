# Louvain Community Detection with shuffled node sequence 

## About
The Louvain community detection is performed for the same graph with shuffled
node sequence and the community structure with the highest modularity score is
returned. The `igraph.community_multilevel` algorithm is used for the community
detection.

## Authors
Fabio Saracco, Mika Straka

### This version
The newest version can be found on
[https://github.com/tsakim/Shuffled_Louvain](https://github.com/tsakim/Shuffled_Louvain).

## Dependencies
* [multiprocessing](https://docs.python.org/2/library/multiprocessing.html#module-multiprocessing)
* [igraph](http://igraph.org/python/)
* [random](https://docs.python.org/2/library/random.html)

## Usage
Be `G` the igraph.Graph object on which we want to perform a community
detection and be `n` the number of iteration we want to run in order to find
the maximal modularity.

Import the module 
```python
import shuffled_louvain as shulou                                     
```                                                                                 
and run the community detection `n` times:                                        
```python
vc = shulou.shuffled_comdet(G, n)                                     
```                                                                                 
The membership list of the detected communities can be accessed with 
```python
vc.membership                                                         
```

## Parallel computation
The module uses the Python multiprocessing to calculate the community
structures for shuffled node sequences in parallel. The number of parallel
processes depends on the number of CPUs of the work station, see variable
`numprocs` in method `shuffled_comdet`.
If the calculation should **not** be performed in parallel, use                 
```python
shulou.shuffled_comdet(G, n, parallel=False)
```

---
Copyright (C) 2016 F. Saracco/M. Straka
