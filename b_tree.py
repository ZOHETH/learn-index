import pandas as pd
import math
import time
import random


class BTreeNode:
    def __init__(self, number_of_key, is_leaf, items=None, children=None, parent=None):
        # self.degree = degree
        self.isLeaf = is_leaf
        self.numberOfKeys = number_of_key
        # self.index = index

        self.parent = parent
        if items is None:
            self.items = [None] * number_of_key
        else:
            self.items = items
        if len(self.items) != number_of_key:
            raise IndexError("Number of key of node ERROR")
            # print("error: number of key of node!!")
        if children is None:
            self.children = [None] * (number_of_key + 1)
        else:
            self.children = children  # children比items多一
        if len(self.children) != number_of_key + 1:
            raise IndexError("Number of children of node ERROR")
            # print("error: number of children of node!!")
        # if items is not None:
        #     self.items = items
        #     #self.items += [None] * (degree * 2 - len(items))
        # else:
        #     self.items = [None] * (degree * 2 - 1)
        # if children is not None:
        #     self.children = children
        #     self.children = [None] * (degree * 2 - number_of_key + 1)
        # else:
        #     self.children = [None] * degree * 2

    # def set_index(self, index):
    #     self.index = index
    #
    # def get_index(self):
    #     return self.index

    def search(self, btree, item):
        i = 0
        while i < self.numberOfKeys and item > self.items[i]:
            i += 1
        if i < self.numberOfKeys and item == self.items[i]:
            return {'found': True, 'node': self, 'index': i}
        # if self.children[i] is None:
        if self.isLeaf:
            return {'found': False, 'node': self, 'index': i}
        btree.set_hot(i)
        return self.children[i].search(btree, item)


class BTree:
    def __init__(self, order, root=None):
        # self.nodes
        self.order = order
        self.rootNode = root
        # self.rootIndex
        self.hot = None

    def build(self, keys, values):
        for i in range(keys):
            self.insert(Item(keys[i], values[i]))

    def insert(self, item):
        print(item.k)
        try:
            if self.rootNode is None:
                new_root = BTreeNode(number_of_key=1, is_leaf=True, items=[item])
                self.rootNode = new_root
                return
            search_result = self.search(item)
            # print(search_result)
            if search_result['found']:
                return
            self.insert_direct(item, search_result['node'])
            search_result['node'].children.append(None)
            if search_result['node'].numberOfKeys == self.order:
                self.split(search_result['node'].parent, search_result['node'])
                # hot的语义更改为搜索到的节点是父亲节点的第几个孩子
                # self.split(self.hot, search_result['node'])
        except IndexError as e:
            print(e.args)
            exit()

    def split(self, node_p, node_c):
        s = math.floor(self.order / 2)
        m = self.order
        if node_p is None:
            print("root")
            new_root = BTreeNode(number_of_key=0, is_leaf=False, children=[node_c])
            node_c.parent = new_root
            self.rootNode = new_root
            node_p = new_root
        index = self.insert_direct(node_c.items[s], node_p)
        node_c.numberOfKeys = s
        new_node = BTreeNode(number_of_key=m - s - 1, is_leaf=node_c.isLeaf,
                             items=node_c.items[s + 1:m], children=node_c.children[s + 1:m + 1], parent=node_p)
        node_p.children.insert(index + 1, new_node)
        node_c.items = node_c.items[0:s]
        node_c.children = node_c.children[0:s + 1]

        if node_p.numberOfKeys == m:
            self.split(node_p.parent, node_p)

    def insert_direct(self, item, node):
        i = node.numberOfKeys
        node.items.append(None)
        while i > 0 and node.items[i - 1] > item:
            node.items[i] = node.items[i - 1]
            i -= 1
        node.items[i] = item
        node.numberOfKeys += 1
        return i

    def delete(self, item):
        search_result = self.search(item)
        if not search_result['found']:
            return
        node = search_result['node']
        r = search_result['index']
        if not node.isLeaf:
            node = node.children[r + 1]
            self.hot = r + 1
        while not node.isLeaf:
            node = node.children[0]
            self.hot = 0
        search_result['node'].items[r] = node.items[0]
        del (node.items[0])
        node.children.pop()
        node.numberOfKeys -= 1
        if node.numberOfKeys == math.ceil(self.order / 2) - 2:
            self.rotate_and_merge(node)
            # 只实现了一层处理下溢

    def rotate_and_merge(self, node):
        if self.hot is None:
            return
        parent = node.parent
        if self.hot > 0 and parent.children[self.hot - 1].numberOfKeys >= (math.ceil(self.order / 2)):
            brother = parent.children[self.hot - 1]
            node.items.insert(0,parent.items[self.hot - 1])
            parent.items[self.hot - 1] = brother.items.pop()
            brother.numberOfKeys -= 1
            brother.children.pop()
        elif self.hot < parent.numberOfKeys + 1 and parent.children[self.hot + 1].numberOfKeys >= (
        math.ceil(self.order / 2)):
            brother = parent.children[self.hot + 1]
            node.items.insert(node.numberOfKeys,parent.items[self.hot])
            parent.items[self.hot] = brother.items.pop(0)
            brother.numberOfKeys -= 1
            brother.children.pop()
        elif self.hot > 0:
            brother = parent.children[self.hot - 1]
            brother.items=brother.items+[parent.items[self.hot-1]]+node.items
            del(parent.items[self.hot-1])
            del(parent.children[self.hot])
            brother.numberOfKeys=self.order-1
            parent.numberOfKeys-=1
        elif self.hot<parent.numberOfKeys+1:
            brother = parent.children[self.hot+1]
            brother.items=node.items+[parent.items[self.hot]]+brother.items
            del(parent.items[self.hot])
            del(parent.children[self.hot])
            brother.numberOfKeys=self.order-1
            parent.numberOfKeys-=1



    def search(self, item):
        self.set_hot(None)
        return self.rootNode.search(self, item)

    def set_hot(self, node):
        self.hot = node


# Value in Node
class Item:
    def __init__(self, k, v):
        self.k = k
        self.v = v

    def __gt__(self, other):
        if self.k > other.k:
            return True
        else:
            return False

    def __ge__(self, other):
        if self.k >= other.k:
            return True
        else:
            return False

    def __eq__(self, other):
        if self.k == other.k:
            return True
        else:
            return False

    def __le__(self, other):
        if self.k <= other.k:
            return True
        else:
            return False

    def __lt__(self, other):
        if self.k < other.k:
            return True
        else:
            return False


def b_tree_main():
    path = "test.csv"
    data = pd.read_csv(path)
    b = BTree(100)
    for i in range(data.shape[0]):
        b.insert(Item(data.iloc[i, 0], data.iloc[i, 1]))

    start = time.perf_counter()
    t = 100000
    while t > 0:
        key = random.randint(0, 200000)
        b.search(Item(key, 0.12))
        t -= 1
    # b.delete(73500)
    # if b.search(Item(73500, 0.12))['found']:
    #     print("hahahahsfoh")
    end = time.perf_counter()
    print(end - start)


if __name__ == '__main__':
    b_tree_main()
