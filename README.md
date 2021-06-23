# DEMON - Overlapping Community Discovery.

[![Test and Coverage (Ubuntu)](https://github.com/GiulioRossetti/DEMON/actions/workflows/test_ubuntu.yml/badge.svg)](https://github.com/GiulioRossetti/DEMON/actions/workflows/test_ubuntu.yml)
[![Coverage Status](https://coveralls.io/repos/github/GiulioRossetti/DEMON/badge.svg?branch=master)](https://coveralls.io/github/GiulioRossetti/DEMON?branch=master)
[![pyversions](https://img.shields.io/pypi/pyversions/demon.svg)](https://badge.fury.io/py/DEMON)
[![PyPI version](https://badge.fury.io/py/demon.svg)](https://badge.fury.io/py/DEMON)
[![Updates](https://pyup.io/repos/github/GiulioRossetti/DEMON/shield.svg)](https://pyup.io/repos/github/GiulioRossetti/DEMON/)
[![DOI](https://zenodo.org/badge/53486170.svg)](https://zenodo.org/badge/latestdoi/53486170)
[![PyPI download month](https://img.shields.io/pypi/dm/demon.svg?color=blue&style=plastic)](https://pypi.python.org/pypi/demon/)

![DEMON logo](http://www.giuliorossetti.net/about/wp-content/uploads/2013/07/Demon-300x233.png)


Community discovery in complex networks is an interesting problem with a number of applications, especially in the knowledge extraction task in social and information networks. However, many large networks often lack a particular community organization at a global level. In these cases, traditional graph partitioning algorithms fail to let the latent knowledge embedded in modular structure emerge, because they impose a top-down global view of a network. We propose here a simple local-first approach to community discovery, able to unveil the modular organization of real complex networks. This is achieved by democratically letting each node vote for the communities it sees surrounding it in its limited view of the global system, i.e. its ego neighborhood, using a label propagation algorithm; finally, the local communities are merged into a global collection. 

**Note:** Demon has been integrated within [CDlib](http://cdlib.readthedocs.io) a python package dedicated to community detection algorithms, check it out!

## Citation
If you use our algorithm please cite the following works:

>Coscia, Michele; Rossetti, Giulio; Giannotti, Fosca; Pedreschi, Dino
> ["Uncovering Hierarchical and Overlapping Communities with a Local-First Approach"](http://dl.acm.org/citation.cfm?id=2629511)
>ACM Transactions on Knowledge Discovery from Data (TKDD), 9 (1), 2014. 

>Coscia, Michele; Rossetti, Giulio; Giannotti, Fosca; Pedreschi, Dino
> ["DEMON: a Local-First Discovery Method for Overlapping Communities"](http://dl.acm.org/citation.cfm?id=2339630)
>SIGKDD international conference on knowledge discovery and data mining, pp. 615-623, IEEE ACM, 2012, ISBN: 978-1-4503-1462-6.

## Installation


In order to install the package just download (or clone) the current project and copy the demon folder in the root of your application.

Alternatively use pip:
```bash
pip install demon
```

or conda
```bash
conda install -c giuliorossetti demon
```

Demon is written in python and requires the following package to run:
- networkx
- tqdm

## Implementation details



# Execution

The algorithm can be used as standalone program as well as integrated in python scripts.

## Standalone

```bash

python demon filename epsilon -c min_com_size
```

where:
* *filename*: edgelist filename
* *epsilon*: merging threshold in [0,1]
* *min_community_size*: minimum size for communities (default 3 - optional)

Demon results will be saved on a text file.

### Input file specs 
Edgelist format: tab separated edgelist (nodes represented with integer ids).

Row example:
```
node_id0    node_id1
```

## As python library

Demon can be executed specifying as input: 

1. an edgelist file

```python
import demon as d
dm = d.Demon(network_filename="filename.tsc", epsilon=0.25, min_community_size=3, file_output="communities.txt")
dm.execute()

```

2. a *networkx* Graph object

```python
import networkx as nx
import demon as d

g = nx.karate_club_graph()
dm = d.Demon(graph=g, epsilon=0.25, min_community_size=3)
coms = dm.execute()

```

The parameter *file_output*, if specified, allows to write on file the algorithm results.
Conversely, the communities will be returned to the main program as a list of node ids tuple, e.g.,

```python
[(0,1,2),(3,4),(5,6,7)]
```
