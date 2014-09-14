pyflrtree
=========

Pure python implementation of factional cascading layered range tree

  - only depends on python standard libraries when using (needs setuptools for installing, of course)
  - `O(n*log(n)**d)` space complexity
  - `O(n*log(n)**d)` constructing time complexity
  - `O(log(n)**(d-1)+k)` querying time complexity

Only supports Python 3 now.

All comparable python objects are OK.

When limit to numpy 3d array with `len(x)>1000`, this query implementation is commonly faster than `scipy.spatial.KDTree`.(but is still slower than `scipy.spatial.cKDTree` due to Python intrinsic speed)

The construction time is much longer than kd-trees so this layered range tree is suitable for a large data set with an event larger number of query times. 

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

run some blackbox tests:
```
import flrtree
flrtree.test()
```
