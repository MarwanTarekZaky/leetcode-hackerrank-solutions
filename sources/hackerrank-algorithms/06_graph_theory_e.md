## Graph Theory

### Huarongdao

**Problem.** On an `N × M` board of movable and fixed blocks with one empty cell, slide blocks into the empty cell (1 second each), or cheat: lift any movable block (not Cao Cao) into the empty cell for `K` seconds. Find the minimum time to bring Cao Cao from `S` to `T`.

**Idea.** The classic "Huarongdao" state graph.
- **States.** Cao Cao can only move by swapping with the empty cell next to it, so the state is `(Cao Cao's cell, side of the empty cell)`, which gives 4 states per cell.
- **Transitions.** There are two:
  - **Swap.** Cao Cao steps into the empty cell, costing 1. The empty cell ends up on the opposite side.
  - **Walk round.** The empty cell moves to another side of Cao Cao without passing through him, at its shortest distance. Cheating moves the empty cell anywhere for `K`, so every such distance is capped at `K`.
- **Bounded searches.** Because of that cap, each empty-cell BFS stops at radius `K` (`K ≤ 15`), which keeps the per-state work small.
- **Search.** Run Dijkstra over the states, computing (and caching) the bounded BFS for each visited `(cell, side)`.

**Steps.**
1. If `S = T`, answer 0. Otherwise the start costs are `min(bfs(E → side of S, avoiding S), K)` for each movable side.
2. Run Dijkstra: swap edges cost 1; walk-round edges cost the capped BFS distance between sides, computed lazily per `(cell, side)`.
3. The answer is the best state whose Cao Cao cell is `T`, or -1.

```python
import os
from collections import deque
from heapq import heappop, heappush

DIRS = ((-1, 0), (1, 0), (0, -1), (0, 1))


def huarongdao(k, board, queries):
    n, m = len(board), len(board[0])

    def free(r, c):
        return 0 <= r < n and 0 <= c < m and board[r][c] == 1

    def bfs(sr, sc, br, bc, targets):
        """Capped distances from (sr, sc) to each target, never entering (br, bc)."""
        res = {t: k for t in targets}
        dist = {(sr, sc): 0}
        if (sr, sc) in res:
            res[(sr, sc)] = 0
        queue = deque([(sr, sc)])
        while queue:
            r, c = queue.popleft()
            d = dist[(r, c)]
            if d + 1 >= k:
                break
            for dr, dc in DIRS:
                nr, nc = r + dr, c + dc
                if free(nr, nc) and (nr, nc) != (br, bc) and (nr, nc) not in dist:
                    dist[(nr, nc)] = d + 1
                    if (nr, nc) in res:
                        res[(nr, nc)] = min(res[(nr, nc)], d + 1)
                    queue.append((nr, nc))
        return res

    cache = {}

    def around(r, c, side):
        key = (r, c, side)
        if key not in cache:
            er, ec = r + DIRS[side][0], c + DIRS[side][1]
            sides = [(s, (r + dr, c + dc)) for s, (dr, dc) in enumerate(DIRS) if s != side and free(r + dr, c + dc)]
            dist = bfs(er, ec, r, c, [p for _, p in sides])
            cache[key] = [(s, dist[p]) for s, p in sides]
        return cache[key]

    out = []
    for ex, ey, sx, sy, tx, ty in queries:
        er, ec, sr, sc, tr, tc = ex - 1, ey - 1, sx - 1, sy - 1, tx - 1, ty - 1
        if (sr, sc) == (tr, tc):
            out.append(0)
            continue
        sides = [(s, (sr + dr, sc + dc)) for s, (dr, dc) in enumerate(DIRS) if free(sr + dr, sc + dc)]
        start = bfs(er, ec, sr, sc, [p for _, p in sides])
        best = {}
        heap = []
        for s, p in sides:
            best[(sr, sc, s)] = start[p]
            heappush(heap, (start[p], sr, sc, s))
        answer = -1
        while heap:
            d, r, c, s = heappop(heap)
            if d > best.get((r, c, s), float('inf')):
                continue
            if (r, c) == (tr, tc):
                answer = d
                break
            nr, nc = r + DIRS[s][0], c + DIRS[s][1]
            moves = [((nr, nc, s ^ 1), d + 1)]
            moves += [((r, c, s2), d + w) for s2, w in around(r, c, s)]
            for state, nd in moves:
                if nd < best.get(state, float('inf')):
                    best[state] = nd
                    heappush(heap, (nd,) + state)
        out.append(answer)
    return out


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m, k, q = map(int, input().split())
    board = [list(map(int, input().split())) for _ in range(n)]
    queries = [list(map(int, input().split())) for _ in range(q)]
    fptr.write('\n'.join(map(str, huarongdao(k, board, queries))) + '\n')
    fptr.close()
```

**Watch out.**
- **Pairing the sides.** The direction indices are paired so that `s ^ 1` is the opposite side: up/down are 0/1, left/right are 2/3.
- **Cheat cost.** A cheat costs `K` even when the empty cell is boxed in, so walls only matter for distances below `K`.
- **Cao Cao blocks the BFS.** The empty-cell searches must treat Cao Cao's cell as blocked.

```stdin
5 5 12 1
1 1 1 1 1
1 1 1 1 1
0 1 1 1 1
1 1 1 1 1
0 1 0 1 1
1 5 4 3 4 1
```

```stdout
20
```

### Training the army

**Problem.** `C_i` people know skill `i`. Each wizard can turn a person's skill from his list `A` into one from his list `B`, using each list entry at most once. Maximise the number of skills that at least one person knows.

**Idea.** Max flow, where people are units of flow:
- **Into and out of skills.** `source → skill i` with capacity `C_i`. `skill i → sink` with capacity 1, so a skill counts once if anyone ends there.
- **Wizards.** A wizard is a node: `a → wizard` (capacity 1) for each `a` in `A`, and `wizard → b` (capacity 1) for each `b` in `B`.

People can be retrained repeatedly by passing through several wizards. The max flow is the number of distinct skills reached.

**Steps.**
1. Build the network with nodes source, skills, wizards and sink.
2. Run Dinic and print the flow.

```python
import sys
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


def main():
    data = sys.stdin.read().split()
    pos = 0
    n, t = int(data[0]), int(data[1])
    pos = 2
    c = list(map(int, data[pos:pos + n]))
    pos += n
    sink = n + t + 1
    net = Dinic(n + t + 2)
    for i in range(n):
        if c[i]:
            net.add(0, 1 + i, c[i])
        net.add(1 + i, sink, 1)
    for w in range(t):
        node = n + 1 + w
        la = int(data[pos]); pos += 1
        for a in data[pos:pos + la]:
            net.add(int(a), node, 1)
        pos += la
        lb = int(data[pos]); pos += 1
        for b in data[pos:pos + lb]:
            net.add(node, int(b), 1)
        pos += lb
    print(net.max_flow(0, sink))


main()
```

**Watch out.** HackerRank's printed sample output says `2`, but its own explanation walks through a plan that reaches 3 skills (keep one person on skill 1, turn one into 3 with the first wizard and one into 2 with the third). The flow model gives 3, matching the explanation. The wizard node must sit between `A` and `B` so that each list entry is used at most once.

```stdin
3 3
3 0 0
1 1
2 2 3
1 2
1 3
1 1
1 2
```

```stdout
3
```

### Jim and his LAN Party

**Problem.** Wires are added one by one. For each game, print the wire after which all its players are connected (0 for a solo player, -1 if never).

**Idea.** Union-find where every component keeps a map `game → number of its players inside`. When merging, fold the smaller map into the larger (small-to-large). When a game's count reaches its total number of players, that game finishes at the current wire. Each player's entry moves O(log n) times.

**Steps.**
1. Count `total[g]`; games with one player answer 0, the rest start at -1.
2. For wire `i`, union the two roots and merge the smaller map into the larger. Record `i` for every game whose count reaches `total`.

```python
import os


def lanParty(games, wires, m):
    n = len(games)
    total = [0] * (m + 1)
    for g in games:
        total[g] += 1
    ans = [0 if total[g] == 1 else -1 for g in range(m + 1)]
    parent = list(range(n + 1))
    bag = [None] + [{g: 1} for g in games]

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i, (u, v) in enumerate(wires, 1):
        ru, rv = find(u), find(v)
        if ru == rv:
            continue
        if len(bag[ru]) < len(bag[rv]):
            ru, rv = rv, ru
        big = bag[ru]
        for g, c in bag[rv].items():
            big[g] = big.get(g, 0) + c
            if big[g] == total[g] and ans[g] == -1:
                ans[g] = i
        bag[rv] = None
        parent[rv] = ru
    return ans[1:]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m, q = map(int, input().split())
    games = list(map(int, input().split()))
    wires = [list(map(int, input().split())) for _ in range(q)]
    fptr.write('\n'.join(map(str, lanParty(games, wires, m))) + '\n')
    fptr.close()
```

**Watch out.** Checking every game after each wire is O(Q·M). The completion test happens only while merging, which is exactly when a count can change. A game with a single player is ready at wire 0.

```stdin
5 2 4
1 2 2 2 1
1 2
2 3
1 5
4 5
```

```stdout
3
4
```

### Travel in HackerLand

**Problem.** For queries `(x, y, k)`, find the smallest possible "maximum road crowd" over walks from `x` to `y` that see at least `k` distinct building types (walks may repeat cities).

**Idea.** A Kruskal reconstruction tree.
- **Building it.** Add roads in increasing crowd order. Each time two components merge, create a new tree node with that crowd value whose children are the two components. Also store its number of distinct building types, merged small-to-large.
- **What a walk can use.** A walk with maximum crowd `c` can wander over the whole component formed by roads of crowd at most `c`. So the answer is the lowest node above both `x` and `y` that sees at least `k` types.
- **Answering.** That means the LCA of `x` and `y` (where they first join), then climbing to the first ancestor with enough types. Counts only grow upward, so binary lifting finds it.

**Steps.**
1. Leaves are cities (value 0, 1 type). Run Kruskal, creating merge nodes with `(crowd, distinct types)`.
2. Build binary lifting over the forest (a root points to itself).
3. For each query, find the LCA (or -1 if `x` and `y` are in different trees), climb to the first node with `types ≥ k`, and print its value or -1.

```python
import sys


def main():
    data = sys.stdin.buffer.read().split()
    n, m, q = int(data[0]), int(data[1]), int(data[2])
    types = data[3:3 + n]
    pos = 3 + n
    roads = []
    for _ in range(m):
        x, y, u = int(data[pos]), int(data[pos + 1]), int(data[pos + 2])
        pos += 3
        roads.append((u, x - 1, y - 1))
    roads.sort()
    total = 2 * n
    par = list(range(total))
    val = [0] * total
    cnt = [1] * total
    dsu = list(range(total))
    bags = [{t} for t in types] + [None] * n

    def find(x):
        while dsu[x] != x:
            dsu[x] = dsu[dsu[x]]
            x = dsu[x]
        return x

    nxt = n
    for u, x, y in roads:
        rx, ry = find(x), find(y)
        if rx == ry:
            continue
        if len(bags[rx]) < len(bags[ry]):
            rx, ry = ry, rx
        bags[rx] |= bags[ry]
        bags[nxt], bags[rx], bags[ry] = bags[rx], None, None
        val[nxt], cnt[nxt] = u, len(bags[nxt])
        par[rx] = par[ry] = nxt
        dsu[rx] = dsu[ry] = nxt
        nxt += 1
    size = nxt
    depth = [0] * size
    for v in range(size - 1, -1, -1):
        if par[v] != v:
            depth[v] = depth[par[v]] + 1
    LOG = max(1, size.bit_length())
    up = [par[:size]]
    for _ in range(1, LOG):
        prev = up[-1]
        up.append([prev[prev[v]] for v in range(size)])

    out = []
    for _ in range(q):
        x, y, k = int(data[pos]) - 1, int(data[pos + 1]) - 1, int(data[pos + 2])
        pos += 3
        if find(x) != find(y):
            out.append(-1)
            continue
        a, b = x, y
        if depth[a] < depth[b]:
            a, b = b, a
        diff = depth[a] - depth[b]
        for j in range(LOG):
            if diff >> j & 1:
                a = up[j][a]
        if a != b:
            for j in range(LOG - 1, -1, -1):
                if up[j][a] != up[j][b]:
                    a, b = up[j][a], up[j][b]
            a = up[0][a]
        if cnt[a] < k:
            for j in range(LOG - 1, -1, -1):
                if cnt[up[j][a]] < k:
                    a = up[j][a]
            a = up[0][a]
        out.append(val[a] if cnt[a] >= k else -1)
    print('\n'.join(map(str, out)))


main()
```

**Watch out.**
- **Root sentinel.** A root is its own parent, so jumping past it stays put; the final `cnt[a] ≥ k` check catches "never enough types".
- **Small-to-large.** Without it, merging the type sets can be quadratic.
- **A single city.** For `x = y` with `k = 1`, the empty walk works, so the answer is 0.

```stdin
7 6 1
1 1 4 5 1 3 2
1 2 3
2 6 2
2 3 4
3 4 3
2 4 9
5 7 9
1 2 4
```

```stdout
4
```

### Alex vs Fedor

**Problem.** Fedor picks a uniformly random spanning tree of a multigraph. Print, as a reduced fraction, the probability that it is a minimum spanning tree.

**Idea.** The answer is `#MSTs / #spanning trees`.
- **Counting spanning trees.** Kirchhoff's matrix-tree theorem: the count is any cofactor of the Laplacian.
- **Exact arithmetic.** Bareiss elimination keeps every intermediate value an integer, so the determinant is exact.
- **Counting MSTs.** Process edge weights in increasing order. All MSTs agree on which components exist after each weight class, so the count factorises. For each class, contract the components formed by lighter edges; in the resulting multigraph, the class's edges must form a spanning forest of each connected piece. Multiply the matrix-tree counts of those pieces together.

**Steps.**
1. `det(L)` with Bareiss (on the Laplacian minus one row and column) gives the spanning-tree count.
2. Run Kruskal by weight class. For each class, build a Laplacian per connected group of contracted components, multiply in its cofactor, then union the class.
3. Reduce `mst / total` with `gcd`.

```python
import os
from math import gcd


def det(mat):
    """Exact integer determinant (Bareiss)."""
    a = [row[:] for row in mat]
    n = len(a)
    if n == 0:
        return 1
    sign, prev = 1, 1
    for k in range(n - 1):
        if a[k][k] == 0:
            for i in range(k + 1, n):
                if a[i][k] != 0:
                    a[k], a[i] = a[i], a[k]
                    sign = -sign
                    break
            else:
                return 0
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                a[i][j] = (a[i][j] * a[k][k] - a[i][k] * a[k][j]) // prev
        prev = a[k][k]
    return sign * a[n - 1][n - 1]


def trees(nodes, edges):
    """Spanning trees of a connected multigraph on `nodes` (list of labels)."""
    idx = {v: i for i, v in enumerate(nodes)}
    k = len(nodes)
    lap = [[0] * k for _ in range(k)]
    for u, v in edges:
        if u == v:
            continue
        a, b = idx[u], idx[v]
        lap[a][a] += 1
        lap[b][b] += 1
        lap[a][b] -= 1
        lap[b][a] -= 1
    return det([row[1:] for row in lap[1:]])


def alexFedor(graph_nodes, graph_from, graph_to, graph_weight):
    n = graph_nodes
    edges = list(zip(graph_from, graph_to, graph_weight))
    total = trees(list(range(1, n + 1)), [(u, v) for u, v, _ in edges])
    parent = list(range(n + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst = 1
    for w in sorted({e[2] for e in edges}):
        group = [(find(u), find(v)) for u, v, ww in edges if ww == w and find(u) != find(v)]
        comp = {}

        def cf(x):
            while comp.get(x, x) != x:
                x = comp[x]
            return x

        for a, b in group:
            comp.setdefault(a, a)
            comp.setdefault(b, b)
            ra, rb = cf(a), cf(b)
            if ra != rb:
                comp[ra] = rb
        pieces = {}
        for a in comp:
            pieces.setdefault(cf(a), []).append(a)
        for root, nodes in pieces.items():
            mst *= trees(nodes, [(a, b) for a, b in group if cf(a) == root])
        for a, b in group:
            parent[find(a)] = find(b)
    g = gcd(mst, total)
    return f"{mst // g}/{total // g}"


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m = map(int, input().split())
    gf, gt, gw = [0] * m, [0] * m, [0] * m
    for i in range(m):
        gf[i], gt[i], gw[i] = map(int, input().split())
    fptr.write(alexFedor(n, gf, gt, gw) + '\n')
    fptr.close()
```

**Watch out.** Floating-point determinants lose precision long before 10¹⁸, so keep the arithmetic exact. Parallel edges between the same pair are distinct edges and both count in the Laplacian. A self-loop never belongs to a spanning tree.

```stdin
4 4
1 2 1
2 3 4
3 4 3
4 1 2
```

```stdout
1/4
```

### Vertical Paths

**Problem.** In a rooted tree, each edge can carry at most `d_i` chosen paths. Each candidate path runs from an ancestor `u` down to a descendant `v` and has value `c`. Choose paths to maximise the total value.

**Idea.** Model it as a min-cost circulation.
- **The network.** Each tree edge becomes an upward arc `child → parent` with capacity `d` and cost 0. Each path becomes a downward "jump" `u → v` with capacity 1 and cost `−c`.
- **Why it matches.** The only way for the flow of a jump to return upward is through the subtree's boundary edges. So the flow on a tree edge equals the number of chosen paths covering it, and the capacity is respected.
- **Removing negative costs.** First saturate every jump: gain all the `c`, and record an excess at `v` and a deficit at `u`. Then send the excesses to the deficits at minimum cost in the residual graph, where undoing a jump costs `+c` and tree arcs are free. The answer is `Σc − min cost`.
- **Solving.** Successive shortest paths with Dijkstra and potentials, one unit per path.

**Steps.**
1. Root the tree at 1; add the arcs `child → parent` (capacity `d`, cost 0) and the reverse jumps `v → u` (capacity 1, cost `c`).
2. Super source → each `v` (one unit per path), each `u` → super sink.
3. Push `m` units with min-cost flow and return `Σc − cost`.

```python
import os
from collections import deque
from heapq import heappop, heappush


def verticalPaths(n, paths, edges):
    adj = [[] for _ in range(n + 1)]
    for a, b, d in paths:
        adj[a].append((b, d))
        adj[b].append((a, d))
    parent, cap_up = [0] * (n + 1), [0] * (n + 1)
    seen = [False] * (n + 1)
    seen[1] = True
    queue = deque([1])
    while queue:
        u = queue.popleft()
        for v, d in adj[u]:
            if not seen[v]:
                seen[v] = True
                parent[v], cap_up[v] = u, d
                queue.append(v)
    S, T = 0, n + 1
    g = [[] for _ in range(n + 2)]

    def add(u, v, cap, cost):
        g[u].append([v, cap, cost, len(g[v])])
        g[v].append([u, 0, -cost, len(g[u]) - 1])

    for v in range(2, n + 1):
        add(v, parent[v], cap_up[v], 0)
    gain = 0
    for u, v, c in edges:
        gain += c
        add(v, u, 1, c)
        add(S, v, 1, 0)
        add(u, T, 1, 0)
    pot = [0] * (n + 2)
    cost = 0
    inf = float('inf')
    for _ in range(len(edges)):
        dist = [inf] * (n + 2)
        prev = [None] * (n + 2)
        dist[S] = 0
        heap = [(0, S)]
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
        if dist[T] == inf:
            break
        for v in range(n + 2):
            if dist[v] < inf:
                pot[v] += dist[v]
        v = T
        while v != S:
            u, i = prev[v]
            e = g[u][i]
            e[1] -= 1
            g[v][e[3]][1] += 1
            cost += e[2]
            v = u
    return gain - cost


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n, m = map(int, input().split())
        paths = [list(map(int, input().split())) for _ in range(n - 1)]
        edges = [list(map(int, input().split())) for _ in range(m)]
        fptr.write(str(verticalPaths(n, paths, edges)) + '\n')
    fptr.close()
```

**Watch out.** Every unit can always be routed back through its own reverse jump (cost `c`, which means "don't take this path"), so all `m` units are always sent. HackerRank's starter names the tree edges `paths` and the candidate paths `edges`; the code keeps those names.

```stdin
1
8 8
1 2 3
1 3 1
2 4 5
2 5 1
2 6 1
3 7 2
4 8 1
1 2 3
2 8 5
1 8 7
1 5 8
1 6 10
3 7 5
1 7 6
1 7 6
```

```stdout
37
```

### Drive

**Problem.** A bus visits stations `1..n` in order and waits at each one for its last commuter. `K` units of nitro, spread over the segments, shorten a segment by one second each. Minimise the commuters' total travel time.

**Idea.** The classic greedy ("sightseeing bus" with accelerators).
- **What a unit gains.** Speeding up segment `i` makes the bus arrive one second earlier at stations `i+1 .. r_i`, where `r_i` is the first later station at which the bus already waits (its arrival is ≤ the last commuter's arrival there). Waiting absorbs the saving. So one unit on `i` saves one second for every commuter getting off in `(i, r_i]`.
- **Spending.** Repeatedly pick the segment with the largest gain and spend as many units as possible at once. The batch stops when nitro runs out, the segment reaches 0, or some intermediate station's spare time (arrival − last commuter) hits 0, which shrinks `r_i`.

**Steps.**
1. `last[i]` = latest commuter arrival at station `i`; `off[j]` = commuters getting off at `j`.
2. Loop: simulate the arrivals and compute `r_i` and the gain of every segment with `d_i > 0`. Take the best positive gain, apply `amount = min(K, d_i, min slack in (i, r_i))`, then repeat.
3. Finally simulate once more and return `Σ (arrival[e] − t)`.

```python
import os


def drive(n, k, d, commuters):
    d = d[:]
    last = [0] * (n + 1)
    off = [0] * (n + 2)
    for t, s, e in commuters:
        last[s] = max(last[s], t)
        off[e] += 1

    def arrivals():
        arr = [0] * (n + 1)
        for i in range(1, n):
            arr[i + 1] = max(arr[i], last[i]) + d[i - 1]
        return arr

    while k > 0:
        arr = arrivals()
        best_gain, best = 0, None
        reach = n
        gain = 0
        slack = float('inf')
        # walk segments right to left, tracking r_i, its gain and the slack before it
        for i in range(n - 1, 0, -1):
            j = i + 1
            if j == n or arr[j] <= last[j]:
                reach, gain, slack = j, off[j], float('inf')
            else:
                gain += off[j]
                slack = min(slack, arr[j] - last[j])
            if d[i - 1] > 0 and gain > best_gain:
                best_gain, best = gain, (i, slack)
        if best is None:
            break
        i, sl = best
        amount = min(k, d[i - 1], sl)
        d[i - 1] -= amount
        k -= amount
    arr = arrivals()
    return sum(arr[e] - t for t, s, e in commuters)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m, k = map(int, input().split())
    d = list(map(int, input().split()))
    commuters = [list(map(int, input().split())) for _ in range(m)]
    fptr.write(str(drive(n, k, d, commuters)) + '\n')
    fptr.close()
```

**Watch out.** The scan runs right to left, so the "reach" and "slack" of segment `i` build on those of `i+1`. The `j == n` / waiting check resets them. Spending units one at a time is too slow when `K` is huge, so spend in batches up to the next structural change.

```stdin
3 3 2
1 4
1 1 3
2 1 2
5 2 3
```

```stdout
9
```

### Travelling Salesman in a Grid

**Problem.** Find the cheapest Hamiltonian cycle through every cell of an `m × n` grid (at most 10 × 10) with weighted edges between neighbours, or print 0 if there is none.

**Idea.** Plug (broken-profile) DP.
- **The frontier.** Scan cells row by row. The frontier holds `n + 1` "plugs": the edges crossing from processed to unprocessed cells. Each plug is 0 (no edge), 1 (left end of a path piece) or 2 (right end). This bracket encoding records which loose ends belong together.
- **Each cell.** Every cell must end with degree 2. At each cell look at its left plug `a` and up plug `b`:
  - **Both empty.** Start a new piece going right and down.
  - **One set.** Continue it either right or down.
  - **Two lefts or two rights.** Join them and re-label the matching bracket.
  - **Right then left.** Simply join.
  - **Left then right.** That closes the loop, which is only allowed at the very last cell.
- **Cost.** Add an edge's cost when the edge is created.

**Steps.**
1. Store states as tuples in a dictionary `state → min cost`, and shift the profile at the end of each row.
2. At the last cell, the only valid finish is closing `(1, 2)` with nothing else open.

```python
import os


def tspGrid(horizontal, vertical):
    m, n = len(horizontal), len(horizontal[0]) + 1 if horizontal[0] else 1
    if m * n < 4 or (m * n) % 2:
        return 0
    states = {(0,) * (n + 1): 0}
    best = None
    for i in range(m):
        for j in range(n):
            nxt = {}

            def push(st, cost):
                if cost < nxt.get(st, float('inf')):
                    nxt[st] = cost

            for st, cost in states.items():
                a, b = st[j], st[j + 1]
                can_down, can_right = i + 1 < m, j + 1 < n
                down_c = vertical[i][j] if can_down else 0
                right_c = horizontal[i][j] if can_right else 0
                s = list(st)
                if a == 0 and b == 0:
                    if can_down and can_right:
                        s[j], s[j + 1] = 1, 2
                        push(tuple(s), cost + down_c + right_c)
                elif a == 0 or b == 0:
                    x = a or b
                    if can_down:
                        s[j], s[j + 1] = x, 0
                        push(tuple(s), cost + down_c)
                    if can_right:
                        s[j], s[j + 1] = 0, x
                        push(tuple(s), cost + right_c)
                else:
                    s[j] = s[j + 1] = 0
                    if a == 1 and b == 1:
                        depth = 0
                        for p in range(j + 2, n + 1):
                            if s[p] == 1:
                                depth += 1
                            elif s[p] == 2:
                                if depth == 0:
                                    s[p] = 1
                                    break
                                depth -= 1
                        push(tuple(s), cost)
                    elif a == 2 and b == 2:
                        depth = 0
                        for p in range(j - 1, -1, -1):
                            if s[p] == 2:
                                depth += 1
                            elif s[p] == 1:
                                if depth == 0:
                                    s[p] = 2
                                    break
                                depth -= 1
                        push(tuple(s), cost)
                    elif a == 2 and b == 1:
                        push(tuple(s), cost)
                    elif i == m - 1 and j == n - 1 and not any(s):
                        best = cost if best is None else min(best, cost)
            states = nxt
        states = {(0,) + st[:n]: c for st, c in states.items() if st[n] == 0}
    return best if best is not None else 0


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    m, n = map(int, input().split())
    horizontal = [list(map(int, input().split())) for _ in range(m)]
    vertical = [list(map(int, input().split())) for _ in range(m - 1)]
    fptr.write(str(tspGrid(horizontal, vertical)) + '\n')
    fptr.close()
```

**Watch out.**
- **Parity.** A grid graph is bipartite, so a grid with an odd number of cells has no Hamiltonian cycle; neither does a single row or column.
- **Bracket matching.** When joining two left (or two right) ends, the bracket matching the other end must be re-labelled, or later merges connect the wrong pieces.

```stdin
2 2
5
8
6 7
```

```stdout
26
```
