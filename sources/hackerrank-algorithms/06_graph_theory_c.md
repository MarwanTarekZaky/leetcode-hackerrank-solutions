## Graph Theory

### Journey Scheduling

**Problem.** In a tree, Fedya starts at `V` and makes `K` moves, each time going to a city farthest from where he stands. Print the total distance for each of `M` journeys.

**Idea.** The farthest node from any vertex is an endpoint of a diameter. So the first move covers the eccentricity of `V`, which is `max(dist(V, a), dist(V, b))` for diameter endpoints `a` and `b`. After that he always stands on a diameter endpoint, so every later move covers exactly the diameter `D`. The tie-breaking rules don't change the lengths. Answer: `ecc(V) + (K − 1)·D`.

**Steps.**
1. BFS from node 1 to find `a`, the farthest node. BFS from `a` gives `b` and `distA`. BFS from `b` gives `distB`.
2. `D = distA[b]`. Each query is `max(distA[V], distB[V]) + (K − 1)·D`.

```python
import os
from collections import deque


def journeyScheduling(n, roads, journeys):
    adj = [[] for _ in range(n + 1)]
    for x, y in roads:
        adj[x].append(y)
        adj[y].append(x)

    def bfs(src):
        dist = [-1] * (n + 1)
        dist[src] = 0
        queue = deque([src])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if dist[v] < 0:
                    dist[v] = dist[u] + 1
                    queue.append(v)
        return dist

    d1 = bfs(1)
    a = max(range(1, n + 1), key=lambda v: d1[v])
    da = bfs(a)
    b = max(range(1, n + 1), key=lambda v: da[v])
    db = bfs(b)
    diameter = da[b]
    return [max(da[v], db[v]) + (k - 1) * diameter for v, k in journeys]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m = map(int, input().split())
    roads = [list(map(int, input().split())) for _ in range(n - 1)]
    journeys = [list(map(int, input().split())) for _ in range(m)]
    fptr.write('\n'.join(map(str, journeyScheduling(n, roads, journeys))) + '\n')
    fptr.close()
```

**Watch out.** `K` goes up to 10⁹, so simulating the moves is out of the question; the formula is O(1) per query. With a single city the diameter is 0 and every answer is 0.

```stdin
8 7
2 1
3 2
4 2
5 1
6 1
7 1
8 7
4 6
3 4
6 3
7 6
4 6
7 1
2 6
```

```stdout
24
16
11
23
24
3
23
```

### Matrix

**Problem.** In a weighted tree, some cities hold machines. Destroy roads (costing their weights) so that no two machines stay connected, at minimum total cost.

**Idea.** Reverse Kruskal: it is best to **keep** the most expensive roads. Process roads from heaviest to lightest. Keep a road (union its two components) unless both components already contain a machine; in that case it must be destroyed, so pay its cost. Each component tracks whether it has a machine.

**Steps.**
1. Sort roads by time, descending.
2. If both endpoints' components have a machine, add the time. Otherwise union them and OR the machine flags.

```python
import os


def minTime(roads, machines):
    n = max(max(a, b) for a, b, _ in roads) + 1
    parent = list(range(n))
    has = [False] * n
    for m in machines:
        has[m] = True

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    total = 0
    for a, b, t in sorted(roads, key=lambda r: -r[2]):
        ra, rb = find(a), find(b)
        if has[ra] and has[rb]:
            total += t
        else:
            parent[ra] = rb
            has[rb] = has[ra] or has[rb]
    return total


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    roads = [list(map(int, input().split())) for _ in range(n - 1)]
    machines = [int(input().strip()) for _ in range(k)]
    fptr.write(str(minTime(roads, machines)) + '\n')
    fptr.close()
```

**Watch out.** Cutting the lightest edge on each machine-to-machine path, one path at a time, double counts; the union-find order handles all paths at once. Cities are numbered from 0.

```stdin
5 3
2 1 8
1 0 5
2 4 5
1 3 4
2
4
0
```

```stdout
10
```

### Recording Episodes

**Problem.** Each episode airs twice (live and repeat), and one DVR records one airing at a time. Find the longest range `[L, R]` of consecutive episodes that can all be recorded, with the smallest `L` on ties.

**Idea.** For a fixed range, "can all be recorded" is **2-SAT**: variable `x_i` = record the live airing. For two airings of different episodes that overlap (touching endpoints count), add the clause "not both". If a range is feasible, so is any sub-range, so two pointers work: for each `L`, push `R` as far as 2-SAT allows. Never move `R` back.

**Steps.**
1. `ok(L, R)`: build the implication graph on the episodes in `[L, R]` and check with Tarjan's SCC that no `x` shares a component with `¬x`.
2. Two pointers over `L` with a non-decreasing `R`. Keep the best `R − L` and the first `L` that reaches it.

```python
import os


def overlap(a, b):
    return a[0] <= b[1] and b[0] <= a[1]


def satisfiable(ep, lo, hi):
    k = hi - lo + 1
    adj = [[] for _ in range(2 * k)]  # node 2i: episode i live, 2i+1: repeat
    for i in range(k):
        for j in range(i + 1, k):
            for a in range(2):
                for b in range(2):
                    if overlap(ep[lo + i][a], ep[lo + j][b]):
                        # not (i=a and j=b): i=a -> j=1-b, j=b -> i=1-a
                        adj[2 * i + a].append(2 * j + 1 - b)
                        adj[2 * j + b].append(2 * i + 1 - a)
    index, low, comp = [-1] * (2 * k), [0] * (2 * k), [-1] * (2 * k)
    stack, on, counter, c = [], [False] * (2 * k), 0, 0
    for root in range(2 * k):
        if index[root] >= 0:
            continue
        work = [(root, 0)]
        index[root] = low[root] = counter
        counter += 1
        stack.append(root)
        on[root] = True
        while work:
            u, i = work[-1]
            if i < len(adj[u]):
                work[-1] = (u, i + 1)
                v = adj[u][i]
                if index[v] < 0:
                    index[v] = low[v] = counter
                    counter += 1
                    stack.append(v)
                    on[v] = True
                    work.append((v, 0))
                elif on[v]:
                    low[u] = min(low[u], index[v])
            else:
                work.pop()
                if work:
                    low[work[-1][0]] = min(low[work[-1][0]], low[u])
                if low[u] == index[u]:
                    while True:
                        w = stack.pop()
                        on[w] = False
                        comp[w] = c
                        if w == u:
                            break
                    c += 1
    return all(comp[2 * i] != comp[2 * i + 1] for i in range(k))


def episodeRecording(episodes):
    ep = [((a, b), (c, d)) for a, b, c, d in episodes]
    n = len(ep)
    best, best_l, r = -1, 0, 0
    for l in range(n):
        r = max(r, l)
        while r + 1 < n and satisfiable(ep, l, r + 1):
            r += 1
        if r - l > best:
            best, best_l = r - l, l
    return [best_l + 1, best_l + 1 + best]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        n = int(input().strip())
        episodes = [list(map(int, input().split())) for _ in range(n)]
        fptr.write(' '.join(map(str, episodeRecording(episodes))) + '\n')
    fptr.close()
```

**Watch out.**
- **Touching airings.** They conflict: `[10, 20]` and `[20, 35]` cannot both be recorded. The first sample depends on it.
- **No clause within an episode.** An episode's own live and repeat airings get no clause, since only one of them is chosen anyway.
- **Recursion.** Tarjan is written iteratively here; the recursive version is shorter but risks recursion limits.

```stdin
3
3
10 20 30 40
20 35 21 35
14 30 35 50
1
10 20 30 40
3
11 19 31 39
12 38 13 37
10 20 30 40
```

```stdout
1 2
1 1
1 1
```

### Repair Roads

**Problem.** A robot repairs a sequence of roads in which consecutive roads share a city, never repeating a road. Find the minimum number of robots to repair every road of a tree. In other words: find a minimum path cover of the tree's *line graph*.

**Idea.** Tree DP over units. A unit is a parent edge `p = (u, parent)` plus everything below `u`.
- **Unit values.** For each unit compute `G` (cover only the edges below `u`), `A` (cover the unit with `p` at the end of a path, so the path can continue at the parent), `S = 1 + G` (`p` alone, so it can sit in the middle of a chain at the parent) and `B` (the best cover of the unit, any shape).
- **Runs at a vertex.** All edges at one vertex pairwise share it, so at a vertex, paths join in *runs* of edges. Every join saves one robot. A run can hold any number of "middle" units (state `S`) but only two "end" units (state `A`).
- **The key numbers.** Linking a child is never worse than leaving it alone, because `S − 1 = G ≤ B`. Using a child as an end instead of a middle saves one exactly when `A = S − 1`. Let `P` be the number of such children and `Base = Σ G_child`.
- **Formulas.** That gives `G = Base − ⌊P/2⌋`, or `Base + 1` when `P = 0`. Likewise `A = Base − ⌊(P−1)/2⌋`, also capped by `S`. A child with no siblings can't join anything at its vertex, so it contributes its own `B`.

**Steps.**
1. Root the tree at 0 and process the vertices in reverse BFS order.
2. A leaf gets `G = 0`, `A = S = B = 1`.
3. For an internal vertex with `d` children, compute `Base` and `P`. For `d = 1`, `G = B_child`; otherwise use the formula. Compute `A` and `S` from the formulas. `B = min(A, G-formula)` when `d ≥ 2`, else `B = A`.
4. The answer is `G` of the root (0 for a single city).

```python
import os
from collections import deque


def repairRoads(n, roads):
    if n <= 1:
        return 0
    adj = [[] for _ in range(n)]
    for a, b in roads:
        adj[a].append(b)
        adj[b].append(a)
    parent = [-1] * n
    order, seen = [], [False] * n
    seen[0] = True
    queue = deque([0])
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                parent[v] = u
                queue.append(v)
    G, A, S, B = [0] * n, [0] * n, [0] * n, [0] * n
    kids = [[] for _ in range(n)]
    for v in order[1:]:
        kids[parent[v]].append(v)
    for u in reversed(order):
        ch = kids[u]
        d = len(ch)
        if d == 0:
            G[u], A[u], S[u], B[u] = 0, 1, 1, 1
            continue
        base = sum(G[c] for c in ch)
        p = sum(1 for c in ch if A[c] == S[c] - 1)
        many = base + 1 if p == 0 else base - p // 2      # runs among children only
        G[u] = B[ch[0]] if d == 1 else many
        A[u] = base + 1 if p == 0 else base - (p - 1) // 2
        S[u] = 1 + G[u]
        A[u] = min(A[u], S[u])
        B[u] = min(A[u], many) if d >= 2 else A[u]
    return G[0]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n = int(input().strip())
        roads = [list(map(int, input().split())) for _ in range(n - 1)]
        fptr.write(str(repairRoads(n, roads)) + '\n')
    fptr.close()
```

**Watch out.**
- **Not tree paths.** A robot's route is not a simple path in the tree. It can fan around a vertex, as in `(v,a) → (v,b) → (v,c)`, so a star needs only one robot.
- **How this was checked.** The formulas were verified against an exhaustive path cover of the line graph on random small trees.

```stdin
3
4
0 1
0 2
0 3
6
0 1
1 2
2 3
2 4
4 5
7
0 1
1 2
2 3
2 4
4 5
3 6
```

```stdout
1
1
2
```

### Kth Ancestor

**Problem.** A rooted tree changes over time: leaves are added and removed. Answer queries for the `K`-th ancestor of `X` (0 if it doesn't exist or `X` isn't in the tree).

**Idea.** Binary lifting: `up[j][v]` is the `2^j`-th ancestor. A newly added leaf fills its own table from its parent's in O(log n). Removing a leaf only marks it absent, because nothing below a leaf refers to it. A query jumps by the set bits of `K`, after checking `depth[X] ≥ K`.

**Steps.**
1. Build the initial tree from the (unordered) `X Y` pairs and BFS from the root to fill depths and lifting tables.
2. `0 Y X`: set `depth[X] = depth[Y] + 1`, `up[0][X] = Y`, `up[j][X] = up[j−1][up[j−1][X]]`.
3. `1 X`: mark `X` absent. `2 X K`: print 0 if `X` is absent or `K > depth[X]`, else jump.

```python
import sys
from collections import deque

LOG = 17
SIZE = 100001


def main():
    data = sys.stdin.buffer.read().split()
    pos = 0
    t = int(data[pos]); pos += 1
    out = []
    for _ in range(t):
        p = int(data[pos]); pos += 1
        up = [[0] * SIZE for _ in range(LOG)]
        depth = [0] * SIZE
        present = [False] * SIZE
        children = {}
        root = 0
        for _ in range(p):
            x, y = int(data[pos]), int(data[pos + 1]); pos += 2
            present[x] = True
            if y == 0:
                root = x
            else:
                children.setdefault(y, []).append(x)
                up[0][x] = y
        queue = deque([root])
        while queue:
            u = queue.popleft()
            for j in range(1, LOG):
                up[j][u] = up[j - 1][up[j - 1][u]]
            for v in children.get(u, ()):
                depth[v] = depth[u] + 1
                queue.append(v)
        q = int(data[pos]); pos += 1
        for _ in range(q):
            kind = data[pos]
            if kind == b'0':
                y, x = int(data[pos + 1]), int(data[pos + 2]); pos += 3
                present[x] = True
                depth[x] = depth[y] + 1
                up[0][x] = y
                for j in range(1, LOG):
                    up[j][x] = up[j - 1][up[j - 1][x]]
            elif kind == b'1':
                present[int(data[pos + 1])] = False
                pos += 2
            else:
                x, k = int(data[pos + 1]), int(data[pos + 2]); pos += 3
                if x >= SIZE or not present[x] or k > depth[x]:
                    out.append('0')
                    continue
                j = 0
                while k:
                    if k & 1:
                        x = up[j][x]
                    k >>= 1
                    j += 1
                out.append(str(x))
    print('\n'.join(out))


main()
```

**Watch out.** In the input a child can appear before its parent, so collect everything first and then BFS from the root. A query on a node that never existed (or was removed) prints 0. Node labels go up to 10⁵, so the arrays are sized by label, not by `P`.

```stdin
2
7
2 0
5 2
3 5
7 5
9 8
8 2
6 8
10
0 5 15
2 15 2
1 3
0 15 20
0 20 13
2 13 4
2 13 3
2 6 10
2 11 1
2 9 1
1
10000 0
3
0 10000 4
1 4
2 4 1
```

```stdout
2
2
5
0
0
8
0
```

### ByteLandian Tours

**Problem.** New roads join every pair of cities at tree distance 2, so the graph becomes the tree's *square*. Count the closed tours from city 0 that visit every city exactly once, modulo 10⁹+7.

**Idea.** A classic result says the square of a tree has a Hamiltonian cycle only when the tree is a **caterpillar**: deleting all leaves leaves a simple path (the spine). Then the tour runs out along the spine and back. Each spine vertex's leaves can be visited in any order, which gives `c!` for a vertex with `c` leaves, and the two travel directions give a factor 2. When the spine is a single vertex (a star), the square is a complete graph and the count is just `c!`.

**Steps.**
1. If `n ≤ 2`, the answer is 1.
2. The spine is the set of non-leaf vertices. If any spine vertex has more than two spine neighbours, return 0.
3. Return `Π c_v!`, times 2 if the spine has at least two vertices.

```python
import os

MOD = 10 ** 9 + 7


def bytelandianTours(n, roads):
    if n <= 2:
        return 1
    adj = [[] for _ in range(n)]
    for a, b in roads:
        adj[a].append(b)
        adj[b].append(a)
    leaf = [len(adj[v]) == 1 for v in range(n)]
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = fact[i - 1] * i % MOD
    spine = [v for v in range(n) if not leaf[v]]
    ans = 1
    for v in spine:
        if sum(1 for u in adj[v] if not leaf[u]) > 2:
            return 0
        ans = ans * fact[sum(1 for u in adj[v] if leaf[u])] % MOD
    return ans * 2 % MOD if len(spine) >= 2 else ans


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n = int(input().strip())
        roads = [list(map(int, input().split())) for _ in range(n - 1)]
        fptr.write(str(bytelandianTours(n, roads)) + '\n')
    fptr.close()
```

**Watch out.** Spine vertices without leaves are fine; they contribute `0! = 1`. A "spider" (three long legs meeting at one vertex) is not a caterpillar, so its answer is 0. The formula was checked against an exhaustive Hamiltonian-cycle count on random small trees.

```stdin
2
3
0 1
1 2
5
0 1
1 2
2 3
2 4
```

```stdout
2
4
```

### Find the Path

**Problem.** In a grid with at most 7 rows and 5000 columns of non-negative cell weights, answer `q ≤ 3·10⁴` queries for the minimum-weight path between two cells (counting both endpoints).

**Idea.** Divide and conquer on columns. For a column range, take the middle column `mid`. Any path between cells on opposite sides of `mid` must pass through one of its at most 7 cells. Run Dijkstra (restricted to the range) from each of those cells. Then for **every** query inside the range, the best path through `mid` is `min over r of d_r(x) + d_r(y) − a[r][mid]`. Queries entirely left or right of `mid` also recurse into that half, because their best path may avoid `mid` completely.

**Steps.**
1. Start with the range `[0, m−1]` holding all queries, each with answer ∞.
2. For a range: run the Dijkstras from the mid column, improve every query, then pass the one-sided queries down to the matching half.
3. Use an explicit stack instead of recursion.

```python
import os
from heapq import heappop, heappush


def shortestPath(a, queries):
    n, m = len(a), len(a[0])
    ans = [float('inf')] * len(queries)
    work = [(0, m - 1, list(range(len(queries))))]
    while work:
        lo, hi, ids = work.pop()
        if not ids:
            continue
        mid = (lo + hi) // 2
        width = hi - lo + 1
        dists = []
        for r in range(n):
            dist = [float('inf')] * (n * width)
            start = (mid - lo) * n + r
            dist[start] = a[r][mid]
            heap = [(a[r][mid], start)]
            while heap:
                d, cell = heappop(heap)
                if d > dist[cell]:
                    continue
                c, rr = divmod(cell, n)
                for nr, nc in ((rr - 1, c), (rr + 1, c), (rr, c - 1), (rr, c + 1)):
                    if 0 <= nr < n and 0 <= nc < width:
                        nd = d + a[nr][nc + lo]
                        idx = nc * n + nr
                        if nd < dist[idx]:
                            dist[idx] = nd
                            heappush(heap, (nd, idx))
            dists.append(dist)
        left, right = [], []
        for i in ids:
            r1, c1, r2, c2 = queries[i]
            x, y = (c1 - lo) * n + r1, (c2 - lo) * n + r2
            for r in range(n):
                cand = dists[r][x] + dists[r][y] - a[r][mid]
                if cand < ans[i]:
                    ans[i] = cand
            if c1 < mid and c2 < mid:
                left.append(i)
            elif c1 > mid and c2 > mid:
                right.append(i)
        if lo < mid:
            work.append((lo, mid - 1, left))
        if mid < hi:
            work.append((mid + 1, hi, right))
    return ans


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m = map(int, input().split())
    a = [list(map(int, input().split())) for _ in range(n)]
    q = int(input().strip())
    queries = [list(map(int, input().split())) for _ in range(q)]
    fptr.write('\n'.join(map(str, shortestPath(a, queries))) + '\n')
    fptr.close()
```

**Watch out.** The mid cell is counted in both `d_r(x)` and `d_r(y)`, so subtract it once. Each level runs `n` Dijkstras over its whole range, about `n²·m·log m` in total; that is fine for C++ but slow in CPython, so use PyPy here.

```stdin
3 5
0 0 0 0 0
1 9 9 9 1
0 0 0 0 0
3
0 0 2 4
0 3 2 3
1 1 1 3
```

```stdout
1
1
18
```

### Savita And Friends

**Problem.** Choose a point on road `K = (A, B, C)` that minimises the largest shortest distance to any house. Print its distance from `A` and that largest distance, both with 5 decimals, preferring the point closest to `A` on ties.

**Idea.** At distance `x` from `A`, house `i` is at distance `min(dA_i + x, dB_i + C − x)`, where `dA` and `dB` come from Dijkstra. Its graph is a tent, and we need the lowest point of the upper envelope of all tents. Sort the houses by `dA` in descending order and track `maxB`, the largest `dB` among the houses processed so far. Each local minimum is where the rising line of some house `i` meets the falling line `maxB + C − x`, at `x = (maxB + C − dA_i) / 2`. Also check both ends, `x = 0` (value `max dA`) and `x = C` (value `max dB`).

**Steps.**
1. Run Dijkstra from `A` and from `B`.
2. Start with the candidates `(max dA, 0)` and `(max dB, C)`.
3. Walk the houses in decreasing `dA`. Before adding house `i` to `maxB`, try `x = (maxB + C − dA_i)/2` if it lies in `[0, C]`.
4. Take the candidate with the smallest `(value, x)`.

```python
import os
from heapq import heappop, heappush


def dijkstra(n, adj, src):
    dist = [float('inf')] * (n + 1)
    dist[src] = 0
    heap = [(0, src)]
    while heap:
        d, u = heappop(heap)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heappush(heap, (d + w, v))
    return dist


def solve(n, k, roads):
    adj = [[] for _ in range(n + 1)]
    for a, b, c in roads:
        adj[a].append((b, c))
        adj[b].append((a, c))
    A, B, C = roads[k - 1]
    da, db = dijkstra(n, adj, A), dijkstra(n, adj, B)
    best = min((max(da[1:]), 0), (max(db[1:]), C))
    max_b = None
    for i in sorted(range(1, n + 1), key=lambda v: -da[v]):
        if max_b is not None:
            x = (max_b + C - da[i]) / 2
            if 0 <= x <= C:
                best = min(best, (da[i] + x, x))
        max_b = db[i] if max_b is None else max(max_b, db[i])
    value, x = best
    return [f"{x:.5f}", f"{value:.5f}"]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n, m, k = map(int, input().split())
        roads = [list(map(int, input().split())) for _ in range(m)]
        fptr.write(' '.join(solve(n, k, roads)) + '\n')
    fptr.close()
```

**Watch out.** Keep `A` and `B` in input order: the first number is measured from `A`. All candidate values are multiples of 0.5, so floating point is exact here. At a candidate `x` the true envelope can only be lower than the candidate value, but the minimum candidate is always attained; a brute force over every pair of tents confirms this.

```stdin
2
2 1 1
1 2 10
4 4 1
1 2 10
2 3 10
3 4 1
4 1 5
```

```stdout
5.00000 5.00000
2.00000 8.00000
```

### Liars

**Problem.** Soldiers are liars or truthful, and each clue says how many liars are in a range. Find the minimum and maximum possible total number of liars.

**Idea.** Use prefix sums `S_i` (liars among the first `i` soldiers). Every rule becomes a difference constraint `S_v − S_u ≤ w`, which is an edge `u → v` of weight `w`:
- each soldier is 0 or 1, so `0 ≤ S_i − S_{i−1} ≤ 1`;
- each clue gives `S_B − S_{A−1} = C`, two inequalities.

The largest possible `S_N − S_0` is the shortest path from 0 to `N`. The smallest is minus the shortest path from `N` to 0. Bellman–Ford handles the negative edges, and with N ≤ 101 that is tiny.

**Steps.**
1. Add the edges `(i−1 → i, 1)`, `(i → i−1, 0)`, `(A−1 → B, C)` and `(B → A−1, −C)`.
2. `Lmax = dist(0 → N)` and `Lmin = −dist(N → 0)`.

```python
import os


def liars(n, sets):
    edges = []
    for i in range(1, n + 1):
        edges.append((i - 1, i, 1))
        edges.append((i, i - 1, 0))
    for a, b, c in sets:
        edges.append((a - 1, b, c))
        edges.append((b, a - 1, -c))

    def bellman(src):
        dist = [float('inf')] * (n + 1)
        dist[src] = 0
        for _ in range(n + 1):
            changed = False
            for u, v, w in edges:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    changed = True
            if not changed:
                break
        return dist

    return [-bellman(n)[0], bellman(0)[n]]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m = map(int, input().split())
    sets = [list(map(int, input().split())) for _ in range(m)]
    fptr.write(' '.join(map(str, liars(n, sets))) + '\n')
    fptr.close()
```

**Watch out.** It is easy to mix up the direction. `S_v ≤ S_u + w` is an edge from `u` to `v`, and the *shortest* path gives the *largest* feasible value. The data is guaranteed consistent, so there is no negative cycle.

```stdin
20 11
3 8 4
1 9 6
1 13 9
5 11 5
4 19 12
8 13 5
4 8 4
7 9 2
10 13 3
7 16 7
14 19 4
```

```stdout
13 14
```

### Jumping Rooks

**Problem.** Place `k` rooks on the free cells of an `n × n` board (`n ≤ 50`). Two rooks beat each other when they share a row or column with no blocked cell between them. Minimise the number of beating pairs.

**Idea.** Min-cost flow with convex costs.
- **Segments.** Split every row into maximal free horizontal segments, and every column into vertical segments. Two rooks beat each other exactly when they share a segment, so `t` rooks in one segment cost `C(t, 2)`. Each cell is the meeting point of one horizontal and one vertical segment, which makes each rook a unit of flow `source → h-segment → (cell) → v-segment → sink`.
- **Convex costs.** The `t`-th rook entering a segment adds `t − 1` new pairs, so the source → segment and segment → sink costs grow 0, 1, 2, …. Convex costs are exactly what successive shortest paths handles. Send `k` units, one Dijkstra (with Johnson potentials) per unit.
- **Costs as counters.** Each segment's cost is just its current rook count, not a stack of parallel edges.

**Steps.**
1. Label the segments and list the cells as `(h, v)` pairs.
2. Repeat `k` times: run Dijkstra over the residual graph. The edges are `S → h` (cost `used[h]`), `h → v` over unused cells (0), `v → h` over used cells (0, undoing a placement) and `v → T` (cost `used[v]`). Then augment and update the potentials.
3. Return `Σ C(used, 2)` over all segments.

```python
import os
from heapq import heappop, heappush


def jumpingRooks(k, board):
    n = len(board)
    hid = [[-1] * n for _ in range(n)]
    vid = [[-1] * n for _ in range(n)]
    H = V = 0
    for i in range(n):
        for j in range(n):
            if board[i][j] == '.':
                if j == 0 or board[i][j - 1] != '.':
                    H += 1
                hid[i][j] = H - 1
    for j in range(n):
        for i in range(n):
            if board[i][j] == '.':
                if i == 0 or board[i - 1][j] != '.':
                    V += 1
                vid[i][j] = V - 1
    cells = [(hid[i][j], vid[i][j]) for i in range(n) for j in range(n) if board[i][j] == '.']
    by_h = [[] for _ in range(H)]
    by_v = [[] for _ in range(V)]
    for c, (h, v) in enumerate(cells):
        by_h[h].append(c)
        by_v[v].append(c)
    size_h = [len(x) for x in by_h]
    size_v = [len(x) for x in by_v]
    used_h, used_v = [0] * H, [0] * V
    used = [False] * len(cells)
    # node ids: 0 = S, 1..H = h-segments, H+1..H+V = v-segments, H+V+1 = T
    T = H + V + 1
    pot = [0] * (T + 1)
    inf = float('inf')
    for _ in range(k):
        dist = [inf] * (T + 1)
        prev = [None] * (T + 1)
        dist[0] = 0
        heap = [(0, 0)]
        while heap:
            d, u = heappop(heap)
            if d > dist[u]:
                continue
            if u == 0:
                steps = [(1 + h, used_h[h], ('S', h)) for h in range(H) if used_h[h] < size_h[h]]
            elif u <= H:
                h = u - 1
                steps = [(1 + H + cells[c][1], 0, ('cell', c)) for c in by_h[h] if not used[c]]
            elif u < T:
                v = u - 1 - H
                steps = [(1 + cells[c][0], 0, ('back', c)) for c in by_v[v] if used[c]]
                if used_v[v] < size_v[v]:
                    steps.append((T, used_v[v], ('T', v)))
            else:
                continue
            for w, cost, how in steps:
                nd = d + cost + pot[u] - pot[w]
                if nd < dist[w]:
                    dist[w] = nd
                    prev[w] = (u, how)
                    heappush(heap, (nd, w))
        for x in range(T + 1):
            if dist[x] < inf:
                pot[x] += dist[x]
        x = T
        while x != 0:
            u, (kind, val) = prev[x]
            if kind == 'S':
                used_h[val] += 1
            elif kind == 'cell':
                used[val] = True
            elif kind == 'back':
                used[val] = False
            else:
                used_v[val] += 1
            x = u
    return sum(c * (c - 1) // 2 for c in used_h + used_v)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    board = [input() for _ in range(n)]
    fptr.write(str(jumpingRooks(k, board)) + '\n')
    fptr.close()
```

**Watch out.** Pairs are counted per segment, not per whole row; a blocked cell splits a row into independent parts. A plain greedy ("put the next rook where it adds the fewest pairs") can fail, because a later rook may want to move an earlier one; the `back` edges in the flow allow exactly that.

```stdin
5 10
..#..
..#..
#####
..#..
..#..
```

```stdout
4
```
