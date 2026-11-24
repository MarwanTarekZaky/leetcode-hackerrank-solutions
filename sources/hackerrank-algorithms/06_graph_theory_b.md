## Graph Theory

### Minimum MST Graph

**Problem.** Build a connected simple graph with `n` nodes, `m` edges and positive integer weights whose minimum spanning tree weighs exactly `s`, minimising the sum of all edge weights. `n` goes up to 10⁸ and `m` up to 10¹⁶.

**Idea.** Sort the MST edges by weight: `w_1 ≤ … ≤ w_{n−1}`, summing to `s`.
- **Extra edges.** A non-tree edge must weigh at least the heaviest tree edge on its cycle. Building the tree as a chain (each edge attaches one new node to one growing component) creates `k − 1` free slots, at weight `w_k`, when the `k`-th edge is added. No other shape creates more cheap slots, so the `e = m − (n − 1)` extra edges take the `e` cheapest slots.
- **Which weights.** The remaining choice is how to spread the excess `X = s − (n − 1)` above weight 1. Weight vectors that are optimal over the reals are "flat on a suffix": the first edges weigh 1 and the last `t` share `X` evenly. The real cost as a function of `t` is concave, so the best `t` sits near `1` or `n − 1`.
- **Integer rounding.** Integer rounding (`q, rem = divmod(X, t)`) only nudges the optimum. There are two ways to place the remainder: spread it as `+1` over the last `rem` edges, or dump all of it on the very last edge. The second can win, because some of the last level's slots may go unused. So evaluate both for a few dozen `t` near each end.

**Steps.**
1. If `e = 0`, the answer is `s`.
2. For each candidate `t` and both remainder placements, list the slot groups: the first `L = n − 1 − t` levels at weight 1, then the suffix weights. Level `k` has `k − 1` slots.
3. The cost is `s` plus `e` slots taken greedily from the cheapest group. Return the minimum.

```python
import os


def slots(a, b):
    """Total slots of levels a..b, where level k has k - 1 slots."""
    if b < a:
        return 0
    return (a - 1 + b - 1) * (b - a + 1) // 2


def minimumMstGraph(n, m, s):
    e = m - (n - 1)
    if e <= 0:
        return s
    x = s - (n - 1)
    best = None
    for t in set(range(1, min(n - 1, 60) + 1)) | set(range(max(1, n - 61), n)):
        low = n - 1 - t
        q, rem = divmod(x, t)
        # (a) the remainder spread as +1 over the last `rem` levels
        spread = ((slots(1, low), 1), (slots(low + 1, n - 1 - rem), 1 + q), (slots(n - rem, n - 1), 2 + q))
        # (b) the whole remainder on the last edge, whose slots may be partly unused
        last = ((slots(1, low), 1), (slots(low + 1, n - 2), 1 + q), (n - 2, 1 + q + rem))
        for groups in (spread, last):
            cost, left = s, e
            for cnt, w in groups:
                take = min(left, cnt)
                cost += take * w
                left -= take
            if left == 0 and (best is None or cost < best):
                best = cost
    return best


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    g = int(input())
    for _ in range(g):
        n, m, s = map(int, input().split())
        fptr.write(str(minimumMstGraph(n, m, s)) + '\n')
    fptr.close()
```

**Watch out.**
- **Simple cases first.** When the extra edges all fit inside the first `n − 1` nodes (`e ≤ (n−2)(n−3)/2`), the answer is simply `s + e`: put all the excess on one last edge to a lone node. The hard case is when extra edges must touch that node too.
- **Exact arithmetic.** All values reach 10¹⁶·10¹⁰, so integers must stay exact. In Python they do.
- **How this was checked.** Against a brute force over every graph for `n ≤ 4`, and over every weight vector of the chain model for `n ≤ 10`.

```stdin
2
4 5 4
4 3 6
```

```stdout
7
6
```

### Jack goes to Rapture

**Problem.** Riding from station A to B costs `fare(A, B)` minus everything paid so far, or nothing if that is negative. Find the cheapest total fare from station 1 to station `n`.

**Idea.** The running total after any route is just the **largest** fare on it: each step tops the total up to `max(total, fare)`. So you want the path that minimises its maximum edge, a bottleneck path. Kruskal finds it: add edges in increasing order until 1 and `n` are connected, and the last edge's fare is the answer.

**Steps.**
1. Sort the edges by fare and union them in order.
2. As soon as `find(1) == find(n)`, print that fare. If that never happens, print `NO PATH EXISTS`.

```python
def getCost(g_nodes, g_from, g_to, g_weight):
    if g_nodes == 1:
        print(0)
        return
    parent = list(range(g_nodes + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for w, u, v in sorted(zip(g_weight, g_from, g_to)):
        parent[find(u)] = find(v)
        if find(1) == find(g_nodes):
            print(w)
            return
    print('NO PATH EXISTS')


if __name__ == '__main__':
    g_nodes, g_edges = map(int, input().split())
    g_from, g_to, g_weight = [0] * g_edges, [0] * g_edges, [0] * g_edges
    for i in range(g_edges):
        g_from[i], g_to[i], g_weight[i] = map(int, input().split())
    getCost(g_nodes, g_from, g_to, g_weight)
```

**Watch out.** Plain Dijkstra on sums is wrong here. A Dijkstra variant that relaxes with `max(d, w)` also works. The function prints, not returns.

```stdin
5 5
1 2 60
3 5 70
1 4 120
4 5 150
2 3 80
```

```stdout
80
```

### Crab Graphs

**Problem.** A crab is a head joined to between 1 and `T` feet. Choose vertex-disjoint crabs in the graph covering as many vertices as possible.

**Idea.** Max flow.
- **Network.** Each vertex `v` gets a head copy (capacity `T` from the source) and a foot copy (capacity 1 to the sink). Every edge `u–v` becomes `head(u) → foot(v)` and `head(v) → foot(u)`.
- **Why the flow is the answer.** A unit of flow into `foot(v)` means "`v` is covered, hanging from a neighbour". Every crab's vertices can be covered this way: the feet hang from the head, and the head hangs from one of its own feet. Conversely, any such "each covered vertex has one parent" structure splits into crabs with at most `T` feet. So the max flow equals the maximum number of covered vertices.

**Steps.**
1. Build the network: source `0`, heads `1..n`, feet `n+1..2n`, sink `2n+1`.
2. Run Dinic and print the flow.

```python
import os
from collections import deque


class Dinic:
    def __init__(self, n):
        self.n = n
        self.g = [[] for _ in range(n)]

    def add(self, u, v, c):
        self.g[u].append([v, c, len(self.g[v])])
        self.g[v].append([u, 0, len(self.g[u]) - 1])

    def max_flow(self, s, t):
        g, total = self.g, 0
        while True:
            level = [-1] * self.n
            level[s] = 0
            queue = deque([s])
            while queue:
                u = queue.popleft()
                for v, c, _ in g[u]:
                    if c > 0 and level[v] < 0:
                        level[v] = level[u] + 1
                        queue.append(v)
            if level[t] < 0:
                return total
            it = [0] * self.n
            while True:
                stack, path = [s], []
                while stack and stack[-1] != t:
                    u = stack[-1]
                    while it[u] < len(g[u]):
                        e = g[u][it[u]]
                        if e[1] > 0 and level[e[0]] == level[u] + 1:
                            break
                        it[u] += 1
                    if it[u] < len(g[u]):
                        stack.append(g[u][it[u]][0])
                        path.append(g[u][it[u]])
                    else:
                        stack.pop()
                        level[u] = -1
                        if path:
                            path.pop()
                            it[stack[-1]] += 1
                if not stack:
                    break
                f = min(e[1] for e in path)
                for e in path:
                    e[1] -= f
                    g[e[0]][e[2]][1] += f
                total += f


def crabGraphs(n, t, graph):
    net = Dinic(2 * n + 2)
    sink = 2 * n + 1
    for v in range(1, n + 1):
        net.add(0, v, t)
        net.add(n + v, sink, 1)
    for u, v in graph:
        net.add(u, n + v, 1)
        net.add(v, n + u, 1)
    return net.max_flow(0, sink)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    c = int(input().strip())
    for _ in range(c):
        n, t, m = map(int, input().split())
        graph = [list(map(int, input().split())) for _ in range(m)]
        fptr.write(str(crabGraphs(n, t, graph)) + '\n')
    fptr.close()
```

**Watch out.** It's tempting to count heads separately, but the flow already includes each head, through the foot unit that comes from one of its own feet. An isolated vertex can never be covered.

```stdin
2
8 2 7
1 4
2 4
3 4
5 4
5 8
5 7
5 6
6 3 8
1 2
2 3
3 4
4 5
5 6
6 1
1 4
2 5
```

```stdout
6
6
```

### Bead Ornaments

**Problem.** Join all beads into a tree, where the beads of each color form a connected subtree. Count the distinct trees modulo 10⁹+7.

**Idea.** Two Cayley-formula facts:
- **Within a color.** The beads of one color, `b` labelled beads, form any of `b^(b−2)` trees (1 when `b = 1`).
- **Between colors.** Joining `k` fixed groups of sizes `b_1..b_k` into one tree, one edge per join, can be done in `S^(k−2) · Π b_i` ways, where `S = Σ b_i`. That is the generalised Cayley formula.

Multiply the two. With a single color, the second factor is just 1.

**Steps.**
1. `ans = Π b^(b−2)`, using 1 for `b = 1`.
2. If there are `k ≥ 2` colors, multiply by `S^(k−2) · Π b_i`.

```python
import os

MOD = 10 ** 9 + 7


def beadOrnaments(b):
    ans = 1
    for x in b:
        if x >= 2:
            ans = ans * pow(x, x - 2, MOD) % MOD
    if len(b) >= 2:
        ans = ans * pow(sum(b), len(b) - 2, MOD) % MOD
        for x in b:
            ans = ans * x % MOD
    return ans


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        input()
        b = list(map(int, input().split()))
        fptr.write(str(beadOrnaments(b)) + '\n')
    fptr.close()
```

**Watch out.** `pow(1, -1, MOD)` would compute a modular inverse, so special-case `b = 1` (exactly 1 tree). The `Π b_i` factor counts which bead of each group the joining edges attach to.

```stdin
5
2
2 1
2
2 2
1
4
2
3 1
5
1 1 1 1 1
```

```stdout
2
4
16
9
125
```

### Jeanie's Route

**Problem.** In a weighted tree, find the shortest walk (any start, any end) that visits all `K` letter cities.

**Idea.** Only the smallest subtree containing every letter city matters. Find it by repeatedly cutting leaves that aren't letter cities. A closed tour of that subtree walks every edge twice. Since the walk doesn't have to return, it can skip walking back along the longest path, the subtree's diameter. So the answer is `2·(edge sum) − diameter`.

**Steps.**
1. Peel non-letter leaves with a queue until none remain.
2. Sum the weights of the edges between surviving nodes.
3. Find the diameter of the surviving tree with two farthest-node searches.

```python
import os
from collections import deque


def jeanisRoute(n, city, roads):
    adj = [[] for _ in range(n + 1)]
    for u, v, d in roads:
        adj[u].append((v, d))
        adj[v].append((u, d))
    letter = [False] * (n + 1)
    for c in city:
        letter[c] = True
    deg = [len(a) for a in adj]
    gone = [False] * (n + 1)
    queue = deque(v for v in range(1, n + 1) if deg[v] == 1 and not letter[v])
    while queue:
        u = queue.popleft()
        gone[u] = True
        for v, _ in adj[u]:
            if not gone[v]:
                deg[v] -= 1
                if deg[v] == 1 and not letter[v]:
                    queue.append(v)
    total = sum(d for u, v, d in roads if not gone[u] and not gone[v])

    def farthest(src):
        dist = {src: 0}
        stack = [src]
        while stack:
            u = stack.pop()
            for v, d in adj[u]:
                if not gone[v] and v not in dist:
                    dist[v] = dist[u] + d
                    stack.append(v)
        far = max(dist, key=dist.get)
        return far, dist[far]

    a, _ = farthest(city[0])
    _, diameter = farthest(a)
    return 2 * total - diameter


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    city = list(map(int, input().split()))
    roads = [list(map(int, input().split())) for _ in range(n - 1)]
    fptr.write(str(jeanisRoute(n, city, roads)) + '\n')
    fptr.close()
```

**Watch out.** HackerRank's starter calls `jeanisRoute(k, roads)` without passing the cities, so pass them yourself. Pruning must repeat: removing a leaf can turn its neighbour into a new non-letter leaf.

```stdin
5 3
1 3 4
1 2 1
2 3 2
2 4 2
3 5 3
```

```stdout
6
```

### Floyd : City of Blinding Lights

**Problem.** Answer up to 10⁵ shortest-distance queries in a directed weighted graph with `n ≤ 400` nodes (`-1` if unreachable).

**Idea.** Floyd–Warshall: for each middle node `k`, `d[i][j] = min(d[i][j], d[i][k] + d[k][j])`. In pure Python the 64 million updates are slow. NumPy does each `k` step as a single matrix operation using broadcasting, so there are only 400 vectorised steps. After that, every query is an O(1) lookup.

**Steps.**
1. Fill the matrix with "infinity" and set each edge, **overwriting** earlier duplicates (the last one wins, per the statement). Set the diagonal to 0.
2. For each `k`: `np.minimum(d, d[:, k:k+1] + d[k:k+1, :], out=d)`.
3. Answer the queries, mapping infinity to -1.

```python
import sys

import numpy as np


def main():
    data = sys.stdin.buffer.read().split()
    n, m = int(data[0]), int(data[1])
    inf = 10 ** 12
    d = np.full((n, n), inf, dtype=np.int64)
    pos = 2
    for _ in range(m):
        u, v, w = int(data[pos]) - 1, int(data[pos + 1]) - 1, int(data[pos + 2])
        pos += 3
        d[u, v] = w
    np.fill_diagonal(d, 0)
    for k in range(n):
        np.minimum(d, d[:, k:k + 1] + d[k:k + 1, :], out=d)
    q = int(data[pos])
    pos += 1
    out = []
    for _ in range(q):
        x, y = int(data[pos]) - 1, int(data[pos + 1]) - 1
        pos += 2
        out.append(str(d[x, y]) if d[x, y] < inf else '-1')
    print('\n'.join(out))


main()
```

**Watch out.** A repeated edge replaces the earlier one even if the new weight is larger; taking the minimum would be wrong here. Use a finite "infinity" in `int64`, so that `inf + inf` cannot overflow.

```stdin
4 5
1 2 5
1 4 24
2 4 6
3 4 4
3 2 7
3
1 2
3 1
1 4
```

```stdout
5
-1
11
```

### Roads in HackerLand

**Problem.** Road lengths are distinct powers of two. Print, in binary, the sum of shortest distances over all pairs of cities.

**Idea.** `2^c` is larger than the sum of all smaller powers of two. So a shortest path never uses an edge when there is an alternative route through cheaper edges only, which means shortest paths run along the minimum spanning tree. In that tree, an edge of length `2^c` that splits it into parts of size `a` and `n − a` lies on `a·(n − a)` paths. So add `a·(n − a)` to bit position `c`, then propagate carries to get the binary answer.

**Steps.**
1. Run Kruskal in increasing `c` to build the MST.
2. Compute subtree sizes in the tree and set `cnt[c] = a·(n − a)` for each tree edge.
3. Propagate carries bit by bit; output the bits from the highest, with no leading zeros.

```python
import os


def roadsInHackerland(n, roads):
    parent = list(range(n + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    adj = [[] for _ in range(n + 1)]
    for a, b, c in sorted(roads, key=lambda r: r[2]):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            adj[a].append((b, c))
            adj[b].append((a, c))
    order, par, pc = [1], [0] * (n + 1), [0] * (n + 1)
    seen = [False] * (n + 1)
    seen[1] = True
    for u in order:
        for v, c in adj[u]:
            if not seen[v]:
                seen[v] = True
                par[v], pc[v] = u, c
                order.append(v)
    size = [1] * (n + 1)
    cnt = {}
    for v in reversed(order[1:]):
        size[par[v]] += size[v]
        cnt[pc[v]] = size[v] * (n - size[v])
    bits, carry, c = [], 0, 0
    top = max(cnt) if cnt else 0
    while c <= top or carry:
        carry += cnt.get(c, 0)
        bits.append(carry & 1)
        carry >>= 1
        c += 1
    s = ''.join(map(str, reversed(bits))).lstrip('0')
    return s or '0'


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m = map(int, input().split())
    roads = [list(map(int, input().split())) for _ in range(m)]
    fptr.write(roadsInHackerland(n, roads) + '\n')
    fptr.close()
```

**Watch out.** Adding `cnt << c` into one big integer for every edge does O(M) big-number additions of up to 2·10⁵ bits each. Carrying bit by bit stays linear. With a single city, the answer is `0`.

```stdin
5 6
1 3 5
4 5 0
2 1 3
3 2 1
4 3 4
4 2 2
```

```stdout
1000100
```

### Kingdom Connectivity

**Problem.** Count the paths from city 1 to city `n` in a directed multigraph, modulo 10⁹, or print `INFINITE PATHS` if there are infinitely many.

**Idea.** There are infinitely many paths exactly when some cycle lies on a route from 1 to `n`. Keep only the nodes that are reachable from 1 **and** can reach `n`. If that subgraph has a cycle, Kahn's topological sort cannot finish it. Otherwise count paths in topological order with `ways[v] += ways[u]` for every parallel edge.

**Steps.**
1. Mark the nodes reachable from 1 by following edges forward, and the nodes that reach `n` by following them backwards. Keep the intersection.
2. If `n` is not in the kept set, print 0.
3. Run Kahn's algorithm on the kept subgraph. If some node is never processed, print `INFINITE PATHS`; otherwise print `ways[n] mod 10⁹`.

```python
from collections import deque


def countPaths(n, edges):
    fwd = [[] for _ in range(n + 1)]
    rev = [[] for _ in range(n + 1)]
    for a, b in edges:
        fwd[a].append(b)
        rev[b].append(a)

    def reach(src, adj):
        seen = [False] * (n + 1)
        seen[src] = True
        stack = [src]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    stack.append(v)
        return seen

    a, b = reach(1, fwd), reach(n, rev)
    good = [a[v] and b[v] for v in range(n + 1)]
    if not good[n]:
        print(0)
        return
    indeg = [0] * (n + 1)
    for u, v in edges:
        if good[u] and good[v]:
            indeg[v] += 1
    ways = [0] * (n + 1)
    ways[1] = 1
    queue = deque(v for v in range(1, n + 1) if good[v] and indeg[v] == 0)
    done = 0
    while queue:
        u = queue.popleft()
        done += 1
        for v in fwd[u]:
            if good[v]:
                ways[v] = (ways[v] + ways[u]) % 10 ** 9
                indeg[v] -= 1
                if indeg[v] == 0:
                    queue.append(v)
    if done < sum(good):
        print('INFINITE PATHS')
    else:
        print(ways[n])


if __name__ == '__main__':
    nodes, m = map(int, input().split())
    edges = [list(map(int, input().split())) for _ in range(m)]
    countPaths(nodes, edges)
```

**Watch out.** A cycle that is unreachable from 1, or that cannot reach `n`, doesn't make the answer infinite; that is why the graph is filtered first. A self-loop on the route is a cycle too. Parallel roads count separately, so keep duplicates in the adjacency lists.

```stdin
5 5
1 2
2 4
2 3
3 4
4 5
```

```stdout
2
```

### Computer Game

**Problem.** Remove pairs `(A_i, B_j)` that share a common factor, using each element at most once. Find the maximum number of pairs (`n ≤ 10⁵`, values `≤ 10⁹`).

**Idea.** This is bipartite matching, but listing every compatible pair directly could need about `n²` edges. Instead, put the primes in the middle: `A_i → p → B_j` whenever `p` divides both, with unlimited capacity through `p`. A max flow from A to B then equals the maximum matching, and the graph has only O(n · #prime factors) edges.

**Factoring.** Trial-divide by primes below 1000. What remains has every prime factor above 1000, so being ≤ 10⁹ it has at most two of them. Check it with Miller–Rabin, and split it with Pollard's rho if it is composite.

**Steps.**
1. Factor every value and give each distinct prime a node.
2. Build the network `source → A_i (1) → p (∞) → B_j (1) → sink` and run Dinic.

```python
import os
import random
from collections import deque
from math import gcd, isqrt

SMALL = [p for p in range(2, 1000) if all(p % d for d in range(2, isqrt(p) + 1))]


def is_prime(n):
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13):
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in (2, 3, 5, 7, 11, 13):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def rho(n):
    while True:
        c = random.randrange(1, n)
        x = y = random.randrange(2, n)
        d = 1
        while d == 1:
            x = (x * x + c) % n
            y = (y * y + c) % n
            y = (y * y + c) % n
            d = gcd(abs(x - y), n)
        if d != n:
            return d


def primes_of(x):
    ps = []
    for p in SMALL:
        if x % p == 0:
            ps.append(p)
            while x % p == 0:
                x //= p
    if x > 1:
        if is_prime(x):
            ps.append(x)
        else:
            r = isqrt(x)
            if r * r == x:
                ps.append(r)
            else:
                d = rho(x)
                ps += [d, x // d]
    return ps


class Dinic:
    def __init__(self, n):
        self.n = n
        self.g = [[] for _ in range(n)]

    def add(self, u, v, c):
        self.g[u].append([v, c, len(self.g[v])])
        self.g[v].append([u, 0, len(self.g[u]) - 1])

    def max_flow(self, s, t):
        g, total = self.g, 0
        while True:
            level = [-1] * self.n
            level[s] = 0
            queue = deque([s])
            while queue:
                u = queue.popleft()
                for v, c, _ in g[u]:
                    if c > 0 and level[v] < 0:
                        level[v] = level[u] + 1
                        queue.append(v)
            if level[t] < 0:
                return total
            it = [0] * self.n
            while True:
                stack, path = [s], []
                while stack and stack[-1] != t:
                    u = stack[-1]
                    while it[u] < len(g[u]):
                        e = g[u][it[u]]
                        if e[1] > 0 and level[e[0]] == level[u] + 1:
                            break
                        it[u] += 1
                    if it[u] < len(g[u]):
                        stack.append(g[u][it[u]][0])
                        path.append(g[u][it[u]])
                    else:
                        stack.pop()
                        level[u] = -1
                        if path:
                            path.pop()
                            it[stack[-1]] += 1
                if not stack:
                    break
                f = min(e[1] for e in path)
                for e in path:
                    e[1] -= f
                    g[e[0]][e[2]][1] += f
                total += f


def computerGame(a, b):
    n = len(a)
    fa = [primes_of(x) for x in a]
    fb = [primes_of(x) for x in b]
    pid = {}
    for ps in fa + fb:
        for p in ps:
            pid.setdefault(p, len(pid))
    # nodes: 0 source, 1..n A, n+1..2n B, then primes, then sink
    sink = 2 * n + len(pid) + 1
    net = Dinic(sink + 1)
    big = n
    for i in range(n):
        net.add(0, 1 + i, 1)
        net.add(n + 1 + i, sink, 1)
        for p in fa[i]:
            net.add(1 + i, 2 * n + 1 + pid[p], 1)
        for p in fb[i]:
            net.add(2 * n + 1 + pid[p], n + 1 + i, big)
    return net.max_flow(0, sink)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    a = list(map(int, input().split()))
    b = list(map(int, input().split()))
    fptr.write(str(computerGame(a, b)) + '\n')
    fptr.close()
```

**Watch out.** Building all `A×B` pairs with `gcd` is O(n²) = 10¹⁰. The prime layer is what makes the graph small. The capacity from `A_i` into a prime can be 1, since `A_i` sends only one unit anyway.

```stdin
4
2 5 6 7
4 9 10 12
```

```stdout
3
```

### Rust & Murderer

**Problem.** The roads given are main roads; every *missing* pair of cities is a village road. Find BFS distances from `S` using village roads only, in the complement of a sparse graph with `N ≤ 2·10⁵`.

**Idea.** Run BFS on the complement without building it. Keep the set of unvisited nodes. When popping `u`, every unvisited node that is **not** a main-road neighbour of `u` gets visited now; the rest stay unvisited. Each check either removes a node from the set (at most N times overall) or is charged to a main road at `u` (at most 2M overall). So the whole BFS is O(N + M).

**Steps.**
1. Store the main roads as adjacency sets.
2. BFS from `S`. For each `u`, split the unvisited list into `adj[u]` members (they stay) and the others (visit them at `dist[u] + 1`).

```python
import os
from collections import deque


def rustMurderer(n, roads, s):
    adj = [set() for _ in range(n + 1)]
    for a, b in roads:
        adj[a].add(b)
        adj[b].add(a)
    dist = [0] * (n + 1)
    unvisited = [v for v in range(1, n + 1) if v != s]
    queue = deque([s])
    while queue and unvisited:
        u = queue.popleft()
        main = adj[u]
        keep = []
        for v in unvisited:
            if v in main:
                keep.append(v)
            else:
                dist[v] = dist[u] + 1
                queue.append(v)
        unvisited = keep
    return [dist[v] for v in range(1, n + 1) if v != s]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input())
    for _ in range(t):
        n, m = map(int, input().split())
        roads = [list(map(int, input().split())) for _ in range(m)]
        s = int(input())
        fptr.write(' '.join(map(str, rustMurderer(n, roads, s))) + '\n')
    fptr.close()
```

**Watch out.** Materialising the complement is about N²/2 = 2·10¹⁰ edges, which is impossible. HackerRank's starter calls `rustMurderer(n, roads)` while the stub is named `rustMurdered` and never passes `s`, so fix the call.

```stdin
2
4 3
1 2
2 3
1 4
1
4 2
1 2
2 3
2
```

```stdout
3 1 2
2 2 1
```

### Problem solving

**Problem.** Solve problems in increasing index order each day. Consecutive problems on the same day must differ in rating by at least `K`. Find the minimum number of days.

**Idea.** Each day is a path in the DAG with edges `i → j` (`i < j`, `|v_i − v_j| ≥ K`). The minimum number of vertex-disjoint paths covering a DAG is `N − maximum matching`, where the matching is between "left copies" (as predecessors) and "right copies" (as successors). Every matched edge glues two problems into the same day, saving one day.

**Steps.**
1. For each `i`, list the successors `j > i` with `|v_i − v_j| ≥ K`.
2. Run Kuhn's augmenting-path matching.
3. Return `N − matching`.

```python
import os


def problemSolving(k, v):
    n = len(v)
    adj = [[j for j in range(i + 1, n) if abs(v[i] - v[j]) >= k] for i in range(n)]
    match = [-1] * n

    def augment(i, seen):
        for j in adj[i]:
            if not seen[j]:
                seen[j] = True
                if match[j] < 0 or augment(match[j], seen):
                    match[j] = i
                    return True
        return False

    matched = sum(augment(i, [False] * n) for i in range(n))
    return n - matched


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n, k = map(int, input().split())
        v = list(map(int, input().split()))
        fptr.write(str(problemSolving(k, v)) + '\n')
    fptr.close()
```

**Watch out.** HackerRank's Python starter reads `T` but then handles only one test, so loop over all `T` yourself. Greedy "start a new day when stuck" is wrong; path cover needs matching.

```stdin
2
3 2
5 4 7
5 1
5 3 4 5 6
```

```stdout
2
1
```
