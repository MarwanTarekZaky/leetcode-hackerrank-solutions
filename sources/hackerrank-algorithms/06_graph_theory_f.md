## Graph Theory

### Road Network

**Problem.** In a weighted undirected multigraph (`N ≤ 500`), the separation number of two cities is their minimum cut. Print the product of the separation numbers over all unordered pairs, modulo 10⁹+7.

**Idea.** Build a **Gomory–Hu tree**. It is a tree on the same cities where the min cut between any two cities equals the lightest edge on their tree path, and it takes only `N − 1` max-flow runs (Gusfield's algorithm).
- **Building it.** Every node starts with parent 0. For node `i`, run a max flow to `parent[i]`; that flow is the weight of edge `i–parent[i]`. Any later node `j` on `i`'s side of the cut that shares `i`'s parent is re-hung under `i`.
- **Taking the product.** Add the tree edges from heaviest to lightest with union-find. When an edge of weight `w` joins groups of sizes `a` and `b`, it is the path minimum for exactly `a·b` pairs, so multiply in `w^(a·b)`.

**Steps.**
1. Gusfield: for `i = 1..N−1`, run Dinic between `i` and `parent[i]` on a fresh copy of the network. Record the flow and re-hang `j > i` on `i`'s side.
2. Sort the tree edges by weight, descending, and multiply `pow(w, a·b, MOD)` while merging.

```python
import os
from collections import deque

MOD = 10 ** 9 + 7


def max_flow_cut(n, edges, s, t):
    """Dinic on an undirected multigraph; returns (flow, set of nodes on s's side)."""
    g = [[] for _ in range(n)]
    for u, v, c in edges:
        g[u].append([v, c, len(g[v])])
        g[v].append([u, c, len(g[u]) - 1])
    total = 0
    while True:
        level = [-1] * n
        level[s] = 0
        queue = deque([s])
        while queue:
            u = queue.popleft()
            for v, c, _ in g[u]:
                if c > 0 and level[v] < 0:
                    level[v] = level[u] + 1
                    queue.append(v)
        if level[t] < 0:
            return total, {v for v in range(n) if level[v] >= 0}
        it = [0] * n
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


def roadNetwork(road_nodes, road_from, road_to, road_weight):
    n = road_nodes
    edges = [(u - 1, v - 1, w) for u, v, w in zip(road_from, road_to, road_weight)]
    parent, weight = [0] * n, [0] * n
    for i in range(1, n):
        f, side = max_flow_cut(n, edges, i, parent[i])
        weight[i] = f
        for j in range(i + 1, n):
            if j in side and parent[j] == parent[i]:
                parent[j] = i
    dsu, size = list(range(n)), [1] * n

    def find(x):
        while dsu[x] != x:
            dsu[x] = dsu[dsu[x]]
            x = dsu[x]
        return x

    ans = 1
    for i in sorted(range(1, n), key=lambda i: -weight[i]):
        a, b = find(i), find(parent[i])
        ans = ans * pow(weight[i], size[a] * size[b], MOD) % MOD
        dsu[a] = b
        size[b] += size[a]
    return ans


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m = map(int, input().split())
    rf, rt, rw = [0] * m, [0] * m, [0] * m
    for i in range(m):
        rf[i], rt[i], rw[i] = map(int, input().split())
    fptr.write(str(roadNetwork(n, rf, rt, rw)) + '\n')
    fptr.close()
```

**Watch out.**
- **Undirected capacities.** An undirected edge is two arcs, each with the full capacity, and each is the other's residual.
- **Cost.** `N − 1` max flows on 10⁴ edges are heavy in CPython, so use PyPy.
- **Sample.** HackerRank shows no sample, so the hidden test is a triangle with weights 1, 2, 3. Its cuts are 3, 4 and 3, giving 36.

```stdin
3 3
1 2 1
2 3 2
1 3 3
```

```stdout
36
```

### Going to the Office

**Problem.** Each day one road is closed. Report the shortest `S → D` distance avoiding it, or `Infinity`. There are up to 2·10⁵ cities, roads and queries.

**Idea.** The replacement-paths technique for undirected graphs.
- **Unaffected queries.** Fix one shortest path `P = p_0 … p_L` from the Dijkstra tree of `S`. Closing a road off `P` changes nothing.
- **Labels.** For every vertex `v`, let `a(v)` be the index where `v`'s `S`-tree branch leaves `P`, and `b(v)` the first index of `P` that `v`'s `D`-tree path reaches.
- **Detours.** Closing `P`'s edge `i` (between `p_i` and `p_{i+1}`) leaves a best detour that crosses from the `S` side to the `D` side through exactly one non-path edge `(x, y)` with `a(x) ≤ i < b(y)`. That detour costs `dS[x] + w + dD[y]`.
- **Filling in the answers.** Sort the candidates by cost and "paint" each one onto its range of path edges, skipping edges already painted (union-find "next unpainted").

**Steps.**
1. Run Dijkstra from `S` and from `D`, keeping the parent pointers. Extract `P`.
2. Compute `a` by walking vertices in increasing `dS` (path vertices get their own index), and `b` in increasing `dD`.
3. For every edge not on `P`, in both directions, add the candidate `[a(x), b(y) − 1]`. Paint the candidates in increasing cost.
4. Answer each query from the painted array, or with `dS[D]` when the road is off `P`.

```python
import sys
from heapq import heappop, heappush


def dijkstra(n, adj, src):
    inf = float('inf')
    dist, par = [inf] * n, [-1] * n
    dist[src] = 0
    heap = [(0, src)]
    while heap:
        d, u = heappop(heap)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                par[v] = u
                heappush(heap, (d + w, v))
    return dist, par


def main():
    data = sys.stdin.buffer.read().split()
    n, m = int(data[0]), int(data[1])
    pos = 2
    adj = [[] for _ in range(n)]
    edges = []
    for _ in range(m):
        u, v, w = int(data[pos]), int(data[pos + 1]), int(data[pos + 2])
        pos += 3
        adj[u].append((v, w))
        adj[v].append((u, w))
        edges.append((u, v, w))
    s, d = int(data[pos]), int(data[pos + 1])
    pos += 2
    q = int(data[pos]); pos += 1
    inf = float('inf')
    ds, ps = dijkstra(n, adj, s)
    dd, pd = dijkstra(n, adj, d)
    out = []
    if ds[d] == inf or s == d:
        res = 'Infinity' if ds[d] == inf else '0'
        print('\n'.join([res] * q))
        return
    path = [d]
    while path[-1] != s:
        path.append(ps[path[-1]])
    path.reverse()
    L = len(path) - 1
    on_path = {v: i for i, v in enumerate(path)}
    path_edge = {}
    for i in range(L):
        path_edge[(path[i], path[i + 1])] = i
        path_edge[(path[i + 1], path[i])] = i
    a = [-1] * n
    for v in sorted((v for v in range(n) if ds[v] < inf), key=lambda v: ds[v]):
        a[v] = on_path[v] if v in on_path else a[ps[v]]
    b = [-1] * n
    for v in sorted((v for v in range(n) if dd[v] < inf), key=lambda v: dd[v]):
        b[v] = on_path[v] if v in on_path else b[pd[v]]
    cands = []
    for u, v, w in edges:
        if (u, v) in path_edge:
            continue
        for x, y in ((u, v), (v, u)):
            if ds[x] < inf and dd[y] < inf and a[x] < b[y]:
                cands.append((ds[x] + w + dd[y], a[x], b[y] - 1))
    cands.sort()
    best = [inf] * L
    nxt = list(range(L + 1))

    def find(x):
        while nxt[x] != x:
            nxt[x] = nxt[nxt[x]]
            x = nxt[x]
        return x

    for cost, lo, hi in cands:
        i = find(lo)
        while i <= hi:
            best[i] = cost
            nxt[i] = i + 1
            i = find(i + 1)
    for _ in range(q):
        u, v = int(data[pos]), int(data[pos + 1])
        pos += 2
        i = path_edge.get((u, v))
        if i is None:
            out.append(str(ds[d]))
        else:
            out.append(str(best[i]) if best[i] < inf else 'Infinity')
    print('\n'.join(out))


main()
```

**Watch out.**
- **Why one crossing edge suffices.** This holds in undirected graphs with positive weights. It is the classic replacement-paths theorem.
- **Running Dijkstra per query** would be O(Q·M log N), far too slow.
- **Painting.** "Paint each edge once, cheapest first" keeps the range-minimum step near linear.

```stdin
6 9
0 1 1
1 2 1
2 3 1
3 4 1
4 5 1
2 4 5
3 5 8
1 3 3
0 2 4
0 5
9
0 1
1 2
2 3
3 4
4 5
2 4
3 5
1 3
0 2
```

```stdout
7
6
6
8
11
5
5
5
5
```

### Tree Splitting

**Problem.** Vertices of a tree are deleted one at a time, online (each query is XOR-encoded with the previous answer). Before each deletion, print the size of the deleted vertex's component.

**Idea.** Keep a component id and a size for every live vertex. Deleting `v` splits its component into one piece per live neighbour. Search all those pieces **in parallel**, one step each in turn, until every piece except one has been fully explored. Give the finished pieces fresh ids and sizes; the last piece keeps the old id with its size reduced. Each search step is charged to a piece that is no larger than the one left unexplored, so a vertex is relabelled only O(log n) times.

**Steps.**
1. Decode `v = previous answer XOR m_j`, then print `size[comp[v]]`.
2. Delete `v`. Run a round-robin BFS from each live neighbour, stopping when only one search is still running.
3. Relabel the completed pieces and shrink the old component's size by `1 + Σ` their sizes.

```python
import sys
from collections import deque


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    adj = [[] for _ in range(n + 1)]
    pos = 1
    for _ in range(n - 1):
        u, v = int(data[pos]), int(data[pos + 1])
        pos += 2
        adj[u].append(v)
        adj[v].append(u)
    m = int(data[pos]); pos += 1
    comp = [0] * (n + 1)
    size = [n]
    alive = [True] * (n + 1)
    out = []
    ans = 0
    for _ in range(m):
        v = ans ^ int(data[pos]); pos += 1
        cid = comp[v]
        ans = size[cid]
        out.append(ans)
        alive[v] = False
        starts = [u for u in adj[v] if alive[u]]
        if not starts:
            continue
        searches = [[deque([u]), {u}, True] for u in starts]   # queue, seen, running
        running = len(searches)
        while running > 1:
            for sr in searches:
                if not sr[2]:
                    continue
                queue, seen, _ = sr
                if not queue:
                    sr[2] = False
                    running -= 1
                    if running == 1:
                        break
                    continue
                x = queue.popleft()
                for y in adj[x]:
                    if alive[y] and y not in seen:
                        seen.add(y)
                        queue.append(y)
        moved = 0
        for queue, seen, run in searches:
            if not run:
                new_id = len(size)
                size.append(len(seen))
                moved += len(seen)
                for x in seen:
                    comp[x] = new_id
        size[cid] -= 1 + moved
    print('\n'.join(map(str, out)))


main()
```

**Watch out.**
- **Fully explored pieces only.** Only searches whose queue emptied are complete pieces. The one still running keeps the old id, and nothing in it is relabelled.
- **Online queries.** Every query depends on the previous answer, so offline tricks like reversing the deletions into union-find merges are not allowed.

```stdin
4
1 2
1 3
1 4
4
3
6
2
6
```

```stdout
4
3
2
1
```

### Ticket

**Problem.** `n ≤ 500` people queue for `m ≤ 10` windows and keep their order. Someone whose window predecessor shares their destination pays 80%. Minimise the total and print one optimal window assignment.

**Idea.** Min-cost flow on a timeline.
- **Links.** A discount is a *link* `i → j`: person `j` is the next person after `i` in the same window, with the same destination. Every person between them must use other windows, so while a link is open it reserves a window. The rule is: at every person `t`, at most `m − 1` links may pass strictly over `t`.
- **The network.** Model the windows as `m` units of flow along the line of people.
  - Person `t` is an edge `P_t → Q_t`. It has a capacity-1 edge with a huge negative cost (forcing at least one window to be free at `t`) plus a capacity `m − 1` edge with cost 0.
  - A link is `Q_i → O_i → I_j → P_j` with cost `−0.2·price_j`. The capacity-1 hops `Q_i → O_i` and `I_j → P_j` allow each person at most one outgoing and one incoming link.
- **Solving.** The graph is a DAG, so the initial potentials come from one topological pass; after that, Dijkstra pushes the `m` units.

**Steps.**
1. Work in tenths of a unit so that costs are integers: full fare `10p`, link saving `2p`.
2. Run the min-cost flow, then read off the used links `i → j`.
3. Assign windows left to right: `j` joins `i`'s window when linked; otherwise it takes any window whose last person has no pending link. Print the total and the windows.

```python
import sys
from heapq import heappop, heappush


def main():
    data = sys.stdin.read().split()
    n, m, k = int(data[0]), int(data[1]), int(data[2])
    pos = 3
    price = {}
    for _ in range(k):
        price[data[pos]] = int(data[pos + 1])
        pos += 2
    dest = data[pos:pos + n]
    cost = [price[x] for x in dest]
    BIG = 10 ** 7
    # node ids: I_t = 4t, P_t = 4t+1, Q_t = 4t+2, O_t = 4t+3  (topological order)
    N = 4 * n
    g = [[] for _ in range(N)]

    def add(u, v, cap, c):
        g[u].append([v, cap, c, len(g[v])])
        g[v].append([u, 0, -c, len(g[u]) - 1])

    for t in range(n):
        I, P, Q, O = 4 * t, 4 * t + 1, 4 * t + 2, 4 * t + 3
        add(P, Q, 1, -BIG)
        if m > 1:
            add(P, Q, m - 1, 0)
        add(Q, O, 1, 0)
        add(I, P, 1, 0)
        if t + 1 < n:
            add(Q, 4 * (t + 1) + 1, m, 0)
        for j in range(t + 1, n):
            if dest[j] == dest[t]:
                add(O, 4 * j, 1, -2 * cost[j])
    src, sink = 1, 4 * (n - 1) + 2
    inf = float('inf')
    pot = [inf] * N
    pot[src] = 0
    for u in range(N):                      # DAG: node ids are already topological
        if pot[u] < inf:
            for v, cap, c, _ in g[u]:
                if cap > 0 and pot[u] + c < pot[v]:
                    pot[v] = pot[u] + c
    pot = [p if p < inf else 0 for p in pot]
    for _ in range(m):
        dist = [inf] * N
        prev = [None] * N
        dist[src] = 0
        heap = [(0, src)]
        while heap:
            d, u = heappop(heap)
            if d > dist[u]:
                continue
            for i, (v, cap, c, _) in enumerate(g[u]):
                if cap > 0:
                    nd = d + c + pot[u] - pot[v]
                    if nd < dist[v]:
                        dist[v] = nd
                        prev[v] = (u, i)
                        heappush(heap, (nd, v))
        if dist[sink] == inf:
            break
        for v in range(N):
            if dist[v] < inf:
                pot[v] += dist[v]
        v = sink
        while v != src:
            u, i = prev[v]
            e = g[u][i]
            e[1] -= 1
            g[v][e[3]][1] += 1
            v = u
    link_to = {}
    for t in range(n):
        for v, cap, c, _ in g[4 * t + 3]:
            if v % 4 == 0 and v > 4 * t and cap == 0 and c < 0:
                link_to[t] = v // 4
    linked_from = {j: i for i, j in link_to.items()}
    window = [0] * n
    last = [None] * (m + 1)
    for t in range(n):
        if t in linked_from:
            w = window[linked_from[t]]
        else:
            w = next(w for w in range(1, m + 1) if last[w] is None or last[w] not in link_to)
        window[t] = w
        last[w] = t
    tenths = 0
    prev_in = {}
    for t in range(n):
        p = prev_in.get(window[t])
        tenths += 8 * cost[t] if p is not None and dest[p] == dest[t] else 10 * cost[t]
        prev_in[window[t]] = t
    total = str(tenths // 10) if tenths % 10 == 0 else f"{tenths // 10}.{tenths % 10}"
    print(total)
    print('\n'.join(map(str, window)))


main()
```

**Watch out.**
- **Strictly over `t`.** The capacity rule counts links strictly over `t`. A link from `i` to `i + 1` reserves nothing, which is why even `m = 1` gets discounts for consecutive equal destinations.
- **Many answers.** Many assignments are optimal, so the hidden test re-scores the printed windows instead of comparing text.

```stdin
5 2 3
CALIFORNIA 10
HAWAII 8
NEWYORK 12
NEWYORK
NEWYORK
CALIFORNIA
NEWYORK
HAWAII
```

```check
lines = output.split('\n')
total = float(lines[0])
assert abs(total - 49.2) < 1e-3, total
toks = stdin.split()
n, m, k = map(int, toks[:3])
price = {toks[3 + 2 * i]: int(toks[4 + 2 * i]) for i in range(k)}
dest = toks[3 + 2 * k:3 + 2 * k + n]
win = [int(x) for x in lines[1:1 + n]]
assert len(win) == n and all(1 <= w <= m for w in win)
last, paid = {}, 0.0
for t in range(n):
    p = last.get(win[t])
    paid += price[dest[t]] * (0.8 if p is not None and dest[p] == dest[t] else 1.0)
    last[win[t]] = t
assert abs(paid - total) < 1e-3, (paid, total)
```

### DFS Edges

**Problem.** Build a directed graph whose DFS from vertex 1 (with adjacency lists in the printed order) produces exactly `t` tree, `b` back, `f` forward and `c` cross edges, or print `-1`.

**Idea.** The tree has `n = t + 1` vertices. Let `D` be the sum of the vertices' depths.
- **The limits.** A vertex at depth `δ` can send back edges to its `δ` ancestors, and can receive forward edges from its `δ − 1` non-parent ancestors. Unrelated pairs can carry one cross edge each, from the later-discovered vertex to the earlier one. So `b ≤ D`, `f ≤ D − (n − 1)` and `c ≤ C(n, 2) − D`.
- **Every edge can be had.** List each vertex's tree edges first and its extra edges after them. Then back edges see ancestors still on the stack, forward edges see finished descendants, and cross edges see finished vertices from earlier branches.
- **Choosing D.** `D` can be any value from `n − 1` (a star) to `C(n, 2)` (a path). So it is feasible exactly when `max(b, f + n − 1, n − 1) ≤ C(n, 2) − c`.
- **Building the tree.** A path of `k` vertices plus leaves on the root, with one extra vertex hung at a chosen height, hits every `D`.

**Steps.**
1. Handle `t = 0` (a single vertex; only `0 0 0 0` works). Otherwise pick `D = max(b, f + n − 1, n − 1)` and check it against `C(n, 2) − c`.
2. Find the path length `k` and the hanging height `h` that give the sum `D`, build the tree, and run DFS on it for depths, discovery and finish order.
3. Enumerate the needed back, forward and cross edges lazily and append them after the tree edges.

```python
import sys


def main():
    t, b, f, c = map(int, sys.stdin.read().split())
    n = t + 1
    if t == 0:
        print("1\n0" if b == f == c == 0 else -1)
        return
    full = n * (n - 1) // 2
    D = max(b, f + n - 1, n - 1)
    if D > full - c:
        print(-1)
        return
    # path 1..k, one vertex hung under path vertex h (depth h), the rest children of the root
    k = 1
    while True:
        base = k * (k - 1) // 2 + (n - k)
        if base <= D <= base + (k - 1 if n > k else 0):
            break
        k += 1
    h = D - base + 1
    children = [[] for _ in range(n + 1)]
    for v in range(2, k + 1):
        children[v - 1].append(v)
    extra = list(range(k + 1, n + 1))
    if extra:
        children[h].append(extra[0])
        for v in extra[1:]:
            children[1].append(v)
    depth = [0] * (n + 1)
    anc = [[] for _ in range(n + 1)]
    order, fin = [], []
    stack = [(1, 0)]
    while stack:
        u, i = stack.pop()
        if i == 0:
            order.append(u)
        if i < len(children[u]):
            stack.append((u, i + 1))
            v = children[u][i]
            depth[v] = depth[u] + 1
            anc[v] = anc[u] + [u]
            stack.append((v, 0))
        else:
            fin.append(u)
    out_edges = [list(ch) for ch in children]
    need = b
    for v in order:
        for a in anc[v]:
            if need == 0:
                break
            out_edges[v].append(a)
            need -= 1
    need = f
    for v in order:
        for a in anc[v][:-1]:
            if need == 0:
                break
            out_edges[a].append(v)
            need -= 1
    need = c
    pos_in = {v: i for i, v in enumerate(order)}
    for v in order:
        if need == 0:
            break
        related = set(anc[v])
        for u in order[:pos_in[v]]:
            if need == 0:
                break
            if u not in related:
                out_edges[v].append(u)
                need -= 1
    lines = [str(n)]
    for v in range(1, n + 1):
        lines.append(' '.join(map(str, [len(out_edges[v])] + out_edges[v])))
    print('\n'.join(lines))


main()
```

**Watch out.**
- **Edge order.** Extra edges must come *after* the tree edges in each list. A forward edge listed first would be taken as a tree edge and change the tree.
- **Cross edge direction.** They must point from the later-discovered vertex to the earlier one; the other direction would be a tree or forward edge.
- **Many answers.** Many graphs are valid, so the hidden test re-runs the DFS and counts the edge types.

```stdin
3 1 1 1
```

```check
toks = output.split()
assert toks[0] != '-1'
n = int(toks[0])
pos, g = 1, [[] for _ in range(n + 1)]
for v in range(1, n + 1):
    d = int(toks[pos]); pos += 1
    g[v] = [int(x) for x in toks[pos:pos + d]]; pos += d
    assert len(set(g[v])) == d and v not in g[v] and all(1 <= x <= n for x in g[v])
disc, fin, onstack, tin = [False] * (n + 1), [False] * (n + 1), [False] * (n + 1), [0] * (n + 1)
cnt = {'t': 0, 'b': 0, 'f': 0, 'c': 0}
timer = 0
stack = [(1, 0)]
disc[1] = onstack[1] = True
while stack:
    u, i = stack.pop()
    if i < len(g[u]):
        stack.append((u, i + 1))
        v = g[u][i]
        if fin[v]:
            cnt['f' if tin[v] > tin[u] else 'c'] += 1
        elif disc[v]:
            cnt['b'] += 1
        else:
            cnt['t'] += 1
            timer += 1
            tin[v] = timer
            disc[v] = onstack[v] = True
            stack.append((v, 0))
    else:
        fin[u] = True
        onstack[u] = False
assert all(disc[1:]), 'not all reachable'
assert (cnt['t'], cnt['b'], cnt['f'], cnt['c']) == tuple(map(int, stdin.split())), cnt
```

### Diameter Minimization

**Problem.** Build a strongly connected directed multigraph on `n` vertices where every vertex has out-degree `m`, with the smallest diameter you can. Print the diameter, then the edges. The task is scored against the author's diameter `s`: `d ≤ s + 1` earns full marks.

**Idea.** Use de Bruijn–style "shift and append a digit" graphs. With `i → (m·i + j) mod n` for `j = 0..m−1`, `d` steps from any `u` reach `m^d·u + x` for every `x < m^d`. Once `m^d ≥ n` that covers every residue, so the diameter is at most `⌈log_m n⌉`, which is essentially optimal for out-degree `m`. The Imase–Itoh variant `i → (−m·i − j) mod n` is often one better. Build both, measure each exact diameter with BFS, and print the better one.

**Steps.**
1. Build the two candidate graphs.
2. For each, take the maximum BFS eccentricity over all vertices (it is finite because the graphs are strongly connected).
3. Print the smaller diameter and its edge lists.

```python
from collections import deque


def diameter(n, out):
    worst = 0
    for s in range(n):
        dist = [-1] * n
        dist[s] = 0
        queue = deque([s])
        seen = 1
        while queue:
            u = queue.popleft()
            for v in out[u]:
                if dist[v] < 0:
                    dist[v] = dist[u] + 1
                    seen += 1
                    queue.append(v)
        if seen < n:
            return float('inf')
        worst = max(worst, max(dist))
    return worst


def main():
    n, m = map(int, input().split())
    candidates = [
        [[(m * i + j) % n for j in range(m)] for i in range(n)],
        [[(-m * i - j) % n for j in range(1, m + 1)] for i in range(n)],
    ]
    best = min(candidates, key=lambda out: diameter(n, out))
    print(diameter(n, best))
    print('\n'.join(' '.join(map(str, row)) for row in best))


main()
```

**Watch out.** Self-loops and repeated edges are allowed, and both constructions produce some. The printed diameter must be the true one for the printed graph, which is why it is measured rather than assumed.

```stdin
5 2
```

```check
toks = output.split()
n, m = map(int, stdin.split())
d = int(toks[0])
rows = [list(map(int, toks[1 + i * m:1 + (i + 1) * m])) for i in range(n)]
assert len(toks) == 1 + n * m and all(0 <= v < n for r in rows for v in r)
worst = 0
for s in range(n):
    dist = {s: 0}
    order = [s]
    for u in order:
        for v in rows[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                order.append(v)
    assert len(dist) == n, 'not strongly connected'
    worst = max(worst, max(dist.values()))
assert worst == d and d <= 2 + 1, (worst, d)
```

### Airports

**Problem.** Airports at positions `x_1, x_2, …` are announced one per day. Two airports are linked if they are at least `d` apart. After each day, print the minimum total movement needed to make all announced airports connected.

**Idea.** Let `lo` and `hi` be the extremes.
- **Connectivity.** Every airport must be at least `d` from one of the two extremes. So no airport may sit strictly inside the window `(hi − d, lo + d)`, and the extremes need `hi − lo ≥ d`.
- **Shrinking.** Pushing the extremes outward shrinks that window by 1 per unit of movement. The window has width `W = 2d − (hi − lo)`, and nothing is needed when `W ≤ 0`.
- **The best split.** Interior airports must end up on one side or the other, and it is never worse to push a side past them than to move them individually. So choose one gap between consecutive interior airports, the window edges included. Shrink the left part up to the gap's left end and the right part down to its right end. That costs `W − G` for the widest gap `G`.
- **The width rule.** The extremes still need `hi − lo ≥ d`, which costs at least `W − d`. So the answer is `max(0, W − G, W − d)`.

**Steps.**
1. Compress the positions of the whole query, ties broken by arrival. Add points to a segment tree that keeps `(first, last, max adjacent gap)` over the added points.
2. After each addition, compute `W` and query the points strictly inside the window, skipping the min and max points themselves.
3. `G = max(first − (hi−d), (lo+d) − last, internal gap)`, or `W` if no point is inside.

```python
import os
from bisect import bisect_left, bisect_right


def airports(d, x):
    n = len(x)
    order = sorted(range(n), key=lambda i: (x[i], i))
    rank = [0] * n
    for r, i in enumerate(order):
        rank[i] = r
    vals = [x[i] for i in order]
    size = 1
    while size < n:
        size *= 2
    NONE = None
    first = [NONE] * (2 * size)
    last = [NONE] * (2 * size)
    gap = [0] * (2 * size)

    def pull(i):
        l, r = 2 * i, 2 * i + 1
        if first[l] is None:
            first[i], last[i], gap[i] = first[r], last[r], gap[r]
        elif first[r] is None:
            first[i], last[i], gap[i] = first[l], last[l], gap[l]
        else:
            first[i], last[i] = first[l], last[r]
            gap[i] = max(gap[l], gap[r], first[r] - last[l])

    def query(lo, hi):
        """Combine leaves lo..hi (inclusive) left to right."""
        res = [None, None, 0]
        lefts, rights = [], []
        lo += size
        hi += size + 1
        while lo < hi:
            if lo & 1:
                lefts.append(lo)
                lo += 1
            if hi & 1:
                hi -= 1
                rights.append(hi)
            lo //= 2
            hi //= 2
        for node in lefts + rights[::-1]:
            if first[node] is None:
                continue
            if res[0] is None:
                res = [first[node], last[node], gap[node]]
            else:
                res = [res[0], last[node], max(res[2], gap[node], first[node] - res[1])]
        return res

    out = []
    lo_v = hi_v = None
    lo_r = hi_r = None
    for i in range(n):
        r = rank[i]
        p = size + r
        first[p] = last[p] = vals[r]
        p //= 2
        while p:
            pull(p)
            p //= 2
        if lo_v is None or r < lo_r:
            lo_r, lo_v = r, vals[r]
        if hi_v is None or r > hi_r:
            hi_r, hi_v = r, vals[r]
        if i == 0:
            out.append(0)
            continue
        w = 2 * d - (hi_v - lo_v)
        if w <= 0:
            out.append(0)
            continue
        left, right = hi_v - d, lo_v + d
        a = max(bisect_right(vals, left), lo_r + 1)
        b = min(bisect_left(vals, right) - 1, hi_r - 1)
        g = w
        if a <= b:
            f, l, inner = query(a, b)
            if f is not None:
                g = max(f - left, right - l, inner)
        out.append(max(0, w - g, w - d))
    return out


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        n, d = map(int, input().split())
        x = list(map(int, input().split()))
        fptr.write(' '.join(map(str, airports(d, x))) + '\n')
    fptr.close()
```

**Watch out.**
- **Duplicates.** Several airports can share a coordinate. Breaking ties by arrival index makes each a separate leaf, so "skip one min and one max" removes exactly one copy.
- **Window edges.** The window is open: an airport exactly `d` away from an extreme is fine.
- **How this was checked.** The formula was verified against an exhaustive search over final positions on small inputs.

```stdin
1
3 1
0 0 0
```

```stdout
0 1 1
```

### Definite Random Walks

**Problem.** The fields form a functional graph `f`. Each turn a die shows `d` with probability `p_d`, and the chip jumps `d` times. Starting uniformly, print the distribution after `k` turns, modulo 998244353.

**Idea.** One turn applies `P(F) = Σ p_d F^d`, so `k` turns apply `Q(F)` with `Q = P^k`. `Q` has degree up to 10⁸, but a functional graph only needs two reductions of it:
- **Reductions of `Q`.**
  - **On the trees.** From a node at distance `t` from its cycle, the first `t` steps stay on its tree. Those steps need only `Q mod x^H`, with `H` the tallest tree.
  - **On a cycle of length `L`.** Positions repeat with period `L`, so only `S_L = Q mod (x^L − 1)` matters.
  - **Computing them.** Both come from binary exponentiation with modular FFT multiplication.
- **Tree nodes.** A node `v` off the cycles receives `Σ_t cnt_v[t]·Q_t`, where `cnt_v[t]` counts the nodes `t` levels below `v`. Long-path decomposition builds every depth-count array inside one shared buffer.
- **Cycle nodes.**
  - **Full sums.** Gather `A[s]` = the number of nodes whose "virtual start" on the cycle (entry index minus depth) is `s`. A cyclic convolution `A ⊛ S_L` then gives every node's mass on the cycle, counting all `j ≥ 0` steps.
  - **Correction.** Those full sums also counted the first `t` steps of each tree node, when it was still on its tree. Subtract them: one correlation of each hanging tree's depth counts with `Q`.

**Steps.**
1. Find the cycles, the hanging trees, their depths and `H`.
2. Compute `Q mod x^H` and `S_L` for each distinct cycle length.
3. Long-path decomposition over the hanging trees: a dot product for each tree node; for each cycle root, its depth counts.
4. For each cycle, combine the cyclic convolution with the correlation corrections. Multiply everything by `n⁻¹`.

```python
import sys

import numpy as np

MOD = 998244353


def mul(a, b):
    """Exact (a * b) mod MOD for int64 arrays via 3-way 10-bit split + float FFT."""
    if len(a) == 0 or len(b) == 0:
        return np.zeros(0, dtype=np.int64)
    need = len(a) + len(b) - 1
    if min(len(a), len(b)) <= 64:
        res = np.zeros(need, dtype=np.int64)
        short, long_ = (a, b) if len(a) <= len(b) else (b, a)
        for i, v in enumerate(short.tolist()):
            if v:
                res[i:i + len(long_)] = (res[i:i + len(long_)] + v * long_) % MOD
        return res
    size = 1
    while size < need:
        size *= 2
    pa = [np.fft.rfft((a >> (10 * i)) & 1023, size) for i in range(3)]
    pb = [np.fft.rfft((b >> (10 * i)) & 1023, size) for i in range(3)]
    res = np.zeros(need, dtype=np.int64)
    for s in range(5):
        acc = sum(pa[i] * pb[s - i] for i in range(3) if 0 <= s - i < 3)
        part = np.rint(np.fft.irfft(acc, size)[:need]).astype(np.int64) % MOD
        res = (res + part * pow(2, 10 * s, MOD)) % MOD
    return res


def power_trunc(p, k, h):
    result = np.zeros(h, dtype=np.int64)
    result[0] = 1
    base = p[:h].copy()
    while k:
        if k & 1:
            result = mul(result, base)[:h]
        k >>= 1
        if k:
            base = mul(base, base)[:h]
    return result


def fold(a, L):
    out = np.zeros(L, dtype=np.int64)
    for start in range(0, len(a), L):
        chunk = a[start:start + L]
        out[:len(chunk)] = (out[:len(chunk)] + chunk) % MOD
    return out


def power_cyclic(p, k, L):
    result = np.zeros(L, dtype=np.int64)
    result[0] = 1
    base = fold(p, L)
    while k:
        if k & 1:
            result = fold(mul(result, base), L)
        k >>= 1
        if k:
            base = fold(mul(base, base), L)
    return result


def main():
    data = sys.stdin.buffer.read().split()
    n, m, k = int(data[0]), int(data[1]), int(data[2])
    f = [int(x) - 1 for x in data[3:3 + n]]
    p = np.array([int(x) % MOD for x in data[3 + n:3 + n + m]], dtype=np.int64)

    # cycles
    state = [0] * n
    on_cycle = [False] * n
    cycles = []
    for s in range(n):
        path = []
        v = s
        while state[v] == 0:
            state[v] = 1
            path.append(v)
            v = f[v]
        if state[v] == 1:
            cyc = path[path.index(v):]
            cycles.append(cyc)
            for u in cyc:
                on_cycle[u] = True
        for u in path:
            state[u] = 2
    children = [[] for _ in range(n)]
    for v in range(n):
        if not on_cycle[v]:
            children[f[v]].append(v)
    # heights (post-order over the hanging trees)
    height = [0] * n
    order = []
    for c in range(n):
        if on_cycle[c]:
            stack = [c]
            while stack:
                v = stack.pop()
                order.append(v)
                stack.extend(children[v])
    for v in reversed(order):
        for w in children[v]:
            height[v] = max(height[v], height[w] + 1)
    H = max(height) + 1
    Q = power_trunc(np.concatenate([p, np.zeros(max(0, H - m), dtype=np.int64)]), k, H)

    # long-path decomposition: positions in one buffer
    pos = [0] * n
    nxt_free = 0
    for c in range(n):
        if not on_cycle[c]:
            continue
        stack = [c]
        while stack:
            top = stack.pop()
            v = top
            while True:          # walk the long path from `top`
                pos[v] = nxt_free
                nxt_free += 1
                if not children[v]:
                    break
                heavy = max(children[v], key=lambda w: height[w])
                for w in children[v]:
                    if w != heavy:
                        stack.append(w)
                v = heavy
    buf = np.zeros(n, dtype=np.int64)
    res = np.zeros(n, dtype=np.int64)
    root_counts = {}
    for v in reversed(order):
        pv = pos[v]
        buf[pv] += 1
        if children[v]:
            heavy = max(children[v], key=lambda w: height[w])
            for w in children[v]:
                if w != heavy:
                    hw = height[w] + 1
                    buf[pv + 1:pv + 1 + hw] += buf[pos[w]:pos[w] + hw]
        cnt = buf[pv:pv + height[v] + 1]
        if on_cycle[v]:
            root_counts[v] = cnt.copy()
        else:
            res[v] = int(np.dot(cnt % MOD, Q[:len(cnt)]) % MOD)

    cache = {}
    for cyc in cycles:
        L = len(cyc)
        if L not in cache:
            cache[L] = power_cyclic(p, k, L)
        SL = cache[L]
        A = np.zeros(L, dtype=np.int64)
        corr = np.zeros(L, dtype=np.int64)
        for i, c in enumerate(cyc):
            cnt = root_counts[c]
            h = len(cnt) - 1
            idx = (i - np.arange(h + 1)) % L
            np.add.at(A, idx, cnt)
            if h > 0:
                cc = mul(cnt[::-1] % MOD, Q[:h + 1])      # cc[h - s] = sum_t cnt[t] Q[t - s]
                s = np.arange(1, h + 1)
                np.add.at(corr, (i - s) % L, cc[h - s])
                corr %= MOD
        full = fold(mul(A % MOD, SL), L)
        for i, c in enumerate(cyc):
            res[c] = (full[i] - corr[i]) % MOD
    inv_n = pow(n, MOD - 2, MOD)
    print('\n'.join(str(int(v) * inv_n % MOD) for v in res))


main()
```

**Watch out.**
- **Why not simulate.** Simulating `k` turns costs O(k·n·m). The polynomial view collapses all the turns into one `Q = P^k`.
- **Exact FFT.** Splitting the values into three 10-bit pieces keeps every float FFT coefficient below about 10¹², so rounding is exact.
- **Speed.** The tree dot products cost Σ heights, which is fine with NumPy. CPython is still slow on the largest inputs.

```stdin
4 5 1
2 3 2 4
332748118 332748118 332748118 0 0
```

```stdout
582309206
332748118
332748118
748683265
```
