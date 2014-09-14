import random
from flrtree.fltree import LRTree
from nose.tools import assert_list_equal

class RawSearcher:
    
    def __init__(self, data):
        self.data = data
    
    def query(self, lower, upper):
        result = []
        index = 0
        for d in self.data:
            add = True
            for d, l, u in zip(d, lower, upper):
                if d > u or d < l:
                    add = False
                    break
            if add:
                result.append(index)
            index += 1
        return result

def mesh_grid_3d(xs, ys, zs):
    result = [(x, y, z) for x in xs for y in ys for z in zs]
    return result

def random_coord(dim_num, coord_num):
    result = [[random.random() for _d in range(dim_num)] for _i in range(coord_num) ]
    return result

def random_range(dim_num):
    xs=[random.random()for _i in range(dim_num*2)]
    xs.sort()
    lower=xs[:dim_num]
    upper=xs[dim_num:]
    return lower,upper

def test_by_mesh_grid_3d():
    dim_num = 3
    data_per_dim=10
    xs=[i/data_per_dim for i in range(data_per_dim)]
    data = mesh_grid_3d(xs,xs,xs)
    random.shuffle(data)
    
    sample_num=1000
    
    raw=RawSearcher(data)
    lrtree=LRTree(data)
    
    for _i in range(sample_num):  

        
        lower,upper=random_range(dim_num)
        exp=raw.query(lower, upper)
        act=lrtree.query(lower, upper)
        act.sort()
        
        assert_list_equal(exp,act)
        
def test_by_random_3d():
    dim_num=3
    data_len=1000
    sample_num=10
    outer_loop_num=100
    
    for _o in range(outer_loop_num):
        data=random_coord(dim_num, data_len)
        
        raw=RawSearcher(data)
        lrtree=LRTree(data)
        
        for _i in range(sample_num):  
    
            
            lower,upper=random_range(dim_num)
            exp=raw.query(lower, upper)
            act=lrtree.query(lower, upper)
            act.sort()
            
            assert_list_equal(exp,act)