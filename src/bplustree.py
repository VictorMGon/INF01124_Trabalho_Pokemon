#Adapted from: https://gist.github.com/savarin/69acd246302567395f65ad6b97ee503d
#Original code by Savarin
#New changes:
#-bug fixes
#-on disk operation
#-next and previous node(linked list)


from blockmanager import *
from filemanager import *
"""Simple implementation of a B+ tree, a self-balancing tree data structure that (1) maintains sort
data order and (2) allows insertions and access in logarithmic time.
"""

class BNode(object):
    """Base node object.

    Each node stores keys and values. Keys are not unique to each value, and as such values are
    stored as a list under each key.

    Attributes:
        order (int): The maximum number of keys each node can hold.
    """
    def __init__(self, order, bmgr=None):
        """Child nodes can be converted into parent nodes by setting self.leaf = False. Parent nodes
        simply act as a medium to traverse the tree."""
        self.order = order
        self.keys = []
        self.values = []
        self.leaf = True

        self.next = None
        self.previous = None
        self.block_id = 0
        self.bm = bmgr

        if bmgr:
            self.block_id = self.bm.generateID()

    def add(self, key, value):
        """Adds a key-value pair to the node."""
        # If the node is empty, simply insert the key-value pair.
        if not self.keys:
            self.keys.append(key)
            self.values.append([value])
            return None

        for i, item in enumerate(self.keys):
            # If new key matches existing key, add to list of values.
            if key == item:
                self.values[i].append(value)
                break
            # If new key is smaller than existing key, insert new key to the left of existing key.
            elif key < item:
                self.keys = self.keys[:i] + [key] + self.keys[i:]
                self.values = self.values[:i] + [[value]] + self.values[i:]
                break

            # If new key is larger than all existing keys, insert new key to the right of all
            # existing keys.
            elif i + 1 == len(self.keys):
                self.keys.append(key)
                self.values.append([value])
                break
        if self.bm:
            self.bm.write_node(self)

    def split(self):
        """Splits the node into two and stores them as child nodes."""
        left = BNode(self.order,self.bm)
        right = BNode(self.order,self.bm)

        mid = self.order // 2

        left.keys = self.keys[:mid]
        left.values = self.values[:mid]

        right.keys = self.keys[mid:]
        right.values = self.values[mid:]

        if self.leaf:
            left.previous = self.previous
            right.next = self.next

        if self.bm:
            left.next = right.block_id
            right.previous = left.block_id
        else:
            left.next = right
            right.previous = left

        # When the node is split, set the parent key to the left-most key of the right child node.
        self.keys = [right.keys[0]]
        self.values = [left, right]
        self.leaf = False
        self.next = None
        self.previous = None
        if self.bm:
            self.values = [left.block_id,right.block_id]
            self.bm.write_node(left)
            self.bm.write_node(right)
            self.bm.write_node(self)

    def is_full(self):
        """Returns True if the node is full."""
        return len(self.keys) == self.order

    def show(self, counter=0):
        """Prints the keys at each level."""
        print(counter, str(self.keys))

        # Recursively print the key of child nodes (if these exist).
        if not self.leaf:
            for item in self.values:
                if self.bm:
                    node = self.bm.read_node(item)
                    node.show(counter + 1)
                else:
                    item.show(counter + 1)

class BPlusTree(object):
    """B+ tree object, consisting of nodes.

    Nodes will automatically be split into two once it is full. When a split occurs, a key will
    'float' upwards and be inserted into the parent node to act as a pivot.

    Attributes:
        order (int): The maximum number of keys each node can hold.
    """
    def __init__(self, order=8, bmgr=None):
        self.root = BNode(order,bmgr)
        self.bm = bmgr
        if bmgr:
            bmgr.setOrder(order)
            bmgr.write_node(self.root,delete_overflow=False)

    def _find(self, node, key):
        """ For a given node and key, returns the index where the key should be inserted and the
        list of values at that index."""
        for i, item in enumerate(node.keys):
            if key < item:
                if self.bm:
                    return self.bm.read_node(node.values[i]), i
                return node.values[i], i
        if self.bm:
            return self.bm.read_node(node.values[i + 1]), i + 1
        return node.values[i + 1], i + 1

    def _merge(self, parent, child, index):
        """For a parent and child node, extract a pivot from the child to be inserted into the keys
        of the parent. Insert the values from the child into the values of the parent.
        """
        parent.values.pop(index)
        pivot = child.keys[0]

        for i, item in enumerate(parent.keys):
            if pivot < item:
                parent.keys = parent.keys[:i] + [pivot] + parent.keys[i:]
                parent.values = parent.values[:i] + child.values + parent.values[i:]
                break

            elif i + 1 == len(parent.keys):
                parent.keys += [pivot]
                parent.values += child.values
                break
        if self.bm:
            self.bm.delete_node(child)
            self.bm.write_node(parent)

    def insert(self, key, value):
        """Inserts a key-value pair after traversing to a leaf node. If the leaf node is full, split
        the leaf node into two.
        """
        parent = None
        child = self.root
        # Traverse tree until leaf node is reached.

        while not child.leaf:
            parent = child
            child, index = self._find(child, key)
        child.add(key, value)
        # If the leaf node is full, split the leaf node into two.
        if child.is_full():
            child.split()

            # Once a leaf node is split, it consists of a internal node and two leaf nodes. These
            # need to be re-inserted back into the tree.
            if parent and not parent.is_full():
                self._merge(parent, child, index)

    def retrieve(self, key):
        """Returns a value for a given key, and None if the key does not exist."""
        child = self.root

        counter = 0
        #print('layer ', counter)
        while not child.leaf:
            counter += 1
            child, index = self._find(child, key)
            #print('layer ', counter)

        for i, item in enumerate(child.keys):
            if key <= item:
                return child.values[i]
                #return child

        return child.values[i]

    def show(self):
        """Prints the keys at each level."""
        self.root.show()

def test_node():
    print('Initializing node...')
    node = BNode(order=4)

    print('\nInserting key a...')
    node.add('a', 'alpha')
    print('Is node full?', node.is_full())
    node.show()

    print('\nInserting keys b, c, d...')
    node.add('b', 'bravo')
    node.add('c', 'charlie')
    node.add('d', 'delta')
    print('Is node full?', node.is_full())
    node.show()

    print('\nSplitting node...')
    node.split()
    node.show()

def test_bplustree1():
    fm = AbstractFileManager()
    fm.createFile('testfile2','test')
    bm = BPlusBlockManager(fm.getFile('testfile2'),4096)
    print('Initializing B+ tree...')
    bplustree = BPlusTree(order=4, bmgr = bm)

    print('root block_id: {}'.format(bplustree.root.block_id))

    print(len(bplustree.root.keys),"|",bplustree.root.keys)
    print(len(bplustree.root.keys),"|",bplustree.root.values)

    print('\nB+ tree with 1 item...')
    bplustree.insert(30, 100)
    bplustree.show()

    print(len(bplustree.root.keys),"|",bplustree.root.keys)
    print(len(bplustree.root.keys),"|",bplustree.root.values)

    print('\nB+ tree with 2 items...')
    bplustree.insert(50, 23)
    bplustree.show()

    print(len(bplustree.root.keys),"|",bplustree.root.keys)
    print(len(bplustree.root.keys),"|",bplustree.root.values)

    print('\nB+ tree with 3 items...')
    bplustree.insert(50, 97)
    bplustree.show()

    print(len(bplustree.root.keys),"|",bplustree.root.keys)
    print(len(bplustree.root.keys),"|",bplustree.root.values)


def test_bplustree2():
    fm = AbstractFileManager()
    fm.createFile('testfile2','test')
    bm = BPlusBlockManager(fm.getFile('testfile2'),4096)
    print('Initializing B+ tree...')
    bplustree = BPlusTree(order=4, bmgr = bm)

    print('\nB+ tree with 1 item...')
    bplustree.insert(30, 100)
    bplustree.show()

    print('\nB+ tree with 2 items...')
    bplustree.insert(50, 23)
    bplustree.show()

    print('\nB+ tree with 3 items...')
    bplustree.insert(50, 97)
    bplustree.show()

    print('\nB+ tree with 4 items...')
    bplustree.insert(10, 60)
    bplustree.show()

    print('\nB+ tree with 5 items...')
    bplustree.insert(40, 65)
    bplustree.show()

    print('root block_id: {}'.format(bplustree.root.block_id))


def test_bplustree3():
    fm = AbstractFileManager()
    fm.createFile('testfile2','test')
    bm = BPlusBlockManager(fm.getFile('testfile2'),4096)
    print('Initializing B+ tree...')
    bplustree = BPlusTree(order=4, bmgr = bm)

    print('\nB+ tree with 1 item...')
    bplustree.insert(30, 100)
    bplustree.show()

    print('\nB+ tree with 2 items...')
    bplustree.insert(50, 23)
    bplustree.show()

    print('\nB+ tree with 3 items...')
    bplustree.insert(50, 97)
    bplustree.show()

    print('\nB+ tree with 4 items...')
    bplustree.insert(10, 60)
    bplustree.show()

    print('\nB+ tree with 5 items...')
    bplustree.insert(40, 65)
    bplustree.show()

    print('\nB+ tree with 6 items...')
    bplustree.insert(15, 31)
    bplustree.show()

    print('\nB+ tree with 7 items...')
    bplustree.insert(43, 43)
    bplustree.show()

    print('\nRetrieving values with key 30...')
    print(bplustree.retrieve(30))

    print('\nRetrieving values with key 50...')
    print(bplustree.retrieve(50))

    print('\nRetrieving values with key 10...')
    print(bplustree.retrieve(10))

    print('\nRetrieving values with key 40...')
    print(bplustree.retrieve(40))

    print('\nRetrieving values with key 15...')
    print(bplustree.retrieve(15))

    print('\nRetrieving values with key 43...')
    print(bplustree.retrieve(43))

    print('root block_id: {}'.format(bplustree.root.block_id))

if __name__ == '__main__':
    #test_node()
    #test_bplustree1()
    #test_bplustree2()
    test_bplustree3()
