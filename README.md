pyflrtree
=========

Pure python implementation of factional cascading layered range tree

  - only depends on python standard libraries
  - `O(n*log(n)**d)` space complexity
  - `O(n*log(n)**d)` constructing time complexity
  - `O(log(n)**(d-1)+k)` querying time complexity

checkout and install:
```bash
git clone https://github.com/epsilony/pyflrtree.git
pip install -e pyflrtree
```

query multi-dimensional data:
```python
from flrtree import LRTree

...
tree=LRTree(data)

indes=tree.query(lower,upper)
```
