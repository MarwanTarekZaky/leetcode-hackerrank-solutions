## Graph Theory

### Frog in Maze

**Problem.** A frog walks randomly on a grid: each step it picks one of the non-wall neighbours with equal probability. A mine kills it, an exit frees it, and stepping onto a tunnel entrance teleports it to the other end. Print the probability that it escapes.

**Idea.** This is an absorbing Markov chain. Let `P[c]` be the escape probability when standing on free cell `c`. Then `P[c]` is the average over neighbours: an exit gives 1, a mine gives 0, and a free cell `w` gives `P[land(w)]`, where `land(w)` is the far end of a tunnel if `w` has one. That is one linear equation per free cell, at most 400 unknowns. Cells that can never reach an exit get `P = 0` up front. This also keeps the system non-singular, because a closed loop with no way out would otherwise have no unique solution.

**Steps.**
1. Number the free cells (`A` and `O`) and map each tunnel end to the other end.
2. For each free cell, add `1/deg` to the right-hand side for every exit neighbour, and `1/deg` to the coefficient of `land(w)` for every free neighbour `w`.
3. Walk the "lands on" edges backwards from cells next to an exit. Cells that are not reached have probability 0.
4. Solve `(I − C)·P = b` on the remaining cells with `numpy.linalg.solve` and print `P[start]`.

```python
import sys
from collections import deque

import numpy as np


def main():
    data = sys.stdin.read().split()
    n, m, k = int(data[0]), int(data[1]), int(data[2])
    grid = data[3:3 + n]
    nums = list(map(int, data[3 + n:3 + n + 4 * k]))
    tunnel = {}
    for t in range(k):
        i1, j1, i2, j2 = (x - 1 for x in nums[4 * t:4 * t + 4])
        tunnel[(i1, j1)] = (i2, j2)
        tunnel[(i2, j2)] = (i1, j1)

    cells = [(i, j) for i in range(n) for j in range(m) if grid[i][j] in 'AO']
    idx = {c: t for t, c in enumerate(cells)}
    coef = [dict() for _ in cells]
    rhs = [0.0] * len(cells)
    for t, (i, j) in enumerate(cells):
        nbrs = [(i + di, j + dj) for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1))
                if 0 <= i + di < n and 0 <= j + dj < m and grid[i + di][j + dj] != '#']
        for (a, b) in nbrs:
            p = 1.0 / len(nbrs)
            ch = grid[a][b]
            if ch == '%':
                rhs[t] += p
            elif ch in 'AO':
                land = idx[tunnel.get((a, b), (a, b))]
                coef[t][land] = coef[t].get(land, 0.0) + p

    # keep only cells that can reach an exit
    back = [[] for _ in cells]
    for t in range(len(cells)):
        for land in coef[t]:
            back[land].append(t)
    good = [rhs[t] > 0 for t in range(len(cells))]
    queue = deque(t for t in range(len(cells)) if good[t])
    while queue:
        u = queue.popleft()
        for v in back[u]:
            if not good[v]:
                good[v] = True
                queue.append(v)

    start = next(t for t, (i, j) in enumerate(cells) if grid[i][j] == 'A')
    if not good[start]:
        print(0.0)
        return
    keep = [t for t in range(len(cells)) if good[t]]
    pos = {t: r for r, t in enumerate(keep)}
    size = len(keep)
    a = np.eye(size)
    b = np.zeros(size)
    for r, t in enumerate(keep):
        b[r] = rhs[t]
        for land, p in coef[t].items():
            if good[land]:
                a[r, pos[land]] -= p
    print(np.linalg.solve(a, b)[pos[start]])


main()
```

**Watch out.** Leaving the "can never escape" cells in the system makes the matrix singular, because any constant solves a closed loop. A cell boxed in by walls (reachable only by tunnel) has no moves at all, so its probability is 0. The answer only needs to be within `1e-6`.

```stdin
3 6 1
###*OO
O#OA%O
###*OO
2 3 2 1
```

```check
assert abs(float(output.split()[0]) - 0.25) < 1e-6, output
```

### Roads and Libraries

**Problem.** Every city must reach a library. You can build a library in any city (`c_lib`) or repair a given road (`c_road`). Find the minimum cost.

**Idea.** If a library is no more expensive than a road, build one in every city. Otherwise each connected component needs exactly one library plus a spanning tree of `size − 1` roads. So the total is `components·c_lib + (n − components)·c_road`.

**Steps.**
1. If `c_lib <= c_road`, return `n * c_lib`.
2. Count components with union-find over the roads.
3. Return `comps * c_lib + (n - comps) * c_road`.

```python
import os


def roadsAndLibraries(n, c_lib, c_road, cities):
    if c_lib <= c_road:
        return n * c_lib
    parent = list(range(n + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    comps = n
    for a, b in cities:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            comps -= 1
    return comps * c_lib + (n - comps) * c_road


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        n, m, c_lib, c_road = map(int, input().split())
        cities = [list(map(int, input().split())) for _ in range(m)]
        fptr.write(str(roadsAndLibraries(n, c_lib, c_road, cities)) + '\n')
    fptr.close()
```

**Watch out.** A recursive DFS over 10⁵ cities overflows Python's stack. Union-find avoids recursion. The answer can exceed 32 bits in other languages.

```stdin
2
3 3 2 1
1 2
3 1
2 3
6 6 2 5
1 3
3 4
2 4
1 2
2 3
5 6
```

```stdout
4
12
```

### Journey to the Moon

**Problem.** Pairs of astronauts from the same country are given. Count the pairs of astronauts from different countries.

**Idea.** Countries are the connected components. Count all pairs, `n(n−1)/2`, then subtract the same-country pairs, `s(s−1)/2` for each component of size `s`.

**Steps.**
1. Union the given pairs and collect component sizes.
2. Return `n(n−1)/2 − Σ s(s−1)/2`.

```python
import os
from collections import Counter


def journeyToMoon(n, astronaut):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in astronaut:
        parent[find(a)] = find(b)
    sizes = Counter(find(x) for x in range(n)).values()
    return n * (n - 1) // 2 - sum(s * (s - 1) // 2 for s in sizes)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, p = map(int, input().split())
    astronaut = [list(map(int, input().split())) for _ in range(p)]
    fptr.write(str(journeyToMoon(n, astronaut)) + '\n')
    fptr.close()
```

**Watch out.** Astronauts that appear in no pair are countries of size 1 and must still be counted. Multiplying sizes pairwise in a double loop is O(c²), so use the complement formula.

```stdin
5 3
0 1
2 3
0 4
```

```stdout
6
```

### Synchronous Shopping

**Problem.** Two cats start at center 1 and must end at center `n`, together buying all `k ≤ 10` fish types along their routes. Minimise the time when the later cat arrives.

**Idea.** Run Dijkstra on states `(center, set of fish bought)`: there are at most 1000·1024 of them. Then `dist[n][mask]` is the fastest single trip that ends at `n` holding `mask`. Two cats are just two such trips whose masks together cover every type, so take the minimum of `max(d1, d2)` over all pairs with `m1 | m2 == full`.

**Steps.**
1. Store each center's fish as a bitmask.
2. Run Dijkstra from `(1, fish[1])`. Moving to `v` ORs in `fish[v]`.
3. Over all reachable masks at `n`, return the minimum `max(d1, d2)` with `m1 | m2 == full`.

```python
import os
from heapq import heappop, heappush


def shop(n, k, centers, roads):
    fish = [0] * (n + 1)
    for i, line in enumerate(centers, 1):
        for f in list(map(int, line.split()))[1:]:
            fish[i] |= 1 << (f - 1)
    adj = [[] for _ in range(n + 1)]
    for u, v, w in roads:
        adj[u].append((v, w))
        adj[v].append((u, w))
    full = (1 << k) - 1
    inf = float('inf')
    dist = [[inf] * (full + 1) for _ in range(n + 1)]
    dist[1][fish[1]] = 0
    heap = [(0, 1, fish[1])]
    while heap:
        d, u, mask = heappop(heap)
        if d > dist[u][mask]:
            continue
        for v, w in adj[u]:
            nm = mask | fish[v]
            if d + w < dist[v][nm]:
                dist[v][nm] = d + w
                heappush(heap, (d + w, v, nm))
    reach = [(d, m) for m, d in enumerate(dist[n]) if d < inf]
    return min(max(d1, d2) for d1, m1 in reach for d2, m2 in reach if m1 | m2 == full)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m, k = map(int, input().split())
    centers = [input() for _ in range(n)]
    roads = [list(map(int, input().split())) for _ in range(m)]
    fptr.write(str(shop(n, k, centers, roads)) + '\n')
    fptr.close()
```

**Watch out.** Don't forget the fish at center 1 itself. One cat can do all the shopping alone (the other's mask is then anything, even the same path), and pairing a mask with itself handles that.

```stdin
5 5 5
1 1
1 2
1 3
1 4
1 5
1 2 10
1 3 10
2 4 10
3 5 10
4 5 10
```

```stdout
30
```

### Subset Component

**Problem.** Each number `d[k]` connects all of its set bits in a 64-vertex graph. Sum the number of connected components over every subset of `d` (including the empty one), with `n ≤ 20`.

**Idea.** 2²⁰ subsets is small enough to enumerate. Build them recursively and keep the components as disjoint bitmasks of size ≥ 2. Adding a number with two or more bits merges it with every component it touches; one pass suffices because components are disjoint. A component of size `s` reduces the count by `s − 1`, so the count is `64 − Σ(s − 1)`.

**Steps.**
1. Recurse over the elements: skip it, or include it.
2. Including a number with ≤ 1 set bit changes nothing. Otherwise OR it with every overlapping component and keep the rest.
3. At each leaf add `64 − merged`, where `merged = Σ(popcount − 1)`.

```python
import os


def findConnectedComponents(d):
    n = len(d)
    total = 0

    def go(i, comps, merged):
        nonlocal total
        if i == n:
            total += 64 - merged
            return
        go(i + 1, comps, merged)
        x = d[i]
        if x & (x - 1) == 0:          # zero or one bit: no edges
            go(i + 1, comps, merged)
            return
        joined, rest = x, []
        for c in comps:
            if c & joined:
                joined |= c
            else:
                rest.append(c)
        rest.append(joined)
        go(i + 1, rest, sum(bin(c).count('1') - 1 for c in rest))

    go(0, [], 0)
    return total


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    d_count = int(input().strip())
    d = list(map(int, input().split()))
    fptr.write(str(findConnectedComponents(d)) + '\n')
    fptr.close()
```

**Watch out.** The empty subset counts too (64 components); that is what makes the sample 504. A value like `0` or a power of two adds no edges, but its subsets still count.

```stdin
3
2 5 9
```

```stdout
504
```

### Breadth First Search: Shortest Reach

**Problem.** In an unweighted graph where every edge has length 6, print the distance from `s` to every other node (`-1` if unreachable).

**Idea.** All edges have the same length, so plain BFS gives shortest paths. Each layer adds 6.

**Steps.**
1. BFS from `s`, setting `dist[v] = dist[u] + 6` on first visit.
2. Return the distances of all nodes except `s`, in order.

```python
import os
from collections import deque


def bfs(n, m, edges, s):
    adj = [[] for _ in range(n + 1)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    dist = [-1] * (n + 1)
    dist[s] = 0
    queue = deque([s])
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 6
                queue.append(v)
    return [dist[i] for i in range(1, n + 1) if i != s]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        n, m = map(int, input().split())
        edges = [list(map(int, input().split())) for _ in range(m)]
        s = int(input().strip())
        fptr.write(' '.join(map(str, bfs(n, m, edges, s))) + '\n')
    fptr.close()
```

**Watch out.** Skip the start node in the output, but keep the others in node order. Duplicate edges are harmless in BFS.

```stdin
2
4 2
1 2
1 3
1
3 1
2 3
2
```

```stdout
6 6 -1
-1 6
```

### Kruskal (MST): Really Special Subtree

**Problem.** Print the weight of the minimum spanning tree, built with Kruskal's algorithm.

**Idea.** Sort edges by weight (ties by `u + v + w`, as the statement asks) and add each edge that joins two different components. Union-find answers "same component?" in near-constant time. The MST weight is the same whatever the tie order, but following the rule costs nothing.

**Steps.**
1. Sort edges by `(w, u + v + w)`.
2. For each edge, if `find(u) != find(v)`, union them and add `w`.

```python
import os


def kruskals(g_nodes, g_from, g_to, g_weight):
    parent = list(range(g_nodes + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    total = 0
    for w, _, u, v in sorted((w, u + v + w, u, v) for u, v, w in zip(g_from, g_to, g_weight)):
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            total += w
    return total


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    g_nodes, g_edges = map(int, input().split())
    g_from, g_to, g_weight = [0] * g_edges, [0] * g_edges, [0] * g_edges
    for i in range(g_edges):
        g_from[i], g_to[i], g_weight[i] = map(int, input().split())
    res = kruskals(g_nodes, g_from, g_to, g_weight)
    fptr.write(str(res) + '\n')
    fptr.close()
```

**Watch out.** HackerRank's Python starter computes `res` but never writes it, so add the `fptr.write` yourself. Parallel edges between the same pair are allowed and simply compete like any other edge.

```stdin
4 6
1 2 5
1 3 3
4 1 6
2 4 7
3 2 4
3 4 5
```

```stdout
12
```

### Even Tree

**Problem.** Remove as many edges as possible from a tree (with an even number of nodes) so that every remaining component has an even number of nodes.

**Idea.** The edge above node `v` can be cut exactly when `v`'s subtree has an even size: the subtree becomes an even component, and the rest stays even because even minus even is even. Cuts are independent, so count all non-root nodes with an even subtree size.

**Steps.**
1. Root the tree at 1 and get a DFS order.
2. Accumulate subtree sizes in reverse order.
3. Count nodes `v ≠ 1` with `size[v] % 2 == 0`.

```python
import os


def evenForest(t_nodes, t_edges, t_from, t_to):
    adj = [[] for _ in range(t_nodes + 1)]
    for a, b in zip(t_from, t_to):
        adj[a].append(b)
        adj[b].append(a)
    parent = [0] * (t_nodes + 1)
    order, stack, seen = [], [1], [False] * (t_nodes + 1)
    seen[1] = True
    while stack:
        u = stack.pop()
        order.append(u)
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                parent[v] = u
                stack.append(v)
    size = [1] * (t_nodes + 1)
    for u in reversed(order[1:]):
        size[parent[u]] += size[u]
    return sum(1 for v in range(2, t_nodes + 1) if size[v] % 2 == 0)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t_nodes, t_edges = map(int, input().split())
    t_from, t_to = [0] * t_edges, [0] * t_edges
    for i in range(t_edges):
        t_from[i], t_to[i] = map(int, input().split())
    fptr.write(str(evenForest(t_nodes, t_edges, t_from, t_to)) + '\n')
    fptr.close()
```

**Watch out.** Don't count the root: it has no edge above it. Edges may be listed child-first or parent-first, so build an undirected adjacency list.

```stdin
10 9
2 1
3 1
4 3
5 2
6 1
7 2
8 6
9 8
10 8
```

```stdout
2
```

### Snakes and Ladders: The Quickest Way Up

**Problem.** On a 100-square board with ladders and snakes, find the fewest die rolls (1 to 6 each) to get from square 1 to 100, or `-1`.

**Idea.** Each square is a node, and each roll is an unweighted edge to `sq + d`, redirected through a snake or ladder if one starts there. BFS gives the minimum number of rolls.

**Steps.**
1. Put all snakes and ladders in one `jump` map.
2. BFS from 1. For each `d` in 1..6 with `sq + d ≤ 100`, go to `jump.get(sq + d, sq + d)`.
3. Return `dist[100]`.

```python
import os
from collections import deque


def quickestWayUp(ladders, snakes):
    jump = {a: b for a, b in ladders + snakes}
    dist = [-1] * 101
    dist[1] = 0
    queue = deque([1])
    while queue:
        sq = queue.popleft()
        for d in range(1, 7):
            nxt = sq + d
            if nxt > 100:
                break
            nxt = jump.get(nxt, nxt)
            if dist[nxt] < 0:
                dist[nxt] = dist[sq] + 1
                queue.append(nxt)
    return dist[100]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n = int(input().strip())
        ladders = [list(map(int, input().split())) for _ in range(n)]
        m = int(input().strip())
        snakes = [list(map(int, input().split())) for _ in range(m)]
        fptr.write(str(quickestWayUp(ladders, snakes)) + '\n')
    fptr.close()
```

**Watch out.** A roll that overshoots 100 is not allowed. You never "stand" on the bottom of a ladder or the head of a snake, so only the redirected square is a BFS node.

```stdin
2
3
32 62
42 68
12 98
7
95 13
97 25
93 37
79 27
75 19
49 47
67 17
4
8 52
6 80
26 42
2 72
9
51 19
39 11
37 29
81 3
59 5
79 23
53 7
43 33
77 21
```

```stdout
3
5
```

### Dijkstra: Shortest Reach 2

**Problem.** Print the shortest distance from `s` to every other node in an undirected weighted graph (`-1` if unreachable).

**Idea.** Dijkstra with a binary heap: always settle the closest unsettled node, then relax its edges. Skip stale heap entries instead of decreasing keys.

**Steps.**
1. Build the adjacency list (parallel edges are fine).
2. Pop `(d, u)`; skip it if `d > dist[u]`; otherwise relax every edge.
3. Output the distances for all nodes but `s`, replacing infinity with -1.

```python
import os
from heapq import heappop, heappush


def shortestReach(n, edges, s):
    adj = [[] for _ in range(n + 1)]
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    inf = float('inf')
    dist = [inf] * (n + 1)
    dist[s] = 0
    heap = [(0, s)]
    while heap:
        d, u = heappop(heap)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heappush(heap, (d + w, v))
    return [dist[i] if dist[i] < inf else -1 for i in range(1, n + 1) if i != s]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n, m = map(int, input().split())
        edges = [list(map(int, input().split())) for _ in range(m)]
        s = int(input().strip())
        fptr.write(' '.join(map(str, shortestReach(n, edges, s))) + '\n')
    fptr.close()
```

**Watch out.** With up to ~10⁶ edge lines, `input()` per line is the bottleneck; reading everything via `sys.stdin.buffer` is faster if you time out. Keep the cheaper of parallel edges by just adding all of them.

```stdin
1
4 4
1 2 24
1 4 20
3 1 3
4 3 12
1
```

```stdout
24 3 15
```

### The Story of a Tree

**Problem.** Bob roots a tree at a uniformly random node. Alice made guesses "`u` is the parent of `v`". Print, as a reduced fraction, the probability that at least `k` guesses are correct.

**Idea.** Rerooting. Count the correct guesses for root 1 directly. Moving the root from `u` to its child `v` changes only the edge `u–v`: guess `(u, v)` stops being true and guess `(v, u)` becomes true. So every root's score follows from its parent's in O(1), and the answer is `wins / n`.

**Steps.**
1. Put the guesses in a set of `(u, v)` pairs.
2. BFS from 1 to get parents and an order; `score[1]` counts the guesses `(parent[v], v)`.
3. In BFS order, `score[v] = score[p] − [(p, v) guessed] + [(v, p) guessed]`.
4. Reduce `wins / n` with `gcd`.

```python
import sys
from collections import deque
from math import gcd


def solve(n, edges, k, guesses):
    adj = [[] for _ in range(n + 1)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    parent = [0] * (n + 1)
    order, seen = [], [False] * (n + 1)
    seen[1] = True
    queue = deque([1])
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                parent[v] = u
                queue.append(v)
    score = [0] * (n + 1)
    score[1] = sum(1 for v in order[1:] if (parent[v], v) in guesses)
    for v in order[1:]:
        p = parent[v]
        score[v] = score[p] - ((p, v) in guesses) + ((v, p) in guesses)
    wins = sum(1 for v in range(1, n + 1) if score[v] >= k)
    g = gcd(wins, n)
    return f"{wins // g}/{n // g}"


def main():
    data = sys.stdin.buffer.read().split()
    pos = 0
    q = int(data[pos]); pos += 1
    out = []
    for _ in range(q):
        n = int(data[pos]); pos += 1
        edges = []
        for _ in range(n - 1):
            edges.append((int(data[pos]), int(data[pos + 1]))); pos += 2
        g, k = int(data[pos]), int(data[pos + 1]); pos += 2
        guesses = set()
        for _ in range(g):
            guesses.add((int(data[pos]), int(data[pos + 1]))); pos += 2
        out.append(solve(n, edges, k, guesses))
    print('\n'.join(out))


main()
```

**Watch out.** HackerRank's Python starter reads the guesses with `for _ in range(q)` (the number of games) instead of `g`, so it breaks on most inputs; parse the input yourself. `gcd(0, n) = n` turns 0 wins into `0/1`, as required.

```stdin
2
4
1 2
1 3
3 4
2 2
1 2
3 4
3
1 2
1 3
2 2
1 2
1 3
```

```stdout
1/2
1/3
```

### Prim's (MST) : Special Subtree

**Problem.** Print the weight of the minimum spanning tree, grown with Prim's algorithm from `start`.

**Idea.** Keep a heap of edges leaving the tree. Repeatedly take the cheapest one whose far end is not yet in the tree, add that node, and push its edges.

**Steps.**
1. Push `(0, start)`.
2. Pop `(w, v)`; skip `v` if it is already in the tree, otherwise add `w`, mark `v` and push all of `v`'s edges.

```python
import os
from heapq import heappop, heappush


def prims(n, edges, start):
    adj = [[] for _ in range(n + 1)]
    for u, v, w in edges:
        adj[u].append((w, v))
        adj[v].append((w, u))
    used = [False] * (n + 1)
    heap = [(0, start)]
    total = 0
    while heap:
        w, v = heappop(heap)
        if used[v]:
            continue
        used[v] = True
        total += w
        for edge in adj[v]:
            if not used[edge[1]]:
                heappush(heap, edge)
    return total


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m = map(int, input().split())
    edges = [list(map(int, input().split())) for _ in range(m)]
    start = int(input().strip())
    fptr.write(str(prims(n, edges, start)) + '\n')
    fptr.close()
```

**Watch out.** Mark a node when it is popped, not when it is pushed: a node can be pushed several times with different weights, and only the first pop is the cheapest.

```stdin
5 6
1 2 3
1 3 4
4 2 6
5 2 2
2 3 5
3 5 7
1
```

```stdout
15
```

### Toll Cost Digits

**Problem.** A road costs `r` one way and `1000 − r` the other way, and roads may be reused freely. For each digit `d`, count the ordered pairs `(x, y)`, `x ≠ y`, that have some path whose total cost ends in `d`.

**Idea.** Only costs mod 10 matter, and reversing an edge negates its cost mod 10. Give every node a potential `pot` from a BFS tree, so the tree path from `x` to `y` costs `pot[y] − pot[x]`. Each non-tree edge closes a cycle with value `pot[u] + w − pot[v]`. Walking any cycle (and back) adds that value, so the reachable residues from `x` to `y` are `pot[y] − pot[x] + multiples of g`, where `g = gcd(10, all cycle values)`. So count pairs by `pot mod g`.

**Steps.**
1. For each component, BFS to assign potentials mod 10 and fold every cycle value into `g` (starting from 10).
2. Count the nodes per `pot mod g`. For each residue `r` mod `g`, `pairs = Σ cnt[a]·cnt[a + r]` (minus the component size when `r = 0`, removing `x = y`).
3. Add `pairs` to every digit `d ≡ r (mod g)`.

```python
import sys
from math import gcd


def main():
    data = sys.stdin.buffer.read().split()
    n, e = int(data[0]), int(data[1])
    adj = [[] for _ in range(n + 1)]
    for i in range(e):
        x, y, r = int(data[2 + 3 * i]), int(data[3 + 3 * i]), int(data[4 + 3 * i]) % 10
        adj[x].append((y, r))
        adj[y].append((x, (10 - r) % 10))
    pot = [-1] * (n + 1)
    ans = [0] * 10
    for s in range(1, n + 1):
        if pot[s] >= 0:
            continue
        pot[s] = 0
        comp, stack, g = [s], [s], 10
        while stack:
            u = stack.pop()
            for v, w in adj[u]:
                if pot[v] < 0:
                    pot[v] = (pot[u] + w) % 10
                    comp.append(v)
                    stack.append(v)
                else:
                    g = gcd(g, (pot[u] + w - pot[v]) % 10)
        cnt = [0] * g
        for v in comp:
            cnt[pot[v] % g] += 1
        for r in range(g):
            pairs = sum(cnt[a] * cnt[(a + r) % g] for a in range(g))
            if r == 0:
                pairs -= len(comp)
            for d in range(r, 10, g):
                ans[d] += pairs
    print('\n'.join(map(str, ans)))


main()
```

**Watch out.** Enumerating actual paths is hopeless, because roads can be reused forever; the gcd of the cycle values captures every possible detour. Going along an edge and straight back costs `r + 1000 − r ≡ 0`, so it never shrinks `g` by itself.

```stdin
3 3
1 3 602
1 2 256
2 3 411
```

```stdout
0
2
1
1
2
0
2
1
1
2
```

### Real Estate Broker

**Problem.** Client `i` wants a house with area strictly greater than `a_i` and price at most `p_i`. Each house goes to at most one client. Maximise the number of houses sold.

**Idea.** Greedy matching. Serve clients from the largest area requirement down: houses that satisfy a strict client satisfy every later one too, so the pool of available houses only grows. Each client takes the most expensive available house they can afford. That leaves cheaper houses for later clients, and any later client who could use the taken house could also use a cheaper one, so nothing is lost.

**Steps.**
1. Sort clients by `a` descending and houses by area descending.
2. For each client, move every house with area `> a` into a sorted price list.
3. Take the largest price `≤ p` (with `bisect`), if there is one, and count a sale.

```python
import os
from bisect import bisect_right, insort


def realEstateBroker(clients, houses):
    clients = sorted(clients, key=lambda c: -c[0])
    houses = sorted(houses, key=lambda h: -h[0])
    prices, i, sold = [], 0, 0
    for a, p in clients:
        while i < len(houses) and houses[i][0] > a:
            insort(prices, houses[i][1])
            i += 1
        j = bisect_right(prices, p) - 1
        if j >= 0:
            prices.pop(j)
            sold += 1
    return sold


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m = map(int, input().split())
    clients = [list(map(int, input().split())) for _ in range(n)]
    houses = [list(map(int, input().split())) for _ in range(m)]
    fptr.write(str(realEstateBroker(clients, houses)) + '\n')
    fptr.close()
```

**Watch out.** The area condition is strict (`>`), the price condition is not (`≤`). HackerRank's starter passes a misspelled `clents`, which raises `NameError`. A general bipartite matching also works but is far slower here.

```stdin
3 3
5 110
9 500
20 400
10 100
2 200
30 300
```

```stdout
2
```

### Clique

**Problem.** Given `n` nodes and `m` edges, find the smallest possible size of the largest clique over all such graphs.

**Idea.** Turán's theorem: the most edges a graph can have without a clique of size `r + 1` is achieved by splitting the nodes into `r` nearly equal groups and joining every pair from different groups. So the answer is the smallest `r` whose Turán graph has at least `m` edges. That count grows with `r`, so binary search.

**Steps.**
1. `turan(r)`: with `q, rem = divmod(n, r)`, the edges are `(n² − rem·(q+1)² − (r−rem)·q²) / 2`.
2. Binary search the smallest `r` in `[1, n]` with `turan(r) ≥ m`.

```python
import os


def clique(n, m):
    def turan(r):
        q, rem = divmod(n, r)
        return (n * n - rem * (q + 1) ** 2 - (r - rem) * q * q) // 2

    lo, hi = 1, n
    while lo < hi:
        mid = (lo + hi) // 2
        if turan(mid) >= m:
            hi = mid
        else:
            lo = mid + 1
    return lo


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n, m = map(int, input().split())
        fptr.write(str(clique(n, m)) + '\n')
    fptr.close()
```

**Watch out.** If `turan(r) ≥ m`, you can drop edges from the Turán graph to get exactly `m` edges with no clique larger than `r`. If `turan(r − 1) < m`, every graph with `m` edges contains a clique of size `r`. Those two facts are why the search is exact.

```stdin
3
3 2
4 6
5 7
```

```stdout
2
4
3
```

### Minimum Penalty Path

**Problem.** The penalty of a path is the bitwise OR of its edge costs (each `< 1024`). Find the minimum penalty from `A` to `B`, or `-1`.

**Idea.** Decide the answer bit by bit from the highest. Start with every bit allowed. For bit 9 down to 0, try forbidding it: if `A` and `B` are still connected using only edges whose cost fits inside the allowed mask, forbid it for good. A higher bit outweighs all lower bits together, so this greedy gives the minimum. Each test is one union-find pass.

**Steps.**
1. If `A` and `B` are not connected with mask 1023, return -1.
2. For `b` from 9 to 0: if they are connected with `mask & ~(1 << b)`, clear that bit.
3. Return `mask`.

```python
import os


def beautifulPath(edges, A, B):
    n = max(max(u, v) for u, v, _ in edges + [[A, B, 0]])

    def connected(mask):
        parent = list(range(n + 1))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for u, v, c in edges:
            if c | mask == mask:
                parent[find(u)] = find(v)
        return find(A) == find(B)

    mask = 1023
    if not connected(mask):
        return -1
    for b in range(9, -1, -1):
        if connected(mask & ~(1 << b)):
            mask &= ~(1 << b)
    return mask


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m = map(int, input().split())
    edges = [list(map(int, input().split())) for _ in range(m)]
    A, B = map(int, input().split())
    fptr.write(str(beautifulPath(edges, A, B)) + '\n')
    fptr.close()
```

**Watch out.** Dijkstra on the OR is wrong: OR is not additive, so a path that is cheaper so far can end up worse. The bit greedy works because the final mask is exactly some path's penalty: every remaining bit failed its removal test.

```stdin
3 4
1 2 1
1 2 1000
2 3 3
1 3 100
1 3
```

```stdout
3
```

### Demanding Money

**Problem.** Pick a set of houses with no road between any two picked houses (an independent set) to maximise the money collected, with `N ≤ 34`. Also count how many different sets reach that maximum.

**Idea.** Maximum-weight independent set by branching with memoisation on the bitmask of remaining houses. Take the house `v` with the most neighbours left: either skip it, or take it and delete its neighbours. When nothing is connected any more, every house is free: take all of them, and each 0-money house doubles the count because taking it or not gives the same total. Branching on a high-degree vertex removes many houses at once, which keeps the search small.

**Steps.**
1. Store neighbour bitmasks.
2. `solve(mask)` returns `(best, ways)`; the base cases are the empty mask and "no edges left".
3. Combine the two branches: keep the larger `best`; if they tie, add the `ways`.

```python
import os


def demandingMoney(money, roads):
    n = len(money)
    nb = [0] * n
    for a, b in roads:
        nb[a - 1] |= 1 << (b - 1)
        nb[b - 1] |= 1 << (a - 1)
    memo = {}

    def solve(mask):
        if mask in memo:
            return memo[mask]
        best_v, best_deg, m = -1, -1, mask
        while m:
            low = m & -m
            v = low.bit_length() - 1
            m ^= low
            deg = bin(nb[v] & mask).count('1')
            if deg > best_deg:
                best_v, best_deg = v, deg
        if best_deg <= 0:
            total, ways, m = 0, 1, mask
            while m:
                low = m & -m
                v = low.bit_length() - 1
                m ^= low
                total += money[v]
                if money[v] == 0:
                    ways *= 2
            res = (total, ways)
        else:
            v = best_v
            skip = solve(mask & ~(1 << v))
            t = solve(mask & ~(1 << v) & ~nb[v])
            take = (t[0] + money[v], t[1])
            if skip[0] != take[0]:
                res = max(skip, take)
            else:
                res = (skip[0], skip[1] + take[1])
        memo[mask] = res
        return res

    return list(solve((1 << n) - 1))


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m = map(int, input().split())
    money = list(map(int, input().split()))
    roads = [list(map(int, input().split())) for _ in range(m)]
    fptr.write(' '.join(map(str, demandingMoney(money, roads))) + '\n')
    fptr.close()
```

**Watch out.** Houses with 0 money matter for the count: visiting one or not gives a different set with the same total. The empty set is a valid way too, which makes the all-zero answer `0 2^N`.

```stdin
3 2
6 8 2
1 2
3 2
```

```stdout
8 2
```

### The Value of Friendship

**Problem.** Friendships are added one at a time, and friendship is transitive. After each addition, `total` grows by the sum over all students of their friend counts. Find the maximum possible `total` over all orders of the given edges.

**Idea.** A component of size `s` contributes `s(s−1)` to the sum. Grow the biggest component first: add its `s − 1` spanning-tree edges one by one, where after the `k`-th one its contribution is `k(k+1)`, on top of the components already finished. Then the next biggest, and so on. Save every redundant (cycle) edge for the very end, when each one adds the full final sum.

**Steps.**
1. Find the component sizes with union-find and sort them in descending order.
2. For each size `s`: `total += base·(s−1) + (s−1)s(s+1)/3`, then `base += s(s−1)`.
3. `total += (m − Σ(s−1)) · base` for the redundant edges.

```python
import os
from collections import Counter


def valueOfFriendsship(n, friendships):
    parent = list(range(n + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in friendships:
        parent[find(a)] = find(b)
    sizes = sorted((s for s in Counter(find(x) for x in range(1, n + 1)).values() if s > 1),
                   reverse=True)
    total = base = 0
    for s in sizes:
        total += base * (s - 1) + (s - 1) * s * (s + 1) // 3
        base += s * (s - 1)
    total += (len(friendships) - sum(s - 1 for s in sizes)) * base
    return total


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        n, m = map(int, input().split())
        friendships = [list(map(int, input().split())) for _ in range(m)]
        fptr.write(str(valueOfFriendsship(n, friendships)) + '\n')
    fptr.close()
```

**Watch out.** The sum `Σ_{k=1}^{s−1} k(k+1)` equals `(s−1)s(s+1)/3`. Building small components first, or adding cycle edges early, loses value. The values reach ~10¹⁶, fine in Python.

```stdin
1
5 4
1 2
3 2
4 2
4 3
```

```stdout
32
```

### Coprime Paths

**Problem.** In a tree with `n, q ≤ 25 000` and node values `≤ 10⁷` (each with at most 3 prime factors), answer queries: how many unordered pairs of nodes on the path `u–v` have coprime values?

**Idea.** Mo's algorithm on trees plus inclusion–exclusion.
- **Coprime counting.** Keep `cnt[d]` = the number of nodes in the current set divisible by `d`, for every squarefree `d`. A new value `x` is coprime to `Σ μ(d)·cnt[d]` of them, summed over the at most 8 squarefree divisors `d` of `x`. So adding or removing a node costs O(8).
- **Paths as ranges.** In an Euler tour where each node appears at entry and exit, the path `u–v` is the set of nodes that appear exactly once in one contiguous range (plus the LCA when it isn't `u`).
- **Ordering.** Mo's ordering moves the range ends only O((n + q)√n) times in total.

**Steps.**
1. Factor each value by trial division over primes ≤ 3163. List its squarefree divisors with the sign `μ`.
2. Do a DFS to get `tin` / `tout` positions in a 2n-long tour, depths, and binary-lifting tables for LCA.
3. Map each query to a range: `[tin[u], tin[v]]` if `u` is the LCA, else `[tout[u], tin[v]]` plus the LCA.
4. Sort queries in Mo order and toggle nodes in and out as the range moves. Add the LCA's contribution without inserting it.

```python
import sys


def main():
    data = sys.stdin.buffer.read().split()
    n, q = int(data[0]), int(data[1])
    vals = list(map(int, data[2:2 + n]))
    pos = 2 + n
    sieve = bytearray([1]) * 3200
    primes = []
    for i in range(2, 3200):
        if sieve[i]:
            primes.append(i)
            sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
    ids = {}
    divs = []
    for x in vals:
        ps = []
        for p in primes:
            if p * p > x:
                break
            if x % p == 0:
                ps.append(p)
                while x % p == 0:
                    x //= p
        if x > 1:
            ps.append(x)
        lst = [(1, 1)]
        for p in ps:
            lst += [(d * p, -s) for d, s in lst]
        divs.append([(ids.setdefault(d, len(ids)), s) for d, s in lst])

    adj = [[] for _ in range(n)]
    for _ in range(n - 1):
        a, b = int(data[pos]) - 1, int(data[pos + 1]) - 1
        pos += 2
        adj[a].append(b)
        adj[b].append(a)
    LOG = max(1, n.bit_length())
    up = [[0] * n for _ in range(LOG)]
    depth, tin, tout = [0] * n, [0] * n, [0] * n
    euler, timer = [0] * (2 * n), 0
    stack, it = [0], [0] * n
    seen = [False] * n
    seen[0] = True
    tin[0], euler[0], timer = 0, 0, 1
    while stack:
        u = stack[-1]
        if it[u] < len(adj[u]):
            v = adj[u][it[u]]
            it[u] += 1
            if not seen[v]:
                seen[v] = True
                up[0][v], depth[v] = u, depth[u] + 1
                tin[v] = timer
                euler[timer] = v
                timer += 1
                stack.append(v)
        else:
            tout[u] = timer
            euler[timer] = u
            timer += 1
            stack.pop()
    for j in range(1, LOG):
        prev, cur = up[j - 1], up[j]
        for v in range(n):
            cur[v] = prev[prev[v]]

    def lca(a, b):
        if depth[a] < depth[b]:
            a, b = b, a
        diff = depth[a] - depth[b]
        j = 0
        while diff:
            if diff & 1:
                a = up[j][a]
            diff >>= 1
            j += 1
        if a == b:
            return a
        for j in range(LOG - 1, -1, -1):
            if up[j][a] != up[j][b]:
                a, b = up[j][a], up[j][b]
        return up[0][a]

    queries = []
    for i in range(q):
        u, v = int(data[pos]) - 1, int(data[pos + 1]) - 1
        pos += 2
        if tin[u] > tin[v]:
            u, v = v, u
        w = lca(u, v)
        if w == u:
            queries.append((tin[u], tin[v], -1, i))
        else:
            queries.append((tout[u], tin[v], w, i))
    block = max(1, int((2 * n) / max(1, q) ** 0.5))
    queries.sort(key=lambda t: (t[0] // block, t[1] if (t[0] // block) % 2 == 0 else -t[1]))

    cnt = [0] * len(ids)
    on = [False] * n
    cur = 0

    def toggle(x):
        nonlocal cur
        dx = divs[x]
        if on[x]:
            on[x] = False
            for d, s in dx:
                cnt[d] -= 1
            cur -= sum(s * cnt[d] for d, s in dx)
        else:
            cur += sum(s * cnt[d] for d, s in dx)
            for d, s in dx:
                cnt[d] += 1
            on[x] = True

    ans = [0] * q
    L, R = 0, -1
    for l, r, w, i in queries:
        while R < r:
            R += 1
            toggle(euler[R])
        while L > l:
            L -= 1
            toggle(euler[L])
        while R > r:
            toggle(euler[R])
            R -= 1
        while L < l:
            toggle(euler[L])
            L += 1
        extra = sum(s * cnt[d] for d, s in divs[w]) if w >= 0 else 0
        ans[i] = cur + extra
    print('\n'.join(map(str, ans)))


main()
```

**Watch out.** HackerRank's Python starter reads `u` and `v` from separate lines, but each query is one line `u v`, so parse the input yourself. A value of 1 is coprime to everything, including another 1. Pairs are unordered and use distinct nodes. In CPython this is heavy; PyPy runs it comfortably.

```stdin
6 5
3 2 4 1 6 5
1 2
1 3
2 4
2 5
3 6
4 6
5 6
1 1
1 6
6 1
```

```stdout
9
6
0
3
3
```
