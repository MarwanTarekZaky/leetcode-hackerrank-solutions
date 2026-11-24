## Trees

### Kitty's Calculations on a Tree

**Problem.** For each query set of nodes, compute `Σ u·v·dist(u, v)` over the unordered pairs of the set, modulo 10⁹+7. There are `n ≤ 2·10⁵` nodes and `Σ k ≤ 2·10⁵`.

**Idea.** Split the sum by edges. An edge contributes `(Σ labels below it) · (Σ labels above it)` times its length. Only the edges of the **virtual tree** of the query set matter: the set plus the LCAs of nodes adjacent in DFS order.
- **Virtual parent.** Sort the closed set by entry time. Then the virtual parent of each node is the LCA of it and the previous node.
- **Contribution.** Walk the virtual nodes in reverse entry order, accumulating each node's subtree label sum `s` into its parent. Each virtual edge adds `(depth difference) · s · (total − s)`.
- **LCA.** An Euler tour plus a sparse table, queried **in one vectorised batch for all queries** (once for the closing LCAs, once for the virtual parents). This avoids per-query NumPy overhead.

**Steps.**
1. Iterative Euler tour; sparse table over the depths.
2. Sort every set by entry time; batch-LCA the neighbours; close the sets; batch-LCA again for the parents.
3. Per query: the subtree-sum sweep.

```python
import sys

import numpy as np

MOD = 10 ** 9 + 7


def build_lca(n, adj, root=1):
    first = [0] * (n + 1)
    depth = [0] * (n + 1)
    parent = [0] * (n + 1)
    it = [0] * (n + 1)
    parent[root] = -1
    euler = [root]
    stack = [root]
    while stack:
        v = stack[-1]
        if it[v] < len(adj[v]):
            u = adj[v][it[v]]
            it[v] += 1
            if u != parent[v]:
                parent[u] = v
                depth[u] = depth[v] + 1
                first[u] = len(euler)
                euler.append(u)
                stack.append(u)
        else:
            stack.pop()
            if stack:
                euler.append(stack[-1])
    e = np.array(euler, dtype=np.int64)
    dep = np.array(depth, dtype=np.int64)
    ed = dep[e]
    m = len(e)
    K = max(1, m.bit_length())
    sp = np.zeros((K, m), dtype=np.int64)
    sp[0] = np.arange(m)
    for k in range(1, K):
        half = 1 << (k - 1)
        a, b = sp[k - 1][:m - half], sp[k - 1][half:]
        sp[k, :m - half] = np.where(ed[a] <= ed[b], a, b)
    log = np.zeros(m + 1, dtype=np.int64)
    log[2:] = np.floor(np.log2(np.arange(2, m + 1))).astype(np.int64)
    fa = np.array(first, dtype=np.int64)

    def lca(u, v):
        a, b = fa[u], fa[v]
        lo, hi = np.minimum(a, b), np.maximum(a, b)
        k = log[hi - lo + 1]
        x, y = sp[k, lo], sp[k, hi - (1 << k) + 1]
        return e[np.where(ed[x] <= ed[y], x, y)]
    return lca, first, depth


def main():
    data = sys.stdin.buffer.read().split()
    n, q = int(data[0]), int(data[1])
    adj = [[] for _ in range(n + 1)]
    pos = 2
    for _ in range(n - 1):
        a, b = int(data[pos]), int(data[pos + 1])
        pos += 2
        adj[a].append(b)
        adj[b].append(a)
    queries = []
    for _ in range(q):
        k = int(data[pos])
        queries.append([int(x) for x in data[pos + 1:pos + 1 + k]])
        pos += 1 + k
    lca, first, dep = build_lca(n, adj)
    key = first.__getitem__
    sq = [sorted(S, key=key) for S in queries]
    us = [v for S in sq for v in S[:-1]]
    vs = [v for S in sq for v in S[1:]]
    l1 = lca(np.array(us, dtype=np.int64), np.array(vs, dtype=np.int64)).tolist() if us else []
    closed, p = [], 0
    for S in sq:
        extra = l1[p:p + len(S) - 1]
        p += len(S) - 1
        closed.append(sorted(set(S).union(extra), key=key))
    us = [v for A in closed for v in A[:-1]]
    vs = [v for A in closed for v in A[1:]]
    par = lca(np.array(us, dtype=np.int64), np.array(vs, dtype=np.int64)).tolist() if us else []
    out, p = [], 0
    for S, A in zip(queries, closed):
        ps = par[p:p + len(A) - 1]
        p += len(A) - 1
        sub = dict.fromkeys(A, 0)
        for v in S:
            sub[v] = v
        total = sum(S)
        res = 0
        for i in range(len(A) - 1, 0, -1):
            v, pv = A[i], ps[i - 1]
            s = sub[v]
            res += (dep[v] - dep[pv]) * s * (total - s)
            sub[pv] += s
        out.append(res % MOD)
    print('\n'.join(map(str, out)))


main()
```

**Watch out.** A set with one node gives 0. Using the virtual tree keeps each query at `O(k log k)` instead of `O(n)`. The tree can be a long path, so the Euler tour is built with an explicit stack.

```stdin
7 3
1 2
1 3
1 4
3 5
3 6
3 7
2
2 4
1
5
3
2 4 5
```

```stdout
16
0
106
```

### Is This a Binary Search Tree?

**Problem.** Decide whether a binary tree is a BST with **strictly** increasing values (no duplicates).

**Idea.** A tree is a strict BST exactly when its inorder traversal is strictly increasing. Run an iterative inorder and compare each value with the previous one. On HackerRank, a hidden stub builds the tree. For local testing, this program reads the tree in array (heap) form: `n` values, where node `i` has children `2i+1` and `2i+2`.

**Steps.**
1. Build the nodes from the array form.
2. Iterative inorder; fail on any value `≤` the previous one.

```python
class node:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None


def check_binary_search_tree_(root):
    prev = None
    stack = []
    cur = root
    while cur or stack:
        while cur:
            stack.append(cur)
            cur = cur.left
        nd = stack.pop()
        if prev is not None and nd.data <= prev:
            return False
        prev = nd.data
        cur = nd.right
    return True


n = int(input())
vals = list(map(int, input().split()))
nodes = [node(v) for v in vals]
for i in range(n):
    if 2 * i + 1 < n:
        nodes[i].left = nodes[2 * i + 1]
    if 2 * i + 2 < n:
        nodes[i].right = nodes[2 * i + 2]
print('Yes' if check_binary_search_tree_(nodes[0]) else 'No')
```

**Watch out.** Checking only parent against children is not enough. A node deep in the left subtree must also be smaller than every ancestor it sits left of, and the inorder test covers that automatically.

```stdin
7
4 2 6 1 3 5 7
```

```stdout
Yes
```

### Square-Ten Tree

**Problem.** Level 0 holds single elements; level `k ≥ 1` holds aligned blocks of length `10^{2^{k−1}}`. Split `[L, R]` (numbers with up to 10⁶ digits) into the fewest blocks, and print the sequence of levels in run-length form.

**Idea.** Block sizes are powers of ten, each one dividing the next. So the minimal cover is the usual greedy for aligned hierarchies:
- **Climbing.** From `a = L − 1`, at each level take level-`k` blocks until `a` reaches a multiple of the next level's size, as long as that stays within `R`.
- **Descending.** Once the next alignment would pass `R`, go back down: at each level take as many blocks as fit into `R − a`.

All the arithmetic is on numbers with a million digits. Python's `decimal` handles them with exact integer arithmetic in near-linear time, and `scaleb` multiplies or divides by powers of ten for free. Equal neighbouring levels are merged, adding their (big) counts.

**Steps.**
1. Set the `decimal` precision above the input length.
2. Climb, then descend, collecting `(level, count)` pairs; merge equal neighbours; print.

```python
import sys
from decimal import Decimal, getcontext, ROUND_CEILING, ROUND_FLOOR, MAX_EMAX, MIN_EMIN


def main():
    Ls, Rs = sys.stdin.read().split()[:2]
    digits = max(len(Ls), len(Rs)) + 10
    ctx = getcontext()
    ctx.prec = digits + 10
    ctx.Emax, ctx.Emin = MAX_EMAX, MIN_EMIN
    a = Decimal(Ls) - 1
    b = Decimal(Rs)
    exps = [0, 1]                                  # level k has blocks of 10**exps[k]
    while exps[-1] < digits:
        exps.append(exps[-1] * 2)
    seq = []
    k = 0
    while True:                                    # climb
        e = exps[k + 1]
        up = a.scaleb(-e).to_integral_value(rounding=ROUND_CEILING).scaleb(e)
        if up == a:
            if a + Decimal(1).scaleb(e) > b:       # not even one block of the next level fits
                break
        elif up > b:
            break
        else:
            seq.append((k, (up - a).scaleb(-exps[k])))
        a = up
        k += 1
    d = b - a
    for lev in range(k, -1, -1):                   # descend
        c = d.scaleb(-exps[lev]).to_integral_value(rounding=ROUND_FLOOR)
        if c > 0:
            seq.append((lev, c))
            d -= c.scaleb(exps[lev])
    merged = []
    for lev, c in seq:
        if merged and merged[-1][0] == lev:
            merged[-1] = (lev, merged[-1][1] + c)
        else:
            merged.append((lev, c))
    out = [str(len(merged))]
    for lev, c in merged:
        out.append(f"{lev} {format(c.quantize(Decimal(1)), 'f')}")
    print('\n'.join(out))


main()
```

**Watch out.**
- **Big integers.** Converting million-digit numbers with plain `int()` and `str()` is quadratic in older Pythons; `decimal` avoids that.
- **Merging runs.** The climbing and descending phases can produce two neighbouring runs of the same level, which must become one run with the counts added.
- **Testing.** Checked against a brute-force minimum-cover DP for small `L, R`.

```stdin
1
10
```

```stdout
1
1 1
```

### Balanced Forest

**Problem.** Add one node with the smallest value `w` so that cutting two edges leaves three trees with equal sums. Print `w`, or `-1` if impossible.

**Idea.** Let `S` be the total and `s_v` the subtree sums. In the end two parts equal some `x` and the third is `S − 2x ≤ x`; the new node tops up the third part, so `w = 3x − S`. For each non-root `v`, two roles are possible:
- **`v` is one of the two equal parts (`x = s_v`, `3x ≥ S`).** The other part `x` is either:
  - a disjoint subtree with sum `x`;
  - an ancestor with sum `2x` (cutting both edges leaves the middle part);
  - an ancestor with sum `S − x` (its complement is the part).
- **`v` is the small third part (`x = (S − s_v)/2 ≥ s_v`).** The other two parts come from a disjoint subtree with sum `x`, or an ancestor with sum `x + s_v`.

There is also a special case: `2·s_v = S` (one cut, and the new node is the third tree, `w = s_v`).

Values are positive, so ancestors have larger sums than `v` and descendants smaller ones. Hence "a disjoint subtree with sum `x`" is `count_all[x] − count_ancestors[x]`, minus `v` itself when `x = s_v`. The ancestor sums are kept in a map maintained by an iterative DFS.

**Steps.**
1. Subtree sums by BFS order; count all the non-root sums.
2. DFS with an enter/exit stack, keeping ancestor counts and testing the cases above.

```python
import sys


def balanced_forest(c, edges):
    n = len(c)
    adj = [[] for _ in range(n + 1)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    parent = [0] * (n + 1)
    parent[1] = -1
    order = [1]
    for v in order:
        for u in adj[v]:
            if u != parent[v]:
                parent[u] = v
                order.append(u)
    s = [0] + c[:]
    for v in reversed(order[1:]):
        s[parent[v]] += s[v]
    S = s[1]
    total = {}
    for v in range(2, n + 1):
        total[s[v]] = total.get(s[v], 0) + 1
    anc = {}
    best = None
    stack = [(1, False)]
    while stack:
        v, leaving = stack.pop()
        if leaving:
            if v != 1:
                anc[s[v]] -= 1
            continue
        if v != 1:
            sv = s[v]
            cands = []
            if 2 * sv == S:
                cands.append(sv)
            if 3 * sv >= S and 2 * sv <= S:
                if (total.get(sv, 0) - anc.get(sv, 0) - 1 > 0 or anc.get(2 * sv, 0) > 0
                        or anc.get(S - sv, 0) > 0):
                    cands.append(sv)
            if (S - sv) % 2 == 0:
                x = (S - sv) // 2
                if x >= sv:
                    own = 1 if x == sv else 0
                    if total.get(x, 0) - anc.get(x, 0) - own > 0 or anc.get(x + sv, 0) > 0:
                        cands.append(x)
            for x in cands:
                w = 3 * x - S
                if best is None or w < best:
                    best = w
            anc[sv] = anc.get(sv, 0) + 1
        stack.append((v, True))
        for u in adj[v]:
            if u != parent[v]:
                stack.append((u, False))
    return -1 if best is None else best


def main():
    data = list(map(int, sys.stdin.read().split()))
    q = data[0]
    pos = 1
    out = []
    for _ in range(q):
        n = data[pos]
        c = data[pos + 1:pos + 1 + n]
        pos += 1 + n
        edges = [(data[pos + 2 * i], data[pos + 2 * i + 1]) for i in range(n - 1)]
        pos += 2 * (n - 1)
        out.append(balanced_forest(c, edges))
    print('\n'.join(map(str, out)))


main()
```

**Watch out.** The disjoint test must not count `v` itself when `x = s_v`; that was the bug a brute force over all edge pairs exposed. `3x ≥ S` is what makes the remaining part small enough to top up.

```stdin
2
5
1 2 2 1 1
1 2
1 3
3 5
1 4
3
1 3 5
1 3
1 2
```

```stdout
2
-1
```

### Jenny's Subtrees

**Problem.** For every node `x`, take all nodes within distance `r` (a connected subtree). Count the different subtrees **up to isomorphism**. Here `n, r ≤ 3000`.

**Idea.** Compare unrooted trees by their **centres**: a tree has one or two centre nodes, found from two farthest-point sweeps. Root the ball at each centre and compute an AHU canonical label: each node's label is an id for the sorted tuple of its children's labels, with the ids shared across all balls. The ball's signature is its centre count and the smallest root label. Count the distinct signatures.
- **Shortcut.** Every ball that covers the whole tree is the same tree, so it is processed once.

**Steps.**
1. For each `x`: BFS up to depth `r` to get the ball.
2. Two sweeps for the diameter, centres from the distance sums, AHU from each centre; record the signature.

```python
import sys


def main():
    data = list(map(int, sys.stdin.read().split()))
    n, r = data[0], data[1]
    adj = [[] for _ in range(n + 1)]
    for i in range(n - 1):
        a, b = data[2 + 2 * i], data[3 + 2 * i]
        adj[a].append(b)
        adj[b].append(a)
    canon = {}
    seen = set()
    full_done = False
    inball = [0] * (n + 1)
    stamp = 0

    def sweep(s):
        d = {s: 0}
        q = [s]
        for v in q:
            dv = d[v] + 1
            for u in adj[v]:
                if inball[u] == stamp and u not in d:
                    d[u] = dv
                    q.append(u)
        return q[-1], d

    for x in range(1, n + 1):
        stamp += 1
        depth = {x: 0}
        ball = [x]
        inball[x] = stamp
        for v in ball:
            if depth[v] == r:
                continue
            for u in adj[v]:
                if u not in depth:
                    depth[u] = depth[v] + 1
                    inball[u] = stamp
                    ball.append(u)
        if len(ball) == n:
            if full_done:
                continue
            full_done = True
        a = ball[-1]
        b, da = sweep(a)
        _, db = sweep(b)
        D = da[b]
        centres = [v for v in ball if da[v] + db[v] == D and abs(da[v] - db[v]) <= 1]
        best = None
        for c in centres:
            par = {c: 0}
            seq = [c]
            for v in seq:
                for u in adj[v]:
                    if inball[u] == stamp and u != par[v]:
                        par[u] = v
                        seq.append(u)
            kids = {v: [] for v in seq}
            for v in reversed(seq):
                key = tuple(sorted(kids[v]))
                lab = canon.get(key)
                if lab is None:
                    lab = canon[key] = len(canon)
                if v != c:
                    kids[par[v]].append(lab)
                else:
                    root_label = lab
            if best is None or root_label < best:
                best = root_label
        seen.add((len(centres), best))
    print(len(seen))


main()
```

**Watch out.**
- **Unrooted comparison.** Rooting at `x` itself is wrong: two balls can be isomorphic with their centres `x` and `y` in different places (think of a short path seen from its end and from its middle). Rooting at the tree centre fixes that.
- **Testing.** Checked against `networkx` isomorphism on small random trees. The worst case (a long path with large `r`) is a few seconds.

```stdin
7 1
1 2
1 3
1 4
1 5
2 6
2 7
```

```stdout
3
```

### Tree Coordinates

**Problem.** A point is a pair of tree vertices `(x, y)`. The distance between two points is `dist(x₁, x₂) + dist(y₁, y₂)` in the same tree. Find the largest distance among `m` given points (`n, m ≤ 7.5·10⁴`).

**Idea.** Use **centroid decomposition on the `x` coordinate**. At a centroid `c`, the pairs whose `x`-path passes through `c` have `d₁ = w_i + w_j`, with `w = depth from c`. For those pairs, `w_i + w_j + d₂(y_i, y_j)` is a **tree metric** on `y` (hang a path of length `w_i` from `y_i`). Tree metrics have the diameter property: the farthest point from any point in a set is an endpoint of the set's diameter.
- **Groups.** The points are grouped by the child subtree of `c` they lie in. The centroid's own points form a group whose internal pairs also count.
- **Group diameters.** Find each group's diameter with a vectorised double sweep.
- **Combining groups.** Merge the groups pairwise, level by level (a balanced merge tree). For two sets, the farthest cross pair is among the 4 endpoint pairs, and the merged diameter is among 6 pairs. Each level is one vectorised batch of distance queries.

`d₂` comes from an Euler tour and sparse-table LCA, written for NumPy arrays.

**Steps.**
1. LCA structure on the tree; points listed per vertex.
2. Iterative centroid decomposition; for each centroid gather the groups with their depths.
3. Double sweep per group; balanced merging; keep the best cross pair.

```python
import sys

import numpy as np


def build_dist(n, adj, root=1):
    first = [0] * (n + 1)
    depth = [0] * (n + 1)
    parent = [0] * (n + 1)
    it = [0] * (n + 1)
    parent[root] = -1
    euler = [root]
    stack = [root]
    while stack:
        v = stack[-1]
        if it[v] < len(adj[v]):
            u = adj[v][it[v]]
            it[v] += 1
            if u != parent[v]:
                parent[u] = v
                depth[u] = depth[v] + 1
                first[u] = len(euler)
                euler.append(u)
                stack.append(u)
        else:
            stack.pop()
            if stack:
                euler.append(stack[-1])
    e = np.array(euler, dtype=np.int64)
    dep = np.array(depth, dtype=np.int64)
    ed = dep[e]
    m = len(e)
    K = max(1, m.bit_length())
    sp = np.zeros((K, m), dtype=np.int64)
    sp[0] = np.arange(m)
    for k in range(1, K):
        half = 1 << (k - 1)
        a, b = sp[k - 1][:m - half], sp[k - 1][half:]
        sp[k, :m - half] = np.where(ed[a] <= ed[b], a, b)
    log = np.zeros(m + 1, dtype=np.int64)
    log[2:] = np.floor(np.log2(np.arange(2, m + 1))).astype(np.int64)
    fa = np.array(first, dtype=np.int64)

    def dist(u, v):
        a, b = fa[u], fa[v]
        lo, hi = np.minimum(a, b), np.maximum(a, b)
        k = log[hi - lo + 1]
        x, y = sp[k, lo], sp[k, hi - (1 << k) + 1]
        l = e[np.where(ed[x] <= ed[y], x, y)]
        return dep[u] + dep[v] - 2 * dep[l]
    return dist


def seg_argmax(vals, starts, gid, G):
    mx = np.maximum.reduceat(vals, starts)
    hit = np.flatnonzero(vals == mx[gid])
    _, firsts = np.unique(gid[hit], return_index=True)
    return hit[firsts]


def main():
    data = sys.stdin.buffer.read().split()
    n, m = int(data[0]), int(data[1])
    adj = [[] for _ in range(n + 1)]
    pos = 2
    for _ in range(n - 1):
        a, b = int(data[pos]), int(data[pos + 1])
        pos += 2
        adj[a].append(b)
        adj[b].append(a)
    xs = [int(data[pos + 2 * i]) for i in range(m)]
    ys = np.array([int(data[pos + 2 * i + 1]) for i in range(m)], dtype=np.int64)
    dist2 = build_dist(n, adj)
    at = [[] for _ in range(n + 1)]
    for i, x in enumerate(xs):
        at[x].append(i)
    removed = [False] * (n + 1)
    size = [0] * (n + 1)
    best = 0
    stack = [1]
    while stack:
        root = stack.pop()
        order = [root]
        par = {root: 0}
        for v in order:
            for u in adj[v]:
                if not removed[u] and u != par[v]:
                    par[u] = v
                    order.append(u)
        for v in reversed(order):
            s = 1
            for u in adj[v]:
                if not removed[u] and u != par[v]:
                    s += size[u]
            size[v] = s
        tot = len(order)
        if tot <= 64:                              # small component: all pairs directly
            for v in order:
                removed[v] = True
            nodes = [v for v in order if at[v]]
            pts = [(v, i) for v in nodes for i in at[v]]
            if len(pts) >= 2:
                d1 = {}
                for v in nodes:                    # BFS inside the component
                    dist_v = {v: 0}
                    qq = [v]
                    for z in qq:
                        for u in adj[z]:
                            if u in par and u not in dist_v:
                                dist_v[u] = dist_v[z] + 1
                                qq.append(u)
                    d1[v] = dist_v
                pi, pj, base = [], [], []
                for s in range(len(pts)):
                    for t in range(s + 1, len(pts)):
                        pi.append(pts[s][1])
                        pj.append(pts[t][1])
                        base.append(d1[pts[s][0]][pts[t][0]])
                tot_d = np.array(base) + dist2(ys[np.array(pi)], ys[np.array(pj)])
                best = max(best, int(tot_d.max()))
            continue
        c = root
        while True:
            nxt = None
            for u in adj[c]:
                if not removed[u] and u != par[c] and size[u] * 2 > tot:
                    nxt = u
                    break
            if nxt is None:
                break
            c = nxt
        removed[c] = True
        for u in adj[c]:
            if not removed[u]:
                stack.append(u)
        idx_l, w_l, sizes = [], [], []
        if at[c]:
            idx_l.extend(at[c])
            w_l.extend([0] * len(at[c]))
            sizes.append(len(at[c]))
        for u in adj[c]:
            if removed[u]:
                continue
            cnt = 0
            q = [(u, c, 1)]
            while q:
                v, p, d = q.pop()
                if at[v]:
                    idx_l.extend(at[v])
                    w_l.extend([d] * len(at[v]))
                    cnt += len(at[v])
                for z in adj[v]:
                    if z != p and not removed[z]:
                        q.append((z, v, d + 1))
            if cnt:
                sizes.append(cnt)
        if len(idx_l) < 2:
            continue
        w = np.array(w_l, dtype=np.int64)
        y = ys[np.array(idx_l, dtype=np.int64)]
        G = len(sizes)
        sz = np.array(sizes)
        starts = np.concatenate(([0], np.cumsum(sz)[:-1]))
        gid = np.repeat(np.arange(G), sz)
        a0 = starts[gid]
        b = seg_argmax(w + w[a0] + dist2(y, y[a0]), starts, gid, G)
        bb = b[gid]
        E2 = seg_argmax(w + w[bb] + dist2(y, y[bb]), starts, gid, G)
        E1 = b
        diam = w[E1] + w[E2] + dist2(y[E1], y[E2])
        if at[c]:
            best = max(best, int(diam[0]))
        while len(E1) > 1:
            h = len(E1) // 2
            A1, A2, dA = E1[0:2 * h:2], E2[0:2 * h:2], diam[0:2 * h:2]
            B1, B2, dB = E1[1:2 * h:2], E2[1:2 * h:2], diam[1:2 * h:2]
            pairs = [(X, Y) for X in (A1, A2) for Y in (B1, B2)]
            dists = [w[X] + w[Y] + dist2(y[X], y[Y]) for X, Y in pairs]
            best = max(best, int(np.max(np.stack(dists))))
            vals = np.stack([dA, dB] + dists)
            ones = np.stack([A1, B1] + [X for X, _ in pairs])
            twos = np.stack([A2, B2] + [Y for _, Y in pairs])
            pick = np.argmax(vals, axis=0)
            col = np.arange(h)
            nE1, nE2, nd = ones[pick, col], twos[pick, col], vals[pick, col]
            if len(E1) % 2:
                nE1 = np.append(nE1, E1[-1])
                nE2 = np.append(nE2, E2[-1])
                nd = np.append(nd, diam[-1])
            E1, E2, diam = nE1, nE2, nd
    print(best)


main()
```

**Watch out.**
- **Internal pairs.** Only the centroid's own group may count pairs inside one group. For a child group, `w_i + w_j` overestimates `d₁` (the path does not pass through `c`); those pairs are handled deeper in the decomposition.
- **Testing.** Checked against an all-pairs brute force. Binary scoring means it must be exact, not approximate.

```stdin
2 2
1 2
1 2
2 1
```

```stdout
2
```

### Array Pairs

**Problem.** Count the pairs `i < j` with `a_i · a_j ≤ max(a_i … a_j)`, for `n ≤ 5·10⁵`.

**Idea.** **Divide at the maximum.** Each pair is owned by the position `m` of the range maximum (the rightmost one on ties). Its span `[L, R]` comes from monotonic stacks: the previous strictly larger value and the next larger-or-equal one. A pair `(i, j)` with `L ≤ i ≤ m ≤ j ≤ R` qualifies when the other end is `≤ a_m / a_(this end)`.
- **Smaller side.** Iterate over the smaller side only. Each element becomes a query "how many values `≤ t` lie in this index range". Small-to-large keeps the total at `O(n log n)`.
- **Answering.** All the queries are answered together by a **wavelet matrix** walked with NumPy, one bit level at a time over all queries.

**Steps.**
1. Monotonic stacks for the spans; generate the `(l, r, threshold)` queries from the smaller sides.
2. Compress the values; build the wavelet levels; count `rank < T` in every range at once; sum.

```python
import sys

import numpy as np


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    a = [int(x) for x in data[1:1 + n]]
    A = np.array(a, dtype=np.int64)
    uniq, rank = np.unique(A, return_inverse=True)
    rank = rank.astype(np.int64)
    bits = max(1, int(len(uniq)).bit_length())
    levels = []
    cur = rank.copy()
    for lev in range(bits - 1, -1, -1):
        b = (cur >> lev) & 1
        z = np.zeros(n + 1, dtype=np.int64)
        z[1:] = np.cumsum(b == 0)
        levels.append((lev, z, int(z[-1])))
        cur = cur[np.argsort(b, kind='stable')]
    left = [0] * n
    right = [n - 1] * n
    st = []
    for i in range(n):
        while st and a[st[-1]] <= a[i]:
            right[st.pop()] = i - 1
        left[i] = st[-1] + 1 if st else 0
        st.append(i)
    ql, qr, qt = [], [], []
    for m in range(n):
        L, R, am = left[m], right[m], a[m]
        if m - L <= R - m:
            for i in range(L, m + 1):              # partner j in [m, R] (j > m if i == m)
                ql.append(m + 1 if i == m else m)
                qr.append(R + 1)
                qt.append(am // a[i])
        else:
            for j in range(m, R + 1):              # partner i in [L, m] (i < m if j == m)
                ql.append(L)
                qr.append(m if j == m else m + 1)
                qt.append(am // a[j])
    if not ql:
        print(0)
        return
    l = np.array(ql, dtype=np.int64)
    r = np.array(qr, dtype=np.int64)
    T = np.searchsorted(uniq, np.array(qt, dtype=np.int64), side='right')
    res = np.zeros(len(l), dtype=np.int64)
    for lev, z, nz in levels:                      # count rank < T in [l, r)
        bit = (T >> lev) & 1
        zl, zr = z[l], z[r]
        res += np.where(bit == 1, zr - zl, 0)
        l = np.where(bit == 1, nz + l - zl, zl)
        r = np.where(bit == 1, nz + r - zr, zr)
    print(int(res.sum()))


main()
```

**Watch out.** Ties need one strict and one non-strict boundary, so that every pair is owned by exactly one maximum. Pairs that use the maximum itself are covered by letting `m` belong to both sides of its own span.

```stdin
5
1 1 2 4 2
```

```stdout
8
```
