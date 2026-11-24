## Multiple Choice

### Data Structures MCQ 1

**Problem.** If a tree has `n` nodes, how many edges does it have?

**Idea.** **`n − 1`.** A tree is connected and has no cycles. Build it by adding the nodes one at a time: every new node needs exactly one edge to join the existing connected part. A second edge would create a cycle, and no edge would leave it disconnected. So `n` nodes use `n − 1` edges. The small program below checks this on any tree given as an edge list: it counts the edges and confirms that they connect all `n` nodes.

**Steps.**
1. Choose the answer `n − 1`.
2. (Demo) Read a tree, verify it is connected with `n − 1` edges, and print the count.

```python
import sys


def main():
    data = list(map(int, sys.stdin.read().split()))
    n = data[0]
    edges = [(data[1 + 2 * i], data[2 + 2 * i]) for i in range((len(data) - 1) // 2)]
    adj = {v: [] for v in range(1, n + 1)}
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    seen = {1}
    stack = [1]
    while stack:
        for u in adj[stack.pop()]:
            if u not in seen:
                seen.add(u)
                stack.append(u)
    assert len(seen) == n and len(edges) == n - 1
    print(len(edges))


main()
```

**Watch out.** The answer is the formula `n − 1`. Neither `n` nor `n + 1` is possible for a tree: any extra edge would close a cycle.

```stdin
5
1 2
1 3
3 4
3 5
```

```stdout
4
```

### Data Structures MCQ 2

**Problem.** Which data structure supports **updates and range queries on an array in `O(log n)`** each?

**Idea.** **Segment tree.** It stores aggregates (sum, min, …) of the array segments in a balanced binary tree. A point update changes one leaf and its `O(log n)` ancestors. A range query combines `O(log n)` stored segments.
- A **Fenwick tree** (BIT) also does this for invertible operations such as sums.
- Plain stacks, queues and linked lists need `O(n)` for one of the two operations.

The demo implements an iterative segment tree for range sums.

**Steps.**
1. Choose **segment tree**.
2. (Demo) Build bottom-up; `update` walks up from the leaf; `query` combines the boundary nodes.

```python
import sys


def main():
    data = sys.stdin.read().split()
    n, q = int(data[0]), int(data[1])
    tree = [0] * (2 * n)
    tree[n:] = map(int, data[2:2 + n])
    for i in range(n - 1, 0, -1):
        tree[i] = tree[2 * i] + tree[2 * i + 1]
    out = []
    pos = 2 + n
    for _ in range(q):
        t, a, b = data[pos], int(data[pos + 1]), int(data[pos + 2])
        pos += 3
        if t == 'u':                                 # a[a] = b
            i = a + n
            tree[i] = b
            while i > 1:
                i //= 2
                tree[i] = tree[2 * i] + tree[2 * i + 1]
        else:                                        # sum of a[a .. b-1]
            lo, hi, s = a + n, b + n, 0
            while lo < hi:
                if lo & 1:
                    s += tree[lo]
                    lo += 1
                if hi & 1:
                    hi -= 1
                    s += tree[hi]
                lo //= 2
                hi //= 2
            out.append(s)
    print('\n'.join(map(str, out)))


main()
```

**Watch out.** A prefix-sum array answers queries in O(1) but needs O(n) per update. A segment tree balances both at O(log n).

```stdin
5 3
1 2 3 4 5
q 1 4
u 2 10
q 0 5
```

```stdout
9
22
```

### Data Structures MCQ 3

**Problem.** Which data structure has **Last In, First Out** ordering?

**Idea.** **Stack.** The most recently pushed element is the first one popped. A **queue** is the opposite (first in, first out). The demo pushes the input values and pops them all, printing them in reverse order of arrival.

**Steps.**
1. Choose **stack**.
2. (Demo) Push all values, then pop until empty.

```python
import sys

data = sys.stdin.read().split()
stack = []
for x in data[1:]:
    stack.append(x)
out = []
while stack:
    out.append(stack.pop())
print(' '.join(out))
```

**Watch out.** Python lists are efficient stacks: `append` and `pop()` from the end are O(1). Popping from the front (`pop(0)`) is O(n).

```stdin
4
a b c d
```

```stdout
d c b a
```
