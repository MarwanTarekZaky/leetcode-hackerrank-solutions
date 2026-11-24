## Trees

### Tree: Preorder Traversal

**Problem.** Print the preorder traversal (node, left, right) of a binary search tree built by inserting the given values.

**Idea.** Preorder visits a node before its subtrees. With an explicit stack, push the right child before the left, so the left child is popped (visited) first. This also avoids Python's recursion limit on deep, skewed trees.

**Steps.**
1. Build the BST with the HackerRank `create` routine.
2. Stack traversal: pop, print, push right, push left.

```python
class Node:
    def __init__(self, info):
        self.info = info
        self.left = None
        self.right = None


class BinarySearchTree:
    def __init__(self):
        self.root = None

    def create(self, val):
        if self.root is None:
            self.root = Node(val)
            return
        cur = self.root
        while True:
            if val < cur.info:
                if cur.left:
                    cur = cur.left
                else:
                    cur.left = Node(val)
                    break
            elif val > cur.info:
                if cur.right:
                    cur = cur.right
                else:
                    cur.right = Node(val)
                    break
            else:
                break


def preOrder(root):
    out = []
    stack = [root] if root else []
    while stack:
        node = stack.pop()
        out.append(node.info)
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
    print(' '.join(map(str, out)))


tree = BinarySearchTree()
t = int(input())
arr = list(map(int, input().split()))
for i in range(t):
    tree.create(arr[i])
preOrder(tree.root)
```

**Watch out.** Inserting values in sorted order makes a path-shaped tree, as deep as the number of nodes. A recursive traversal would then exceed the default recursion limit, while the stack version does not care.

```stdin
6
1 2 5 3 6 4
```

```stdout
1 2 5 3 4 6
```

### Tree: Postorder Traversal

**Problem.** Print the postorder traversal (left, right, node).

**Idea.** Postorder is the reverse of a "node, right, left" preorder. Run that modified preorder with a stack and print the collected values reversed.

**Steps.**
1. Stack: pop, record, push left then right (so right is processed first).
2. Print the record reversed.

```python
class Node:
    def __init__(self, info):
        self.info = info
        self.left = None
        self.right = None


class BinarySearchTree:
    def __init__(self):
        self.root = None

    def create(self, val):
        if self.root is None:
            self.root = Node(val)
            return
        cur = self.root
        while True:
            if val < cur.info:
                if cur.left:
                    cur = cur.left
                else:
                    cur.left = Node(val)
                    break
            elif val > cur.info:
                if cur.right:
                    cur = cur.right
                else:
                    cur.right = Node(val)
                    break
            else:
                break


def postOrder(root):
    out = []
    stack = [root] if root else []
    while stack:
        node = stack.pop()
        out.append(node.info)
        if node.left:
            stack.append(node.left)
        if node.right:
            stack.append(node.right)
    print(' '.join(map(str, reversed(out))))


tree = BinarySearchTree()
t = int(input())
arr = list(map(int, input().split()))
for i in range(t):
    tree.create(arr[i])
postOrder(tree.root)
```

**Watch out.** The order of the two pushes is the opposite of the preorder version. Getting it wrong prints "node, left, right" reversed, which is not postorder.

```stdin
6
1 2 5 3 6 4
```

```stdout
4 3 6 5 2 1
```

### Tree: Inorder Traversal

**Problem.** Print the inorder traversal (left, node, right); for a BST this is the sorted order.

**Idea.** Iterative inorder: walk left as far as possible, pushing nodes; pop one, visit it, then continue with its right subtree.

**Steps.**
1. `cur = root`; loop: push and go left while `cur`; pop, visit, `cur = node.right`.

```python
class Node:
    def __init__(self, info):
        self.info = info
        self.left = None
        self.right = None


class BinarySearchTree:
    def __init__(self):
        self.root = None

    def create(self, val):
        if self.root is None:
            self.root = Node(val)
            return
        cur = self.root
        while True:
            if val < cur.info:
                if cur.left:
                    cur = cur.left
                else:
                    cur.left = Node(val)
                    break
            elif val > cur.info:
                if cur.right:
                    cur = cur.right
                else:
                    cur.right = Node(val)
                    break
            else:
                break


def inOrder(root):
    out = []
    stack = []
    cur = root
    while cur or stack:
        while cur:
            stack.append(cur)
            cur = cur.left
        node = stack.pop()
        out.append(node.info)
        cur = node.right
    print(' '.join(map(str, out)))


tree = BinarySearchTree()
t = int(input())
arr = list(map(int, input().split()))
for i in range(t):
    tree.create(arr[i])
inOrder(tree.root)
```

**Watch out.** For a BST, the output is simply the distinct input values sorted; that makes a handy self-check. Duplicates are ignored by `create`.

```stdin
6
1 2 5 3 6 4
```

```stdout
1 2 3 4 5 6
```

### Tree: Height of a Binary Tree

**Problem.** Print the height of the tree, measured in **edges** on the longest root-to-leaf path.

**Idea.** Count the levels with a BFS (one queue pass per level); the height is the number of levels minus one. This is iterative, so it is safe for deep trees.

**Steps.**
1. Level-by-level BFS counting levels; print `levels − 1`.

```python
class Node:
    def __init__(self, info):
        self.info = info
        self.left = None
        self.right = None


class BinarySearchTree:
    def __init__(self):
        self.root = None

    def create(self, val):
        if self.root is None:
            self.root = Node(val)
            return
        cur = self.root
        while True:
            if val < cur.info:
                if cur.left:
                    cur = cur.left
                else:
                    cur.left = Node(val)
                    break
            elif val > cur.info:
                if cur.right:
                    cur = cur.right
                else:
                    cur.right = Node(val)
                    break
            else:
                break


def height(root):
    level = [root] if root else []
    levels = 0
    while level:
        levels += 1
        level = [c for node in level for c in (node.left, node.right) if c]
    return levels - 1


tree = BinarySearchTree()
t = int(input())
arr = list(map(int, input().split()))
for i in range(t):
    tree.create(arr[i])
print(height(tree.root))
```

**Watch out.** HackerRank counts edges, so a single node has height 0, not 1.

```stdin
7
3 5 2 1 4 6 7
```

```stdout
3
```

### Tree : Top View

**Problem.** Print the nodes visible from above, from the leftmost column to the rightmost.

**Idea.** Give each node a horizontal distance: the root is 0, a left child is `−1` and a right child is `+1` relative to its parent. Do a BFS (top to bottom). The **first** node met in each column is the one seen from the top. Then print the columns from left to right.

**Steps.**
1. BFS with `(node, hd)`; record a column only the first time it appears.
2. Print the values sorted by column.

```python
from collections import deque


class Node:
    def __init__(self, info):
        self.info = info
        self.left = None
        self.right = None


class BinarySearchTree:
    def __init__(self):
        self.root = None

    def create(self, val):
        if self.root is None:
            self.root = Node(val)
            return
        cur = self.root
        while True:
            if val < cur.info:
                if cur.left:
                    cur = cur.left
                else:
                    cur.left = Node(val)
                    break
            elif val > cur.info:
                if cur.right:
                    cur = cur.right
                else:
                    cur.right = Node(val)
                    break
            else:
                break


def topView(root):
    first = {}
    q = deque([(root, 0)])
    while q:
        node, hd = q.popleft()
        if hd not in first:
            first[hd] = node.info
        if node.left:
            q.append((node.left, hd - 1))
        if node.right:
            q.append((node.right, hd + 1))
    print(' '.join(str(first[k]) for k in sorted(first)))


tree = BinarySearchTree()
t = int(input())
arr = list(map(int, input().split()))
for i in range(t):
    tree.create(arr[i])
topView(tree.root)
```

**Watch out.** A DFS would also work, but it has to compare depths. With DFS, a deep node found early could wrongly claim a column that a shallower node owns. BFS order settles that automatically.

```stdin
6
1 2 5 3 6 4
```

```stdout
1 2 5 6
```

### Tree: Level Order Traversal

**Problem.** Print the nodes level by level, left to right.

**Idea.** A breadth-first search with a queue visits the nodes exactly in level order.

**Steps.**
1. Queue the root; pop, print, enqueue the left then the right child.

```python
from collections import deque


class Node:
    def __init__(self, info):
        self.info = info
        self.left = None
        self.right = None


class BinarySearchTree:
    def __init__(self):
        self.root = None

    def create(self, val):
        if self.root is None:
            self.root = Node(val)
            return
        cur = self.root
        while True:
            if val < cur.info:
                if cur.left:
                    cur = cur.left
                else:
                    cur.left = Node(val)
                    break
            elif val > cur.info:
                if cur.right:
                    cur = cur.right
                else:
                    cur.right = Node(val)
                    break
            else:
                break


def levelOrder(root):
    out = []
    q = deque([root] if root else [])
    while q:
        node = q.popleft()
        out.append(node.info)
        if node.left:
            q.append(node.left)
        if node.right:
            q.append(node.right)
    print(' '.join(map(str, out)))


tree = BinarySearchTree()
t = int(input())
arr = list(map(int, input().split()))
for i in range(t):
    tree.create(arr[i])
levelOrder(tree.root)
```

**Watch out.** Use `collections.deque`; `list.pop(0)` is O(n) per pop and turns the BFS quadratic.

```stdin
6
1 2 5 3 6 4
```

```stdout
1 2 5 3 6 4
```

### Binary Search Tree : Insertion

**Problem.** Implement `insert(val)` for a BST, then print the preorder traversal.

**Idea.** Walk from the root, going left for smaller values and right for larger ones, until an empty spot is found; attach the new node there.

**Steps.**
1. Empty tree → the new node is the root.
2. Otherwise descend and attach at the first missing child.

```python
class Node:
    def __init__(self, info):
        self.info = info
        self.left = None
        self.right = None


class BinarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, val):
        node = Node(val)
        if self.root is None:
            self.root = node
            return self.root
        cur = self.root
        while True:
            if val < cur.info:
                if cur.left is None:
                    cur.left = node
                    break
                cur = cur.left
            else:
                if cur.right is None:
                    cur.right = node
                    break
                cur = cur.right
        return self.root


def preOrder(root):
    out = []
    stack = [root] if root else []
    while stack:
        node = stack.pop()
        out.append(node.info)
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
    print(' '.join(map(str, out)))


tree = BinarySearchTree()
t = int(input())
arr = list(map(int, input().split()))
for i in range(t):
    tree.insert(arr[i])
preOrder(tree.root)
```

**Watch out.** The iterative loop avoids deep recursion. The problem guarantees distinct values, so it does not matter which side ties go to.

```stdin
6
4 2 3 1 7 6
```

```stdout
4 2 1 3 7 6
```

### Tree: Huffman Decoding

**Problem.** Decode a bit string using a Huffman tree: `0` goes left, `1` goes right, and reaching a leaf emits its character.

**Idea.** Walk the tree bit by bit and restart at the root after every leaf. HackerRank's hidden code builds the tree from the input text, encodes the text, and prints what `decodeHuff` returns. This program does the same: it builds a Huffman tree with a heap, encodes the text, and decodes it again.

**Steps.**
1. Build the Huffman tree (repeatedly merge the two least frequent subtrees).
2. Encode with the leaf codes; decode by walking the tree; print.

```python
import heapq
import itertools


class Node:
    def __init__(self, freq, data):
        self.freq = freq
        self.data = data
        self.left = None
        self.right = None


def build(text):
    counter = itertools.count()
    freq = {}
    for ch in text:
        freq[ch] = freq.get(ch, 0) + 1
    heap = [(f, next(counter), Node(f, ch)) for ch, f in freq.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        f1, _, a = heapq.heappop(heap)
        f2, _, b = heapq.heappop(heap)
        parent = Node(f1 + f2, '\0')
        parent.left, parent.right = a, b
        heapq.heappush(heap, (f1 + f2, next(counter), parent))
    return heap[0][2]


def codes(root):
    table = {}
    stack = [(root, '')]
    while stack:
        node, path = stack.pop()
        if node.left is None and node.right is None:
            table[node.data] = path or '0'       # a single-symbol text still needs one bit
        else:
            stack.append((node.left, path + '0'))
            stack.append((node.right, path + '1'))
    return table


def decodeHuff(root, s):
    if root.left is None and root.right is None:
        return root.data * len(s)
    out = []
    node = root
    for bit in s:
        node = node.left if bit == '0' else node.right
        if node.left is None and node.right is None:
            out.append(node.data)
            node = root
    return ''.join(out)


text = input().strip()
root = build(text)
table = codes(root)
print(decodeHuff(root, ''.join(table[ch] for ch in text)))
```

**Watch out.** If the text has a single distinct character, the tree is one leaf. Each character is then encoded as one bit, and decoding must emit one character per bit.

```stdin
ABACA
```

```stdout
ABACA
```

### Binary Search Tree : Lowest Common Ancestor

**Problem.** Find the lowest common ancestor of two values in a BST.

**Idea.** In a BST, if both values are smaller than the current node, the LCA is in the left subtree, and if both are larger, it is in the right subtree. Otherwise the current node splits them (or equals one of them), so it is the LCA.

**Steps.**
1. Descend while both values lie on the same side; return the node where they split.

```python
class Node:
    def __init__(self, info):
        self.info = info
        self.left = None
        self.right = None


class BinarySearchTree:
    def __init__(self):
        self.root = None

    def create(self, val):
        if self.root is None:
            self.root = Node(val)
            return
        cur = self.root
        while True:
            if val < cur.info:
                if cur.left:
                    cur = cur.left
                else:
                    cur.left = Node(val)
                    break
            elif val > cur.info:
                if cur.right:
                    cur = cur.right
                else:
                    cur.right = Node(val)
                    break
            else:
                break


def lca(root, v1, v2):
    node = root
    while node:
        if v1 < node.info and v2 < node.info:
            node = node.left
        elif v1 > node.info and v2 > node.info:
            node = node.right
        else:
            return node


tree = BinarySearchTree()
t = int(input())
arr = list(map(int, input().split()))
for i in range(t):
    tree.create(arr[i])
v = list(map(int, input().split()))
print(lca(tree.root, v[0], v[1]).info)
```

**Watch out.** The BST order makes this O(height) without parent pointers or any extra memory. In a general binary tree you would need a different method.

```stdin
6
4 2 3 1 7 6
1 7
```

```stdout
4
```

### Swap Nodes [Algo]

**Problem.** A binary tree is given by child indices (`-1` = none). For each query `k`, swap the left and right children of every node at a depth that is a multiple of `k`, then print the inorder traversal.

**Idea.** Swaps are cumulative across queries. Compute every node's depth once with a BFS. For each query, swap at the depths divisible by `k`, then run an iterative inorder traversal.

**Steps.**
1. Depths by BFS from node 1 (depth 1).
2. Per query: swap the children at the matching depths; iterative inorder; record.

```python
import os
from collections import deque


def swapNodes(indexes, queries):
    n = len(indexes)
    left = [0] + [a for a, _ in indexes]
    right = [0] + [b for _, b in indexes]
    depth = [0] * (n + 1)
    depth[1] = 1
    q = deque([1])
    while q:
        v = q.popleft()
        for c in (left[v], right[v]):
            if c != -1:
                depth[c] = depth[v] + 1
                q.append(c)
    result = []
    for k in queries:
        for v in range(1, n + 1):
            if depth[v] % k == 0:
                left[v], right[v] = right[v], left[v]
        out = []
        stack = []
        cur = 1
        while cur != -1 or stack:
            while cur != -1:
                stack.append(cur)
                cur = left[cur]
            v = stack.pop()
            out.append(v)
            cur = right[v]
        result.append(out)
    return result


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    indexes = [list(map(int, input().rstrip().split())) for _ in range(n)]
    queries = [int(input().strip()) for _ in range(int(input().strip()))]
    fptr.write('\n'.join(' '.join(map(str, x)) for x in swapNodes(indexes, queries)) + '\n')
    fptr.close()
```

**Watch out.** The tree can be a path of 1024 nodes, so the traversal must be iterative. Swapping does not change any node's depth, so the depths are computed only once.

```stdin
3
2 3
-1 -1
-1 -1
2
1
1
```

```stdout
3 1 2
2 1 3
```
