## Graph Theory

### Tripartite Matching

**Problem.** Three forests share the vertex set `1..n`. Count the ordered triples `(a, b, c)` with `(a, b)` in `G1`, `(b, c)` in `G2` and `(c, a)` in `G3`.

**Idea.** Fix the middle edge. For every `G2` edge, taken in both directions as `(b, c)`, the valid `a` are exactly `N1(b) ∩ N3(c)`. Intersect by scanning the smaller neighbour set and testing membership in the other (a hash set). Forests have small average degree, so the total work stays near O(m√m).

**Steps.**
1. Build neighbour sets for `G1` and `G3`.
2. For each `G2` edge `(u, v)`, add `|N1(u) ∩ N3(v)| + |N1(v) ∩ N3(u)|`.

```python
import os


def tripartiteMatching(n, g1, g2, g3):
    n1 = [set() for _ in range(n + 1)]
    n3 = [set() for _ in range(n + 1)]
    for u, v in g1:
        n1[u].add(v)
        n1[v].add(u)
    for u, v in g3:
        n3[u].add(v)
        n3[v].add(u)

    def common(x, y):
        if len(x) > len(y):
            x, y = y, x
        return sum(1 for a in x if a in y)

    return sum(common(n1[u], n3[v]) + common(n1[v], n3[u]) for u, v in g2)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    graphs = []
    for _ in range(3):
        m = int(input().strip())
        graphs.append([list(map(int, input().split())) for _ in range(m)])
    fptr.write(str(tripartiteMatching(n, *graphs)) + '\n')
    fptr.close()
```

**Watch out.** The triples are ordered, so each `G2` edge counts in both directions. The distinctness conditions hold automatically, because no graph has self-loops.

```stdin
3
2
1 2
2 3
3
1 2
1 3
2 3
2
1 3
2 3
```

```stdout
3
```

### Tree Flow

**Problem.** Find an antisymmetric matrix `A` with `|A[u][v]| ≤ dist(u, v)` (tree distance) and zero row sums for every `u ∉ {1, n}`, maximising `Σ_i A[1][i]`.

**Idea.** This is a max flow from 1 to `n` in the *complete* graph whose capacities are the tree distances. By max-flow/min-cut, it equals the cheapest cut. Splitting the vertices into any `S ∋ 1` and its complement `∌ n` costs `Σ dist(u, v)` over the crossing pairs. Moving vertices across never beats isolating one terminal: for any `S` and outside `v`, `dist(1, v)` is at most `dist(1, u) + dist(u, v)`, and that argument extends over all pairs. So the min cut is `min(Σ_v dist(1, v), Σ_v dist(n, v))`.

**Steps.**
1. Compute the distances from 1 and from `n` with one tree traversal each.
2. Return the smaller of the two sums.

```python
import os


def treeFlow(n, tree):
    adj = [[] for _ in range(n + 1)]
    for a, b, c in tree:
        adj[a].append((b, c))
        adj[b].append((a, c))

    def total(src):
        dist = [-1] * (n + 1)
        dist[src] = 0
        stack = [src]
        while stack:
            u = stack.pop()
            for v, c in adj[u]:
                if dist[v] < 0:
                    dist[v] = dist[u] + c
                    stack.append(v)
        return sum(dist[1:])

    return min(total(1), total(n))


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    tree = [list(map(int, input().split())) for _ in range(n - 1)]
    fptr.write(str(treeFlow(n, tree)) + '\n')
    fptr.close()
```

**Watch out.** `n` reaches 5·10⁵, so use an explicit stack rather than recursion. The cut formula was checked against an exhaustive min cut over every vertex subset on small random trees.

```stdin
3
1 2 2
1 3 1
```

```stdout
3
```

### DAG Queries

**Problem.** On a DAG, process three kinds of query: set every vertex reachable from `u` to `x`; lower every reachable vertex above `x` to `x`; print `a_u`.

**Idea.** Process the queries in blocks of about √q.
- **Within a block.** At the start, compute for every vertex a bitmask of which of the block's update vertices reach it. One pass in topological order does it: `mask[v] |= mask[u]` along every edge. A print query then needs only the block's earlier updates that reach `u`. The value is the last "set" among them, or the stored value, lowered by every later "min".
- **At the end of a block.** Apply the block's updates to the stored values by walking the updates **backwards** with DFS.
  - **Freezing.** A "set" freezes everything it reaches at `min(x, pending minimum)`. A frozen vertex's descendants are already frozen, so the DFS stops there.
  - **Pending minimum.** A "min" only lowers the pending minimum of unfrozen vertices. It stops where the pending minimum is already ≤ `x`.

**Steps.**
1. Topologically sort once.
2. For each block, build the masks, then answer each print query from the stored value plus the relevant earlier updates of the block.
3. Fold the block's updates into the stored values with the backwards pruned DFS.

```python
import sys
from collections import deque


def main():
    data = sys.stdin.buffer.read().split()
    n, m, q = int(data[0]), int(data[1]), int(data[2])
    adj = [[] for _ in range(n + 1)]
    indeg = [0] * (n + 1)
    pos = 3
    for _ in range(m):
        u, v = int(data[pos]), int(data[pos + 1])
        pos += 2
        adj[u].append(v)
        indeg[v] += 1
    topo = []
    queue = deque(v for v in range(1, n + 1) if indeg[v] == 0)
    while queue:
        u = queue.popleft()
        topo.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                queue.append(v)
    queries = []
    for _ in range(q):
        t = int(data[pos])
        if t == 3:
            queries.append((3, int(data[pos + 1]), 0))
            pos += 2
        else:
            queries.append((t, int(data[pos + 1]), int(data[pos + 2])))
            pos += 3

    val = [0] * (n + 1)
    inf = float('inf')
    pend = [inf] * (n + 1)
    frozen = [False] * (n + 1)
    out = []
    block = max(1, int(q ** 0.5))
    for start in range(0, q, block):
        chunk = queries[start:start + block]
        ops = [qq for qq in chunk if qq[0] != 3]
        mask = [0] * (n + 1)
        t1 = 0
        for i, (t, u, x) in enumerate(ops):
            mask[u] |= 1 << i
            if t == 1:
                t1 |= 1 << i
        for u in topo:
            mu = mask[u]
            if mu:
                for v in adj[u]:
                    mask[v] |= mu
        seen = 0
        for t, u, x in chunk:
            if t != 3:
                seen += 1
                continue
            rel = mask[u] & ((1 << seen) - 1)
            sets = rel & t1
            if sets:
                last = sets.bit_length() - 1
                res = ops[last][2]
                rel &= ~((2 << last) - 1)
            else:
                res = val[u]
            mins = rel & ~t1
            while mins:
                low = mins & -mins
                res = min(res, ops[low.bit_length() - 1][2])
                mins ^= low
            out.append(res)
        touched = []
        for t, u, x in reversed(ops):
            stack = [u]
            while stack:
                v = stack.pop()
                if frozen[v]:
                    continue
                if t == 1:
                    frozen[v] = True
                    if pend[v] == inf:
                        touched.append(v)
                    val[v] = min(x, pend[v])
                    pend[v] = inf
                    stack.extend(adj[v])
                elif pend[v] > x:
                    if pend[v] == inf:
                        touched.append(v)
                    pend[v] = x
                    stack.extend(adj[v])
        for v in touched:
            if not frozen[v] and pend[v] < val[v]:
                val[v] = pend[v]
            frozen[v] = False
            pend[v] = inf
    print('\n'.join(map(str, out)))


main()
```

**Watch out.**
- **The pruning argument.** The rules "stop at frozen vertices" and "stop where the pending minimum is ≤ x" are safe because, walking backwards, everything below such a vertex was already handled at least as strongly.
- **Speed.** Updating each query by a full DFS is O(q·(n+m)), far too slow. Even the block version is heavy for CPython, so prefer PyPy.

```stdin
6 5 18
1 2
1 3
3 4
2 4
5 6
1 1 3
3 1
3 2
3 3
3 4
1 2 2
3 1
3 2
3 3
3 4
2 6 7
3 5
3 6
2 1 3
3 1
3 2
3 3
3 4
```

```stdout
3
3
3
3
3
2
3
2
0
0
3
2
3
2
```

### Favorite sequence

**Problem.** Several copies of an unknown sequence of distinct numbers had elements erased. Rebuild the shortest possible original, choosing the lexicographically smallest one on ties.

**Idea.** Each copy keeps the original order, so consecutive numbers in a copy give a precedence edge `a → b`. The shortest original contains each number once, so it is a topological order of these constraints. Kahn's algorithm with a **min-heap** instead of a queue always emits the smallest available number, which gives the lexicographically smallest order.

**Steps.**
1. Add an edge for every adjacent pair in every copy, skipping duplicates.
2. Run Kahn's algorithm with a heap and print the order.

```python
import sys
from heapq import heapify, heappop, heappush


def main():
    data = sys.stdin.read().split()
    pos = 0
    n = int(data[pos]); pos += 1
    succ, indeg = {}, {}
    for _ in range(n):
        k = int(data[pos]); pos += 1
        seq = list(map(int, data[pos:pos + k]))
        pos += k
        for x in seq:
            succ.setdefault(x, set())
            indeg.setdefault(x, 0)
        for a, b in zip(seq, seq[1:]):
            if b not in succ[a]:
                succ[a].add(b)
                indeg[b] += 1
    heap = [x for x, d in indeg.items() if d == 0]
    heapify(heap)
    out = []
    while heap:
        x = heappop(heap)
        out.append(x)
        for y in succ[x]:
            indeg[y] -= 1
            if indeg[y] == 0:
                heappush(heap, y)
    print(' '.join(map(str, out)))


main()
```

**Watch out.** The same pair can appear in many copies; count each edge once, or the in-degrees never reach zero. Only consecutive pairs are needed, because longer-range order follows by transitivity.

```stdin
2
2
1 3
3
2 3 4
```

```stdout
1 2 3 4
```

### Jogging Cats

**Problem.** Count the distinct 4-cycles (as sets of 4 roads) in a simple graph with up to 10⁵ edges.

**Idea.** Count each cycle once from its highest-ranked vertex, ranking vertices by `(degree, id)`.
- **Two-step walks.** For each vertex `u`, walk `u → v → w` with both `v` and `w` ranked below `u`, and count how many such walks end at each `w`.
- **Closing the cycle.** Any two different middle vertices to the same `w` close a 4-cycle `u–v1–w–v2`, so add `C(cnt[w], 2)`.
- **Speed.** Ranking by degree keeps the work at O(m√m).

**Steps.**
1. Sort the vertices by `(degree, id)` to get ranks.
2. For each `u`: for each lower `v` in `adj[u]`, for each lower `w ≠ u` in `adj[v]`, increase `cnt[w]`.
3. Add `C(cnt[w], 2)` for every `w` touched, then reset.

```python
import sys


def main():
    data = sys.stdin.buffer.read().split()
    n, m = int(data[0]), int(data[1])
    adj = [[] for _ in range(n + 1)]
    for i in range(m):
        x, y = int(data[2 + 2 * i]), int(data[3 + 2 * i])
        adj[x].append(y)
        adj[y].append(x)
    rank = [0] * (n + 1)
    for r, v in enumerate(sorted(range(1, n + 1), key=lambda v: (len(adj[v]), v))):
        rank[v] = r
    lower = [[w for w in adj[v] if rank[w] < rank[v]] for v in range(n + 1)]
    cnt = [0] * (n + 1)
    total = 0
    for u in range(1, n + 1):
        ru = rank[u]
        touched = []
        for v in lower[u]:
            for w in adj[v]:
                if rank[w] < ru:
                    if cnt[w] == 0:
                        touched.append(w)
                    cnt[w] += 1
        for w in touched:
            total += cnt[w] * (cnt[w] - 1) // 2
            cnt[w] = 0
    print(total)


main()
```

**Watch out.** The middle step must scan *all* of `adj[v]`, not just `lower[v]`. Only `v` and `w` must rank below `u`; `w` may rank above `v`. A complete graph `K4` contains 3 different 4-cycles.

```stdin
4 6
1 2
2 3
3 4
4 1
1 3
2 4
```

```stdout
3
```

### Quadrant Queries

**Problem.** Points (never on an axis) get range reflections across the x-axis or the y-axis. Answer range queries counting how many points are in each quadrant.

**Idea.** Segment tree with lazy flips. Each node stores its range's counts per quadrant.
- **The flips.** Reflecting across the x-axis swaps quadrants 1↔4 and 2↔3. Reflecting across the y-axis swaps 1↔2 and 3↔4.
- **The lazy tag.** A node's pending tag is just two bits (x-flip, y-flip), and they combine by XOR. Applying a tag to a node swaps its counts, so it is O(1).

**Steps.**
1. Build leaves from each point's quadrant.
2. Updates: push tags down, toggle the fully covered nodes, then pull the counts up.
3. Queries: add up the counts of the covered nodes.

```python
import sys


def quadrant(x, y):
    if x > 0:
        return 0 if y > 0 else 3
    return 1 if y > 0 else 2


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    pts = [quadrant(int(data[1 + 2 * i]), int(data[2 + 2 * i])) for i in range(n)]
    pos = 1 + 2 * n
    q = int(data[pos]); pos += 1
    size = 1
    while size < n:
        size *= 2
    cnt = [[0, 0, 0, 0] for _ in range(2 * size)]
    tag = [0] * (2 * size)
    for i, qd in enumerate(pts):
        cnt[size + i][qd] = 1
    for i in range(size - 1, 0, -1):
        cnt[i] = [a + b for a, b in zip(cnt[2 * i], cnt[2 * i + 1])]

    def apply(node, f):
        c = cnt[node]
        if f & 1:
            c[0], c[3], c[1], c[2] = c[3], c[0], c[2], c[1]
        if f & 2:
            c[0], c[1], c[2], c[3] = c[1], c[0], c[3], c[2]
        tag[node] ^= f

    def update(node, lo, hi, l, r, f):
        if r < lo or hi < l:
            return
        if l <= lo and hi <= r:
            apply(node, f)
            return
        if tag[node]:
            apply(2 * node, tag[node])
            apply(2 * node + 1, tag[node])
            tag[node] = 0
        mid = (lo + hi) // 2
        update(2 * node, lo, mid, l, r, f)
        update(2 * node + 1, mid + 1, hi, l, r, f)
        cnt[node] = [a + b for a, b in zip(cnt[2 * node], cnt[2 * node + 1])]

    def query(node, lo, hi, l, r, acc):
        if r < lo or hi < l:
            return
        if l <= lo and hi <= r:
            for k in range(4):
                acc[k] += cnt[node][k]
            return
        if tag[node]:
            apply(2 * node, tag[node])
            apply(2 * node + 1, tag[node])
            tag[node] = 0
        mid = (lo + hi) // 2
        query(2 * node, lo, mid, l, r, acc)
        query(2 * node + 1, mid + 1, hi, l, r, acc)

    out = []
    for _ in range(q):
        kind, i, j = data[pos], int(data[pos + 1]) - 1, int(data[pos + 2]) - 1
        pos += 3
        if kind == b'C':
            acc = [0, 0, 0, 0]
            query(1, 0, size - 1, i, j, acc)
            out.append(' '.join(map(str, acc)))
        else:
            update(1, 0, size - 1, i, j, 1 if kind == b'X' else 2)
    print('\n'.join(out))


main()
```

**Watch out.** Applying the same reflection twice cancels it, so tags must combine with XOR, not overwrite. With up to 10⁶ queries, read all input at once; even so, CPython is slow here, so prefer PyPy.

```stdin
4
1 1
-1 1
-1 -1
1 -1
5
C 1 4
X 2 4
C 3 4
Y 1 2
C 1 3
```

```stdout
1 1 1 1
1 1 0 0
0 2 0 1
```

### Hacker Country

**Problem.** In a complete directed graph (n ≤ 500), find the cycle with the minimum average toll per road. Print it as a reduced fraction.

**Idea.** Karp's minimum mean cycle algorithm:
- **Walk table.** Let `D_k[v]` be the cheapest walk of exactly `k` edges ending at `v`, starting anywhere (`D_0 = 0`).
- **Formula.** The minimum mean equals `min over v of max over k of (D_n[v] − D_k[v]) / (n − k)`.
- **Speed.** Each step `D_k = min over u of (D_{k−1}[u] + w[u][·])` is one NumPy operation on the n×n matrix, so the whole table costs O(n³) inside NumPy.
- **Exactness.** The fractions are compared exactly with cross-multiplication.

**Steps.**
1. Set the diagonal to infinity, because there are no self-roads.
2. Build `D_0..D_n` with `D_k = (D_{k−1}[:, None] + W).min(axis=0)`.
3. For each `v` with finite `D_n[v]`, take the largest fraction over `k`; keep the smallest across `v`. Reduce with `gcd`.

```python
import os
from math import gcd

import numpy as np


def hackerCountry(tolls):
    n = len(tolls)
    big = 10 ** 12
    w = np.array(tolls, dtype=np.int64)
    np.fill_diagonal(w, big)
    d = np.zeros((n + 1, n), dtype=np.int64)
    for k in range(1, n + 1):
        d[k] = np.minimum((d[k - 1][:, None] + w).min(axis=0), big)
    best = None
    for v in range(n):
        if d[n][v] >= big:
            continue
        worst = None
        for k in range(n):
            if d[k][v] >= big:
                continue
            num, den = int(d[n][v] - d[k][v]), n - k
            if worst is None or num * worst[1] > worst[0] * den:
                worst = (num, den)
        if best is None or worst[0] * best[1] < best[0] * worst[1]:
            best = worst
    g = gcd(best[0], best[1])
    return f"{best[0] // g}/{best[1] // g}"


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    tolls = [list(map(int, input().split())) for _ in range(n)]
    fptr.write(hackerCountry(tolls) + '\n')
    fptr.close()
```

**Watch out.** The diagonal 0 means "no road", not a free self-loop; leaving it at 0 would give the answer 0. Binary search on the mean with floats can't produce an exact fraction, and Karp gives the exact answer directly.

```stdin
2
0 1
2 0
```

```stdout
3/2
```

### HackerX

**Problem.** Missile `i` arrives at time `t_i` with frequency `f_i`. One defence missile can handle missile `i` and then missile `j` if `|f_j − f_i| ≤ t_j − t_i`. Find the minimum number of defence missiles.

**Idea.** Substitute `a = t + f` and `b = t − f`. Then "one missile can handle `i` then `j`" becomes simply `a_i ≤ a_j` and `b_i ≤ b_j`, a 2D dominance order. The minimum number of chains covering it equals its largest antichain (Dilworth's theorem). After sorting by `(a, b)`, that is the longest strictly decreasing subsequence of `b`.

**Steps.**
1. Map each missile to `(t + f, t − f)` and sort.
2. Find the longest strictly increasing subsequence of `−b` (patience sorting with `bisect_left`).

```python
import os
from bisect import bisect_left


def missileDefend(missiles):
    pts = sorted((t + f, t - f) for t, f in missiles)
    tails = []
    for _, b in pts:
        x = -b
        i = bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    missiles = [list(map(int, input().split())) for _ in range(n)]
    fptr.write(str(missileDefend(missiles)) + '\n')
    fptr.close()
```

**Watch out.** Identical missiles (same time and frequency) are comparable, so one defence missile handles them all; the strict decrease (`bisect_left`) respects that. The rotation by 45° is the whole trick, because it turns the `|Δf| ≤ Δt` cone into a plain quadrant.

```stdin
4
1 1
2 3
3 1
5 1
```

```stdout
2
```
