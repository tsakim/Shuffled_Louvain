# Louvain Community Detection with shuffled node sequence 

## About
Louvain community detection with shuffled node sequence are performed and the community structure with the highest modularity score are returned. The igraph.community_multilevel algorithm is used for the community detection.

## Dependencies
[multiprocessing](https://docs.python.org/2/library/multiprocessing.html#module-multiprocessing)
[igraph](http://igraph.org/python/)
[random](https://docs.python.org/2/library/random.html)

## Usage
Be `G` the igraph.Graph object on which we want to perform a community detection and be `n` the number of iteration we want to run in order to find the maximal modularity.

Import modules:
```
$ import shuffled_louvain as shulou                                     
```                                                                                 
Run n-times the community detection:                                        
```
$ vc = shulou.shuffled_comdet(G, n)                                     
```                                                                                 
The membership list of the detected communities can be accessed with 
```
$ vc.membership                                                         
```
