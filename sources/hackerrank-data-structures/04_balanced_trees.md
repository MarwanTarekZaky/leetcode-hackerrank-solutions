## Balanced Trees

### Self Balancing Tree

**Problem.** Insert values into an AVL tree, rotating as needed so every node's balance factor (left height − right height) stays in `[−1, 1]`.

**Idea.** Use the standard recursive AVL insert:
1. Insert as in a BST.
2. On the way back up, update each node's height.
3. Fix any balance factor of ±2 with one of the four rotation cases:
   - **left-left:** a right rotation;
   - **right-right:** a left rotation;
   - **left-right:** a left rotation of the child, then a right rotation;
   - **right-left:** the mirror of left-right.

HackerRank's hidden stub builds the tree and prints it. For local testing, this program inserts the given values one by one, then prints the inorder and preorder traversals with each node's balance factor.

**Steps.**
1. `insert(root, v)`: BST insert, update the height, rebalance, return the new subtree root.
2. Print `value(BF=b)` in inorder and in preorder.

```python
import sys

sys.setrecursionlimit(10000)


class node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None
        self.ht = 0


def h(t):
    return t.ht if t else -1


def fix(t):
    t.ht = 1 + max(h(t.left), h(t.right))


def rot_right(t):
    l = t.left
    t.left = l.right
    l.right = t
    fix(t)
    fix(l)
    return l


def rot_left(t):
    r = t.right
    t.right = r.left
    r.left = t
    fix(t)
    fix(r)
    return r


def insert(root, val):
    if root is None:
        return node(val)
    if val < root.val:
        root.left = insert(root.left, val)
    else:
        root.right = insert(root.right, val)
    fix(root)
    bf = h(root.left) - h(root.right)
    if bf > 1:
        if val > root.left.val:                  # left-right
            root.left = rot_left(root.left)
        return rot_right(root)
    if bf < -1:
        if val < root.right.val:                 # right-left
            root.right = rot_right(root.right)
        return rot_left(root)
    return root


def walk(t, order, out):
    if t is None:
        return
    tag = f"{t.val}(BF={h(t.left) - h(t.right)})"
    if order == 'pre':
        out.append(tag)
    walk(t.left, order, out)
    if order == 'in':
        out.append(tag)
    walk(t.right, order, out)


data = sys.stdin.read().split()
n = int(data[0])
root = None
for v in map(int, data[1:1 + n]):
    root = insert(root, v)
for order in ('in', 'pre'):
    out = []
    walk(root, order, out)
    print(' '.join(out))
```

**Watch out.** The tree height stays O(log n), so recursion is safe even for many insertions. Heights must be updated bottom-up after every rotation, child first, then the new parent.

```stdin
5
3 2 4 5 6
```

```stdout
2(BF=0) 3(BF=-1) 4(BF=0) 5(BF=0) 6(BF=0)
3(BF=-1) 2(BF=0) 5(BF=0) 4(BF=0) 6(BF=0)
```

### Array and simple queries

**Problem.** Up to 10⁵ times, move the block `A[i..j]` to the front (type 1) or to the back (type 2). Then print `|A₁ − A_N|` and the final array.

**Idea.** A **chunked list** (a simple rope). Keep the array as a list of Python lists.
- **Cutting.** To cut at position `p`, find the chunk through prefix sums of the chunk lengths (computed in C with `accumulate` and `bisect`) and split that one chunk.
- **Moving.** A query cuts at `i−1` and at `j`, then reorders the chunk references, which is O(number of chunks).
- **Rebuilding.** When there are too many chunks, flatten and re-chunk, about every √n queries.

Every step is a C-level list operation on about √n items.

**Steps.**
1. `cut(p)` returns the index of the chunk that starts at `p`, splitting if needed.
2. Per query: `a = cut(i−1)`, `b = cut(j)`; move `chunks[a:b]` to the front or back; rebuild if needed.

```python
import sys
from bisect import bisect_right
from itertools import accumulate, chain


def main():
    data = sys.stdin.buffer.read().split()
    n, m = int(data[0]), int(data[1])
    arr = data[2:2 + n]
    B = 1500
    chunks = [arr[k:k + B] for k in range(0, n, B)]

    def cut(p):
        if p == 0:
            return 0
        ends = list(accumulate(map(len, chunks)))
        k = bisect_right(ends, p - 1)              # chunk containing position p - 1
        start = ends[k] - len(chunks[k])
        if ends[k] == p:
            return k + 1
        c = chunks[k]
        chunks[k:k + 1] = [c[:p - start], c[p - start:]]
        return k + 1

    pos = 2 + n
    for _ in range(m):
        t, i, j = int(data[pos]), int(data[pos + 1]), int(data[pos + 2])
        pos += 3
        a = cut(i - 1)
        b = cut(j)
        mid = chunks[a:b]
        rest = chunks[:a] + chunks[b:]
        chunks = mid + rest if t == 1 else rest + mid
        if len(chunks) > n // B + 240:             # rebuild about every 120 queries
            flat = list(chain.from_iterable(chunks))
            chunks = [flat[k:k + B] for k in range(0, n, B)]
    flat = list(chain.from_iterable(chunks))
    print(abs(int(flat[0]) - int(flat[-1])))
    print(b' '.join(flat).decode())


main()
```

**Watch out.** `chunks` is rebound to a new list after each move, so `cut` must look it up afresh every time (it reads the variable from the enclosing scope). The elements stay as their input byte strings, so printing joins them with no conversions.

```stdin
8 4
1 2 3 4 5 6 7 8
1 2 4
2 3 5
1 4 7
2 1 4
```

```stdout
1
2 3 6 5 7 8 4 1
```

### Median Updates

**Problem.** Process `a x` (add) and `r x` (remove) operations and print the median after each one. Print `Wrong!` for removing a missing value or when the list is empty. Integers print without a decimal point, and halves as `.5`.

**Idea.** Read all operations first and compress the values, then keep a **Fenwick tree of counts**. The `k`-th smallest value is found by the usual binary descent over the tree. With an even count, the median is the average of the two middle values. Their sum `s` is printed exactly: `s/2` if `s` is even, otherwise `⌊|s|/2⌋.5` with the right sign.

**Steps.**
1. Offline compression; a Fenwick tree for counts; a dictionary for multiplicities.
2. After each valid operation, print the median from one or two `k`-th queries.

```python
import sys


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    ops = [(data[1 + 2 * i], int(data[2 + 2 * i])) for i in range(n)]
    vals = sorted({x for _, x in ops})
    idx = {v: i + 1 for i, v in enumerate(vals)}
    size = len(vals)
    tree = [0] * (size + 1)
    LOG = 1 << size.bit_length()

    def add(i, d):
        while i <= size:
            tree[i] += d
            i += i & -i

    def kth(k):                                    # 1-based k-th smallest
        pos = 0
        step = LOG
        while step:
            nxt = pos + step
            if nxt <= size and tree[nxt] < k:
                pos = nxt
                k -= tree[nxt]
            step >>= 1
        return vals[pos]

    cnt = {}
    total = 0
    out = []
    for op, x in ops:
        if op == 'a':
            cnt[x] = cnt.get(x, 0) + 1
            add(idx[x], 1)
            total += 1
        else:
            if cnt.get(x, 0) == 0:
                out.append('Wrong!')
                continue
            cnt[x] -= 1
            add(idx[x], -1)
            total -= 1
        if total == 0:
            out.append('Wrong!')
        elif total % 2:
            out.append(str(kth(total // 2 + 1)))
        else:
            s = kth(total // 2) + kth(total // 2 + 1)
            if s % 2 == 0:
                out.append(str(s // 2))
            else:
                out.append(('-' if s < 0 else '') + f"{abs(s) // 2}.5")
    print('\n'.join(out))


main()
```

**Watch out.** Printing a float directly would show `3.0` instead of the required `3`. The integer-only formatting avoids that and also gets negative halves such as `-0.5` right. Removing the last element prints `Wrong!`, because the list is then empty.

```stdin
7
r 1
a 1
a 2
a 1
r 1
r 2
r 1
```

```stdout
Wrong!
1
1.5
1
1.5
1
Wrong!
```
