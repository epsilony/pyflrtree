'''

@author: "epsilonyuan@gmail.com"
'''

import uuid
from bisect import bisect_left

class _Tree:
    __slots__ = ['key', 'left', 'right', 'down']
    
    def __init__(self, key, left=None, right=None, down=None):
        self.key = key
        self.left = left
        self.right = right
        self.down = down

class _FractionalCascadeNode:
    __slots__ = ['sorted_keys', 'left_fc', 'right_fc']
    
    def __init__(self, sorted_keys, left_fc, right_fc):
        self.sorted_keys = sorted_keys
        self.left_fc = left_fc
        self.right_fc = right_fc

def dict_compare_indes(main_dim, dim_num):
    dict_compare_indes = [main_dim]
    dict_compare_indes.extend(i for i in range(dim_num) if i != main_dim)
    return dict_compare_indes

class _DictComparable:
    
    @classmethod
    def setup_dict_compare(cls, main_dim, dim_num):
        cls.dict_compare_indes = dict_compare_indes(main_dim, dim_num)
    
    @property
    def main_dim(self):
        return self.dict_compare_indes[0] if self.dict_compare_indes is not None else None

    def __lt__(self, other):
        val = self.value
        oval = other.value
        for i in self.dict_compare_indes:
            v = val[i]
            o = oval[i]
            if v < o:
                return True
            if v > o:
                return False
        return self.index < other.index
    
    def __le__(self, other):
        val = self.value
        oval = other.value
        for i in self.dict_compare_indes:
            v = val[i]
            o = oval[i]
            if v < o:
                return True
            if v > o:
                return False
        return self.index <= other.index
    
    def __gt__(self, other):
        return not self.__le__(other)
    
    def __ge__(self, other):
        return not self.__lt__(other)
    
    def __ne__(self, other):
        val = self.value
        oval = other.value
        for i in self.dict_compare_indes:
            v = val[i]
            o = oval[i]
            if v != o:
                return True
        return self.index != other.index
    
    def __eq__(self, other):
        return not(self.__ne__(other))
    
    def __repr__(self):
        return "%s[%d:%d:%s]" % (str(self.__class__), self.index, self.main_dim, str(self.value))

class _AbstractKey(_DictComparable):
    
    def __init__(self, index=None):
        self.index = index
    
    @property
    def value(self):
        return self.data[self.index]

def _is_accept(key, lq, uq):
    lower = lq.value
    upper = uq.value
    value = key.value
    for i in range(len(value)):
        if value[i] > upper[i] or value[i] < lower[i]:
            return False
    return True

def _is_lower_than(key, uq):
    upper = uq.value
    value = key.value
    for i in range(len(value)):
        if value[i] > upper[i]:
            return False
    return True

class LRTree:
    def __init__(self, data, dim_num=None, leaf_size=1):
        """build a fractional cascading layered range tree
        
        arguments:
        data     -- a [n,d] list like input, d>=2 is the dimension number
        
        space complexity: O(n*log(n)**d)
        the time complexity of construction: O(n*log(n)**d)
        note: the data will not be copied, so once the data is changed the results will be wrong!
        """
        self.data = data
        if dim_num is None:
            dim_num = len(data[0])
        self.dim_num = dim_num
        if dim_num < 2:
            raise ValueError()
        if leaf_size < 1:
            raise ValueError()
        self.leaf_size = leaf_size
        self._build()
    
    def _build(self):
        self._gen_by_dim_sorted_classes()
        by_dim_sorted_keyss = self._gen_by_dim_sorted_keyss()
        self.root = self._build_tree(by_dim_sorted_keyss)
    
    def _gen_by_dim_sorted_classes(self):
        dim_num = self.dim_num
        self.by_dim_key_classes = [
                 type('_LRTree_%d_%s' % (i, uuid.uuid4().hex),
                      (_AbstractKey,),
                      {'__slots__':['index']}) 
                                 for i in range(dim_num)]
        for i in range(dim_num):
            by_dim_cls = self.by_dim_key_classes[i]
            by_dim_cls.setup_dict_compare(i, dim_num)
            by_dim_cls.data = self.data
    
    def _gen_by_dim_sorted_keyss(self):
        dim_num = self.dim_num
        by_dim_sorted_keyss = []
        for dim in range(dim_num):
            by_dim_cls = self.by_dim_key_classes[dim]
            by_dim_sorted_keys = [by_dim_cls(i) for i in range(len(self.data))]
            by_dim_sorted_keys.sort()
            by_dim_sorted_keyss.append(by_dim_sorted_keys)
        return by_dim_sorted_keyss

    def _build_tree(self, sorted_keyss):
        if (len(sorted_keyss[0]) <= self.leaf_size):
            return self._build_leaf(sorted_keyss)
        
        if len(sorted_keyss) > 2:
            return self._build_associated_tree(sorted_keyss)
        else:
            return self._build_fractional_cascaded_tree(sorted_keyss)
    
    def _build_associated_tree(self, sorted_keyss):
        keys = sorted_keyss[0]
        mid_index = (len(keys) - 1) // 2
        mid = keys[mid_index]
        associated = self._build_tree(sorted_keyss[1:])
        left_sorted_keyss = [keys[:mid_index + 1]]
        right_sorted_keyss = [keys[mid_index + 1:]]
        for ks in sorted_keyss[1:]:
            left_keys = []
            right_keys = []
            for key in ks:
                if mid < key:
                    right_keys.append(key)
                else:
                    left_keys.append(key)
            left_sorted_keyss.append(left_keys)
            right_sorted_keyss.append(right_keys)
        
        left = self._build_tree(left_sorted_keyss)
        right = self._build_tree(right_sorted_keyss)
        return _Tree(mid, left, right, associated)
    
    def _build_fractional_cascaded_tree(self, sorted_keyss):
        keys = sorted_keyss[0]
        mid = keys[len(keys) // 2]
        down_keys = sorted_keyss[1]
        
        left_fc = []
        right_fc = []
        
        left_index = 0
        right_index = 0
        
        left_down_keys = []
        right_down_keys = []
        

        for dk in down_keys:
            left_fc.append(left_index)
            right_fc.append(right_index)
            if mid < dk:
                right_down_keys.append(dk)
                right_index += 1
            else:
                left_down_keys.append(dk)
                left_index += 1
        
        left_size = (len(keys) + 1) // 2
        left_sorted_keys = [keys[:left_size], left_down_keys]
        right_sorted_keys = [keys[left_size:], right_down_keys]
        
        left = self._build_tree(left_sorted_keys)
        right = self._build_tree(right_sorted_keys)
        
        return _Tree(mid, left, right, _FractionalCascadeNode(down_keys, left_fc, right_fc))
        
    def _build_leaf(self, sorted_keys):
        return sorted_keys[-1]
    
    def query(self, lower, upper):
        """query a list of all i where data[i][j]<=upper[j] and data[i][j]>=lower[j] (0<j<d)
        
        the query time complexity is O(log(n)**d+k), where k is the length of result list
        """
        
        lq = _DictComparable()
        lq.value = lower
        lq.index = -1
        uq = _DictComparable()
        uq.value = upper
        uq.index = len(self.data)
        
        result = []
        
        self._query(self.root, lq, uq, result)
        
        return result
    
    def _query(self, tree, lq, uq, result):   
        split_node = self._find_split(tree, lq, uq)
        
        if not isinstance(split_node, _Tree):
            self._query_leaf(split_node, lq, uq, result)
            return 
        
        self._query_split_left(split_node.left, lq, uq, result)
        self._query_split_right(split_node.right, lq, uq, result)
        
    def _find_split(self, tree, lq, uq):
        node = tree
        while True:
            if not isinstance(node, _Tree):
                return node
            key = node.key
            if key <= lq:
                node = node.right
            elif key > uq:
                node = node.left
            else:
                return node
    
    def _query_leaf(self, leaf, lq, uq, result):
        result.extend(key.index for key in leaf if _is_accept(key, lq, uq))
    
    def _query_split_left(self, tree, lq, uq, result):
        node = tree
        while True:
            if not isinstance(node, _Tree):
                self._query_leaf(node, lq, uq, result)
                return
            if node.key <= lq:
                node = node.right
            else:
                if isinstance(node.down, _Tree):
                    if isinstance(node.right, _Tree):
                        self._query(node.right.down, lq, uq, result)
                    else:
                        self._query_leaf(node.right, lq, uq, result)
                elif isinstance(node.down, _FractionalCascadeNode):
                    self._query_right_fc(node, lq, uq, result)
                else:
                    self._query_leaf(node.down, lq, uq, result)
                node = node.left
    
    def _query_split_right(self, tree, lq, uq, result):
        node = tree
        while True:
            if not isinstance(node, _Tree):
                self._query_leaf(node, lq, uq, result)
                return
            if node.key > uq:
                node = node.left
            else:
                if isinstance(node.down, _Tree):
                    if isinstance(node.left, _Tree):
                        self._query(node.left.down, lq, uq, result)
                    else:
                        self._query_leaf(node.left, lq, uq, result)
                elif isinstance(node.down, _FractionalCascadeNode):
                    self._query_left_fc(node, lq, uq, result)
                else:
                    self._query_leaf(node.down, lq, uq, result)
                node = node.right
    
    def _query_right_fc(self, tree, lq, uq, result):
        fc = tree.down
        index = bisect_left(fc.sorted_keys, lq)
        if index >= len(fc.right_fc):
            return
        right_index = fc.right_fc[index]
        right = tree.right
        if isinstance(right, _Tree):
            right_keys = right.down.sorted_keys
        else:
            right_keys = right
        result.extend(right_keys[i].index for i in range(right_index, len(right_keys)) if _is_lower_than(right_keys[i], uq))
    
    def _query_left_fc(self, tree, lq, uq, result):
        fc = tree.down
        index = bisect_left(fc.sorted_keys, lq)
        if index >= len(fc.left_fc):
            return
        left_index = fc.left_fc[index]
        left = tree.left
        if isinstance(left, _Tree):
            left_keys = left.down.sorted_keys
        else:
            left_keys = left
        
        result.extend(left_keys[i].index for i in range(left_index, len(left_keys)) if _is_lower_than(left_keys[i], uq))


