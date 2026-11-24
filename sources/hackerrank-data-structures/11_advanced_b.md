## Advanced

### Counting On a Tree

**Problem.** In a tree with node values `c_i`, each query `w x y z` asks for the number of ordered pairs `(i, j)` with `i ≠ j`, `i` on the path `w–x`, `j` on the path `y–z` and `c_i = c_j`.

**Idea.** If colour `c` appears `a_c` times on the first path and `b_c` times on the second, then the pairs with `i = j` allowed number `Σ a_c·b_c`. The pairs with `i = j` are exactly the nodes shared by both paths, so subtract that overlap. A **heavy-light decomposition** turns each path into `O(log n)` contiguous slices of one array. The colours of a path are then a few numpy slices. `bincount` of the shorter path's colours gives every `a_c`, and indexing it with the longer path's colours gives `Σ a_c·b_c` in one pass. The overlap is the total length of the pairwise intersections of the two slice lists.

**Steps.**
1. Compress the colours to `0..K−1`. Build the HLD (`head`, `pos`) and store `col_at[pos[u]] = col[u]`.
2. For each query, collect both paths' slices and concatenate their colours.
3. Answer `= bincount(c1)[c2].sum() − overlap`.

```python
import sys

import numpy as np


def main():
    data = sys.stdin.buffer.read().split()
    n, q = int(data[0]), int(data[1])
    raw = np.array(data[2:2 + n], dtype=np.int64)
    _, col = np.unique(raw, return_inverse=True)          # colours -> 0..K-1
    K = int(col.max()) + 1
    adj = [[] for _ in range(n)]
    p = 2 + n
    for _ in range(n - 1):
        a = int(data[p]) - 1; b = int(data[p + 1]) - 1; p += 2
        adj[a].append(b)
        adj[b].append(a)
    parent = [-1] * n
    depth = [0] * n
    order = [0]
    for u in order:
        for v in adj[u]:
            if v != parent[u]:
                parent[v] = u
                depth[v] = depth[u] + 1
                order.append(v)
    size = [1] * n
    heavy = [-1] * n
    for u in reversed(order):
        if parent[u] >= 0:
            size[parent[u]] += size[u]
    for u in order:
        best = 0
        for v in adj[u]:
            if v != parent[u] and size[v] > best:
                best = size[v]
                heavy[u] = v
    head = [0] * n
    pos = [0] * n
    cur = 0
    st = [0]
    while st:                                   # lay every heavy chain out contiguously
        h = st.pop()
        u = h
        while u != -1:
            head[u] = h
            pos[u] = cur
            cur += 1
            for v in adj[u]:
                if v != parent[u] and v != heavy[u]:
                    st.append(v)
            u = heavy[u]
    col_at = np.empty(n, dtype=np.int64)
    col_at[pos] = col

    def segments(u, v):                         # path u-v as half-open slices of pos
        segs = []
        while head[u] != head[v]:
            if depth[head[u]] < depth[head[v]]:
                u, v = v, u
            segs.append((pos[head[u]], pos[u] + 1))
            u = parent[head[u]]
        a, b = pos[u], pos[v]
        if a > b:
            a, b = b, a
        segs.append((a, b + 1))
        return segs

    out = []
    for _ in range(q):
        w = int(data[p]) - 1; x = int(data[p + 1]) - 1
        y = int(data[p + 2]) - 1; z = int(data[p + 3]) - 1
        p += 4
        s1 = segments(w, x)
        s2 = segments(y, z)
        c1 = np.concatenate([col_at[a:b] for a, b in s1])
        c2 = np.concatenate([col_at[a:b] for a, b in s2])
        if len(c1) > len(c2):
            c1, c2 = c2, c1
        total = int(np.bincount(c1, minlength=K)[c2].sum())
        overlap = 0                             # nodes on both paths (the i == j pairs)
        for a, b in s1:
            for c, d in s2:
                lo = a if a > c else c
                hi = b if b < d else d
                if hi > lo:
                    overlap += hi - lo
        out.append(total - overlap)
    sys.stdout.write('\n'.join(map(str, out)) + '\n')


main()
```

**Watch out.** Each query is linear in the path lengths, but all of that work happens inside numpy. Path queries on a long path graph with 10⁵ distinct colours take about 4.6 s for 5·10⁴ queries. The fully sub-linear solutions (Mo's algorithm on trees, heavy/light colour splits) do far more Python-level work and are slower here. The slices inside one path never overlap, so summing pairwise intersections counts each shared node exactly once.

```stdin
10 5
10 2 3 5 10 5 3 6 2 1
1 2
1 3
3 4
3 5
3 6
4 7
5 8
7 9
2 10
8 5 2 10
3 8 4 9
1 9 5 9
4 6 4 6
5 8 5 8
```

```stdout
0
1
3
2
0
```

### Costly Intervals

**Problem.** `cost(l, r) = (OR − AND) − (MAX − MIN)` over `A[l..r]`. For every index `i`, print the largest length of a subarray containing `i` with `cost ≥ k`, or `-1`.

**Idea.** Only the **smallest valid `l` for each `r`** matters: any valid interval `[l, r]` is contained in `[l_r, r]`, which is also valid and covers the same `i`. For a fixed `r`, `OR − AND` changes only at the last position `≤ r` where some bit is set (for OR) or clear (for AND). That gives at most 62 breakpoints, which split the `l`s into groups with a constant `D = OR − AND`. Inside a group `MAX − MIN` only grows as `l` moves left. So:
- the group's right end `c` is its best member;
- the smallest valid `l` lies in the **leftmost group whose right end is valid**;
- inside that group it is found by binary search on `MAX − MIN ≤ D − k`.

Everything is vectorised over all `r` and all breakpoints with sparse tables. Then the intervals are painted longest first with a "next unpainted" DSU.

**Steps.**
1. Build sparse tables for OR, AND, MAX and MIN. For each bit, take `maximum.accumulate` of the positions where it is set or clear; these are the candidate group ends.
2. Check each candidate's right end, pick the smallest valid one per `r`, and binary search inside its group.
3. Sort the intervals by length (descending) and assign each unpainted position its first covering interval's length.

```python
import sys

import numpy as np


def main():
    data = sys.stdin.buffer.read().split()
    n, K = int(data[0]), int(data[1])
    A = np.array(data[2:2 + n], dtype=np.int64)
    idx = np.arange(n, dtype=np.int64)
    LOG2 = np.zeros(n + 2, dtype=np.int64)
    for i in range(2, n + 2):
        LOG2[i] = LOG2[i >> 1] + 1

    def build(fn):
        t = [A]
        while (1 << len(t)) <= n:
            prev = t[-1]
            h = 1 << (len(t) - 1)
            t.append(fn(prev[:-h], prev[h:]))
        return t

    def query(t, fn, l, r):                      # vectorised, inclusive ranges
        k = LOG2[r - l + 1]
        out = np.empty(k.shape, dtype=np.int64)
        for kk in np.unique(k).tolist():
            m = k == kk
            out[m] = fn(t[kk][l[m]], t[kk][r[m] - (1 << kk) + 1])
        return out

    T_or, T_and = build(np.bitwise_or), build(np.bitwise_and)
    T_max, T_min = build(np.maximum), build(np.minimum)

    def cost_parts(l, r):
        d = query(T_or, np.bitwise_or, l, r) - query(T_and, np.bitwise_and, l, r)
        s = query(T_max, np.maximum, l, r) - query(T_min, np.minimum, l, r)
        return d, s

    # group ends for every r: last set / last clear position of every bit, and r itself
    cols = [idx]
    for b in range(31):
        bit = (A >> b) & 1
        cols.append(np.maximum.accumulate(np.where(bit == 1, idx, -1)))
        cols.append(np.maximum.accumulate(np.where(bit == 0, idx, -1)))
    C = np.stack(cols, axis=1)
    R = np.repeat(idx, C.shape[1]).reshape(C.shape)
    valid = C >= 0
    d, s = cost_parts(C[valid], R[valid])
    good = np.zeros(C.shape, dtype=bool)
    good[valid] = d - s >= K
    BIG = n + 5
    cbest = np.where(good, C, BIG).min(axis=1)
    has = cbest < BIG
    rs = idx[has]
    cb = cbest[has]
    row = C[has]
    lo = np.where(row < cb[:, None], row, -1).max(axis=1) + 1   # group is [lo, cb]
    D, _ = cost_parts(cb, rs)
    lim = D - K
    hi = cb.copy()
    while True:                                  # smallest l in [lo, cb] with MAX-MIN <= lim
        act = lo < hi
        if not act.any():
            break
        mid = (lo + hi) // 2
        ok = np.zeros(len(lo), dtype=bool)
        a = np.flatnonzero(act)
        _, spread = cost_parts(mid[a], rs[a])
        ok[a] = spread <= lim[a]
        hi = np.where(act & ok, mid, hi)
        lo = np.where(act & ~ok, mid + 1, lo)

    ls, rl = lo.tolist(), rs.tolist()
    ans = [-1] * n
    nxt = list(range(n + 1))                     # next unpainted position

    def find(x):
        root = x
        while nxt[root] != root:
            root = nxt[root]
        while nxt[x] != root:
            nxt[x], x = root, nxt[x]
        return root

    for t in sorted(range(len(ls)), key=lambda t: ls[t] - rl[t]):
        l, r = ls[t], rl[t]
        x = find(l)
        while x <= r:
            ans[x] = r - l + 1
            nxt[x] = x + 1
            x = find(x + 1)
    sys.stdout.write('\n'.join(map(str, ans)) + '\n')


main()
```

**Watch out.**
- `OR ≥ MAX` and `AND ≤ MIN`, so every cost is `≥ 0` and `k = 0` makes the answer `n` everywhere.
- A breakpoint list can contain duplicates, so the group's left bound is the **largest candidate strictly smaller** than the chosen end.
- `A_i < 2^30`, but 31 bits are scanned to be safe.

```stdin
5 6
2 4 3 1 7
```

```stdout
-1
2
2
-1
-1
```

### The Strange Function

**Problem.** Maximise `f(l, r) = gcd(a_l..a_r) · (sum(a_l..a_r) − max(a_l..a_r))` over all subarrays (`gcd` uses absolute values). `n ≤ 5·10⁴` and `|a_i| ≤ 10⁶`.

**Idea.** Use **divide and conquer on the middle**. A crossing subarray is a left part `a[l..mid−1]` plus a right part `a[mid..r]`. Each side has prefix arrays computed with `np.gcd.accumulate`, `cumsum` and `maximum.accumulate`. The right side's gcd takes at most ~20 distinct values, so group `r` by it. Inside one group `G = gcd(gl, gr)` is fixed per `l`, and the max is either the left max or the right max:
- **right max ≤ left max:** the allowed `r` form a prefix of the group, because the right max only grows. Use `searchsorted` on the right maxima and a prefix maximum of the right sums.
- **right max > left max:** the allowed `r` form a suffix. Use a suffix maximum of `sum − max`.

Small ranges (≤ 48) are brute-forced in pure Python.

**Steps.**
1. Use an explicit stack of ranges; brute-force the small ones.
2. For a big range, compute the left/right accumulations and split the right side at its gcd changes.
3. For each group, handle both cases vectorised over all `l` and keep the best value (starting from 0, since `f(i, i) = 0`).

```python
import sys
from math import gcd

import numpy as np


def maximum_value(a):
    n = len(a)
    A = np.array(a, dtype=np.int64)
    best = 0                                     # f(i, i) = 0

    def brute(lo, hi):
        res = 0
        for l in range(lo, hi):
            g = s = 0
            m = -10 ** 7
            for r in range(l, hi):
                x = a[r]
                g = gcd(g, x)
                s += x
                if x > m:
                    m = x
                v = g * (s - m)
                if v > res:
                    res = v
        return res

    stack = [(0, n)]
    while stack:
        lo, hi = stack.pop()
        if hi - lo <= 48:
            best = max(best, brute(lo, hi))
            continue
        mid = (lo + hi) // 2
        stack.append((lo, mid))
        stack.append((mid, hi))
        L = A[lo:mid][::-1]                      # a[mid-1], a[mid-2], ..., a[lo]
        gl = np.gcd.accumulate(np.abs(L))
        sl = np.cumsum(L)
        ml = np.maximum.accumulate(L)
        R = A[mid:hi]
        gr = np.gcd.accumulate(np.abs(R))
        sr = np.cumsum(R)
        mr = np.maximum.accumulate(R)
        cuts = np.flatnonzero(np.diff(gr)) + 1
        starts = np.concatenate(([0], cuts)).tolist()
        ends = np.concatenate((cuts, [len(R)])).tolist()
        for s0, e0 in zip(starts, ends):
            G = np.gcd(gl, gr[s0])
            msub = mr[s0:e0]
            k = np.searchsorted(msub, ml, side='right')     # r's with right max <= left max
            pre = np.maximum.accumulate(sr[s0:e0])
            ok = k > 0
            if ok.any():
                best = max(best, int((G[ok] * (sl[ok] - ml[ok] + pre[k[ok] - 1])).max()))
            suf = np.maximum.accumulate((sr[s0:e0] - msub)[::-1])[::-1]
            ok = k < e0 - s0
            if ok.any():
                best = max(best, int((G[ok] * (sl[ok] + suf[k[ok]])).max()))
    return best


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    print(maximum_value(list(map(int, data[1:1 + n]))))


main()
```

**Watch out.**
- `gcd(0, x) = |x|`, and an all-zero subarray has gcd 0, so its value is 0.
- The products reach about `10⁶ · 5·10¹⁰`, which still fits in int64.
- With ties in the max, case 1 uses `side='right'` so equal maxima count as "right max ≤ left max"; both cases then give the same value anyway.

```stdin
4
10 -5 5 20
```

```stdout
50
```

### Self-Driving Bus

**Problem.** In a tree on nodes `1..n`, count the segments `[L, R]` whose node set `{L, …, R}` is connected.

**Idea.** An induced subgraph of a tree is a forest, so `[L, R]` is connected iff it contains exactly `R − L` edges. Let `h_R(L) = L + #edges inside [L, R]`. Then `h_R(L) ≤ R` always, with equality exactly for connected segments. Sweep `R` upward. Each edge `(u, R)` with `u < R` adds 1 to `h(L)` for every `L ≤ u`. For each `R`, count the `L ≤ R` with `h(L) = R`, which is the **count of the maximum**. A sqrt-decomposition in numpy keeps a lazy add plus `(max, count)` per block. Positions `L > R` keep `h = L`, and queries never include them.

**Steps.**
1. Put each edge at its larger endpoint.
2. For `R = 0..n−1`: apply the prefix +1 updates, then count `h == R` over full blocks (block max + lazy) and over the partial block directly.

```python
import sys

import numpy as np


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    smaller = [[] for _ in range(n)]              # smaller[v] = neighbours u < v
    for i in range(n - 1):
        a = int(data[1 + 2 * i]) - 1
        b = int(data[2 + 2 * i]) - 1
        if a > b:
            a, b = b, a
        smaller[b].append(a)
    B = max(64, int(n ** 0.5))
    nb = (n + B - 1) // B
    h = np.arange(nb * B, dtype=np.int64)         # h[L] = L + edges inside [L, R]
    hb = h.reshape(nb, B)
    bmax = hb.max(axis=1)
    bcnt = np.ones(nb, dtype=np.int64)
    lazy = np.zeros(nb, dtype=np.int64)
    total = 0
    for R in range(n):
        for u in smaller[R]:                      # +1 on h[0..u]
            k = u // B
            lazy[:k] += 1
            seg = hb[k]
            seg[:u - k * B + 1] += 1
            m = seg.max()
            bmax[k] = m
            bcnt[k] = np.count_nonzero(seg == m)
        k = R // B
        if k:
            total += int(bcnt[:k][bmax[:k] + lazy[:k] == R].sum())
        total += int(np.count_nonzero(hb[k][:R - k * B + 1] == R - lazy[k]))
    print(total)


main()
```

**Watch out.**
- The partial block in a query may contain inactive positions (`L > R`), so it is sliced to `[k·B, R]`.
- Full blocks lie entirely below `R`, so their max is the max over active `L` only.
- About 1.9 s for `n = 2·10⁵`.

```stdin
3
1 3
3 2
```

```stdout
5
```

### Unique Colors

**Problem.** For every node `i` of a coloured tree, print `Σ_j d(i, j)`, where `d(i, j)` is the number of distinct colours on the path `i–j` (with `j = i` included).

**Idea.** Count by colour instead. Colour `c` is on path `i–j` unless `j` lies in `i`'s part of the tree **after deleting all `c`-nodes**. So `sum_i = n·C − Σ_c part_c(i)`, where `part_c(i) = 0` when `i` itself has colour `c`. Deleting colour `c` leaves:
- the **root part**, which is everything outside the top-most `c`-nodes' subtrees;
- for every `c`-node `a` and child `b`, the part below `b`, which is `subtree(b)` minus the subtrees of the nearest `c`-nodes inside it.

One DFS that keeps the nearest node of every colour on the current path finds, for each node `w`, which part loses `subtree(w)`. Every part is then added over its Euler range, with the removed subtrees subtracted, using one difference array.

**Steps.**
1. Preorder `tin` and `size` from root 0.
2. DFS with enter/exit events:
   - on entering `u`, mark `u` as its parent's active branch;
   - let `a` be the nearest node of colour `c_u` on the path: `u` is removed from `a`'s active branch `b`, or from the root part if there is no such `a`.
3. Add each part on the difference array: `+part` on its range and `−part` on the ranges of its removed subtrees. Then `sum_i = n·C − prefix(tin_i)`.

```python
import sys


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    col = [int(x) for x in data[1:1 + n]]
    adj = [[] for _ in range(n)]
    p = 1 + n
    for _ in range(n - 1):
        a = int(data[p]) - 1
        b = int(data[p + 1]) - 1
        p += 2
        adj[a].append(b)
        adj[b].append(a)
    parent = [-1] * n
    order = []
    stack = [0]
    seen = [False] * n
    seen[0] = True
    while stack:
        u = stack.pop()
        order.append(u)
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                parent[v] = u
                stack.append(v)
    tin = [0] * n
    for i, u in enumerate(order):
        tin[u] = i
    size = [1] * n
    for u in reversed(order):
        if parent[u] >= 0:
            size[parent[u]] += size[u]
    kids = [[] for _ in range(n)]
    for u in order[1:]:
        kids[parent[u]].append(u)

    nearest = {}                   # colour -> nearest node of that colour on the DFS path
    branch = [0] * n               # branch[a] = child of a currently being explored
    owner = [-1] * n               # owner[w] = branch that loses subtree(w), -1 = root part
    part = size[:]                 # part[b] = size of the part hanging below branch b
    root_part = {}                 # colour -> size of the root part
    saved = [0] * n
    st = [(0, True)]
    while st:
        u, enter = st.pop()
        c = col[u]
        if not enter:
            nearest[c] = saved[u]
            continue
        if parent[u] >= 0:
            branch[parent[u]] = u
        a = nearest.get(c, -1)
        saved[u] = a
        if a == -1:
            root_part[c] = root_part.get(c, n) - size[u]
        else:
            b = branch[a]
            owner[u] = b
            part[b] -= size[u]
        nearest[c] = u
        st.append((u, False))
        for v in reversed(kids[u]):
            st.append((v, True))

    diff = [0] * (n + 1)
    for s in root_part.values():
        diff[0] += s
        diff[n] -= s
    for b in order[1:]:
        s = part[b]
        diff[tin[b]] += s
        diff[tin[b] + size[b]] -= s
    for w in range(n):
        s = root_part[col[w]] if owner[w] == -1 else part[owner[w]]
        diff[tin[w]] -= s
        diff[tin[w] + size[w]] += s
    C = len(root_part)
    acc = [0] * n
    run = 0
    for i in range(n):
        run += diff[i]
        acc[i] = run
    sys.stdout.write('\n'.join(str(n * C - acc[tin[u]]) for u in range(n)) + '\n')


main()
```

**Watch out.**
- A node never lies in a part of its own colour: its subtree is subtracted from the part above it, and the parts below it start at its children. That gives `part_c(i) = 0` for free.
- A child of the same colour as its parent forms an empty part, which is harmless.
- Everything is `O(n)`.

```stdin
5
1 2 3 2 3
1 2
2 3
2 4
1 5
```

```stdout
10
9
11
9
12
```

### Fibonacci Numbers Tree

**Problem.** In a rooted tree, `U X k` adds `F_{k+D}` to every node at distance `D` below `X`. `Q X Y` prints the path sum mod `10⁹+7`. `k ≤ 10¹⁵`.

**Idea.** Write `t = k − depth(X)`. The identity `F_{t+d} = F_t·F_{d+1} + F_{t−1}·F_d` holds for all integers, so the update adds `A·F_{d+1} + B·F_d` at depth `d`, with `A = F_t` and `B = F_{t−1}`. Let `S(v)` be the sum of values on the path root → `v`. An update at an ancestor `X` of `v` adds to `S(v)` the depths from `depth(X)` to `depth(v)`. Using `G0(d) = Σ_{e≤d} F_e = F_{d+2} − 1` and `G1(d) = F_{d+3} − 1`:

`S(v) = G1(d_v)·ΣA + G0(d_v)·ΣB − ΣC`, with `C = A·G1(d_X − 1) + B·G0(d_X − 1)`,

where the sums run over the updates at ancestors of `v`. Each update is a range add on `X`'s Euler interval, and `S(v)` reads a point. One Fenwick tree stores `A`, `B` and `C` **packed into one Python int**, in 64-bit fields. A path sum is `S(x) + S(y) − S(lca) − S(parent(lca))`.

**Steps.**
1. Preorder `tin` and `size`, depth, and binary lifting for the LCA.
2. `U`: compute `F_t` and `F_{t−1}` by fast doubling (negative `t` uses `F_{−m} = (−1)^{m+1} F_m`), then add the packed value on `[tin, tin + size)`.
3. `Q`: combine four `S` values.

```python
import sys

MOD = 10 ** 9 + 7
SH = 64
MASK = (1 << SH) - 1


def fib_pair(t):                                # (F_t, F_{t+1}) by fast doubling, t >= 0
    a, b = 0, 1
    for bit in bin(t)[2:]:
        c = a * ((2 * b - a) % MOD) % MOD
        d = (a * a + b * b) % MOD
        a, b = (d, (c + d) % MOD) if bit == '1' else (c, d)
    return a, b


def fib_any(t):
    if t >= 0:
        return fib_pair(t)[0]
    f = fib_pair(-t)[0]
    return f if (-t) % 2 == 1 else (-f) % MOD


def main():
    data = sys.stdin.buffer.read().split()
    n, m = int(data[0]), int(data[1])
    parent = [-1] * n
    kids = [[] for _ in range(n)]
    for i in range(1, n):
        p = int(data[1 + i]) - 1
        parent[i] = p
        kids[p].append(i)
    pos = n + 1
    depth = [0] * n
    order = []
    st = [0]
    while st:
        u = st.pop()
        order.append(u)
        for v in kids[u]:
            depth[v] = depth[u] + 1
            st.append(v)
    tin = [0] * n
    for i, u in enumerate(order):
        tin[u] = i + 1                          # 1-based for the Fenwick tree
    size = [1] * n
    for u in reversed(order):
        if parent[u] >= 0:
            size[parent[u]] += size[u]
    LOG = max(1, (n - 1).bit_length())
    up = [[p if p >= 0 else 0 for p in parent]]
    for _ in range(LOG - 1):
        prev = up[-1]
        up.append([prev[prev[v]] for v in range(n)])

    def lca(a, b):
        if depth[a] < depth[b]:
            a, b = b, a
        diff = depth[a] - depth[b]
        k = 0
        while diff:
            if diff & 1:
                a = up[k][a]
            diff >>= 1
            k += 1
        if a == b:
            return a
        for k in range(LOG - 1, -1, -1):
            if up[k][a] != up[k][b]:
                a = up[k][a]
                b = up[k][b]
        return up[0][a]

    F = [0, 1]
    for _ in range(n + 5):
        F.append((F[-1] + F[-2]) % MOD)
    G0 = [(F[d + 2] - 1) % MOD for d in range(n + 1)]
    G1 = [(F[d + 3] - 1) % MOD for d in range(n + 1)]
    tree = [0] * (n + 2)

    def add(i, val):
        while i <= n:
            tree[i] += val
            i += i & -i

    def S(v):                                   # sum of values on root -> v
        if v < 0:
            return 0
        i = tin[v]
        tot = 0
        while i:
            tot += tree[i]
            i -= i & -i
        d = depth[v]
        return G1[d] * (tot & MASK) + G0[d] * ((tot >> SH) & MASK) - (tot >> (2 * SH))

    out = []
    for _ in range(m):
        op = data[pos]
        x = int(data[pos + 1]) - 1
        y = int(data[pos + 2])
        pos += 3
        if op == b'U':
            t = y - depth[x]
            A = fib_any(t)
            B = fib_any(t - 1)
            dx = depth[x]
            C = (A * (G1[dx - 1] if dx else 0) + B * (G0[dx - 1] if dx else 0)) % MOD
            packed = A | (B << SH) | (C << (2 * SH))
            add(tin[x], packed)
            add(tin[x] + size[x], -packed)
        else:
            y -= 1
            l = lca(x, y)
            out.append((S(x) + S(y) - S(l) - S(parent[l])) % MOD)
    sys.stdout.write('\n'.join(map(str, out)) + ('\n' if out else ''))


main()
```

**Watch out.**
- `t = k − depth(X)` can be negative, so the negative-index Fibonacci rule is needed.
- Packing works even though Fenwick nodes hold negative numbers: integer arithmetic is linear, and every final point value has each field in `[0, 2⁶⁴)`, so the fields decode exactly.
- About 2.3 s for `N = M = 10⁵`.

```stdin
5 10
1
1
2
2
Q 1 5
U 1 1
Q 1 1
Q 1 2
Q 1 3
Q 1 4
Q 1 5
U 2 2
Q 2 3
Q 4 5
```

```stdout
0
1
2
2
4
4
4
10
```

### Pair Sums

**Problem.** The value of an array is the sum of `a_i·a_j` over its pairs `i < j`. Find the largest value among all subarrays. `n ≤ 5·10⁵` and `|a_i| ≤ 1000`.

**Idea.** A subarray's value is `(S² − Q)/2`, with `S` the sum and `Q` the sum of squares. With prefix sums `X` and `Y` (of `a` and `a²`), twice the value of the subarray between prefix points `i < j` is

`(X_j − X_i)² − (Y_j − Y_i) = W_i + Z_j − 2·X_i·X_j`, where `W_i = X_i² + Y_i` and `Z_j = X_j² − Y_j`.

For fixed `j` this is a maximum over the lines of the earlier points `i`. Run a **bottom-up divide and conquer over the index**. Every block keeps two upper convex hulls of points `(X, W)` and `(X, Z)`, merged from its halves. Cross pairs (left `i`, right `j`) only need hull vertices, and a two-pointer walk finds them: as `X_j` grows, the best `X_i` moves left. Leaf blocks of 16 points are brute-forced as one numpy tensor.

**Steps.**
1. Compute the prefix arrays. Brute-force all pairs inside 16-point leaves with numpy.
2. Build each leaf's hulls, then repeatedly pair up neighbouring blocks: evaluate the cross pairs on the hulls, and merge the hulls.
3. Print `best // 2`.

```python
import sys

import numpy as np


def upper_hull(pts):                            # pts sorted by x
    h = []
    for x, v in pts:
        if h and h[-1][0] == x:
            if h[-1][1] >= v:
                continue
            h.pop()
        while len(h) >= 2:
            x1, v1 = h[-2]
            x2, v2 = h[-1]
            if (x2 - x1) * (v - v1) - (v2 - v1) * (x - x1) >= 0:
                h.pop()
            else:
                break
        h.append((x, v))
    return h


def merge(a, b):
    out = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    out.extend(a[i:])
    out.extend(b[j:])
    return out


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    A = np.array(data[1:1 + n], dtype=np.int64)
    X = np.zeros(n + 1, dtype=np.int64)
    Y = np.zeros(n + 1, dtype=np.int64)
    X[1:] = np.cumsum(A)
    Y[1:] = np.cumsum(A * A)
    m = n + 1
    LEAF = 16
    nb = (m + LEAF - 1) // LEAF
    pad = nb * LEAF - m
    Xp = np.concatenate((X, np.zeros(pad, dtype=np.int64))).reshape(nb, LEAF)
    Yp = np.concatenate((Y, np.zeros(pad, dtype=np.int64))).reshape(nb, LEAF)
    dx = Xp[:, None, :] - Xp[:, :, None]
    val = dx * dx - (Yp[:, None, :] - Yp[:, :, None])
    idx = np.arange(nb * LEAF).reshape(nb, LEAF)
    ok = (np.arange(LEAF)[:, None] < np.arange(LEAF)[None, :])[None] & (idx < m)[:, None, :]
    best = int(np.where(ok, val, 0).max())
    W = (X * X + Y).tolist()
    Z = (X * X - Y).tolist()
    xs = X.tolist()

    def leaf_hulls(lo, hi):
        order = sorted(range(lo, hi), key=xs.__getitem__)
        return (upper_hull([(xs[i], W[i]) for i in order]),
                upper_hull([(xs[i], Z[i]) for i in order]))

    level = [leaf_hulls(b * LEAF, min(m, (b + 1) * LEAF)) for b in range(nb)]
    while len(level) > 1:
        nxt = []
        for k in range(0, len(level) - 1, 2):
            wl, zl = level[k]
            wr, zr = level[k + 1]
            p = len(wl) - 1
            for xj, zj in zr:                   # x_j increasing -> best x_i moves left
                s = -2 * xj
                while p > 0 and wl[p - 1][1] + s * wl[p - 1][0] >= wl[p][1] + s * wl[p][0]:
                    p -= 1
                v = wl[p][1] + s * wl[p][0] + zj
                if v > best:
                    best = v
            nxt.append((upper_hull(merge(wl, wr)), upper_hull(merge(zl, zr))))
        if len(level) % 2:
            nxt.append(level[-1])
        level = nxt
    print(best // 2)


main()
```

**Watch out.**
- A single element has no pairs, so the answer is at least 0.
- A cross pair's maximum over all `(i, j)` is reached on hull vertices of **both** sides: for fixed `i` the best `j` is a `Z`-hull vertex, and vice versa.
- An odd block at the end of a level is carried up unchanged, which keeps left/right order intact.
- About 1.3 s for `n = 5·10⁵`.

```stdin
6
-3 7 -2 3 5 -2
```

```stdout
41
```

### Functional Palindromes

**Problem.** List all palindromic substrings of `s` (each occurrence counted) in lexicographic order. For each `k`, print the polynomial hash `f` of the `k`-th one, or `-1`.

**Idea.**
- A **palindromic tree (eertree)** lists the ≤ `n` distinct palindromes with their occurrence counts.
- To sort them, view each palindrome as `s[i : i+len]`. All copies of a substring share one key: the **first suffix-array rank** whose suffix starts with it. Find it by binary search on the LCP sparse table.
- Ordering by `(first rank, length)` is exactly lexicographic order, because a prefix of a string gets the same or a smaller first rank and is shorter.
- Prefix sums of the counts in that order answer each `k` with `bisect`. The hash comes from prefix hashes.

**Steps.**
1. Build the eertree, keeping one end position and the count of each node; push the counts down the suffix links.
2. Suffix array by numpy prefix doubling, LCP by Kasai, and a sparse table over the LCP.
3. Vectorised binary search for each palindrome's first rank, then `lexsort` by `(rank, length)`.
4. Cumulative counts; `bisect_left` for each `k`.

```python
import sys
from bisect import bisect_left

import numpy as np

MOD = 10 ** 9 + 7
BASE = 100001


def suffix_array(s):
    n = len(s)
    rank = np.frombuffer(s.encode(), dtype=np.uint8).astype(np.int64)
    k = 1
    while True:
        second = np.full(n, -1, dtype=np.int64)
        if k < n:
            second[:n - k] = rank[k:]
        sa = np.lexsort((second, rank))
        r1, r2 = rank[sa], second[sa]
        change = np.zeros(n, dtype=np.int64)
        change[1:] = (r1[1:] != r1[:-1]) | (r2[1:] != r2[:-1])
        rank = np.empty(n, dtype=np.int64)
        rank[sa] = np.cumsum(change)
        if rank.max() == n - 1:
            return sa, rank
        k <<= 1


def main():
    data = sys.stdin.buffer.read().split()
    n, q = int(data[0]), int(data[1])
    s = data[2].decode()
    ks = [int(x) for x in data[3:3 + q]]

    # palindromic tree: node 0 = root of length -1, node 1 = empty palindrome
    length, link, nxt, cnt, endpos = [-1, 0], [0, 0], [{}, {}], [0, 0], [0, 0]
    last = 1
    for i, ch in enumerate(s):
        cur = last
        while not (i - length[cur] - 1 >= 0 and s[i - length[cur] - 1] == ch):
            cur = link[cur]
        if ch in nxt[cur]:
            last = nxt[cur][ch]
            cnt[last] += 1
            continue
        node = len(length)
        length.append(length[cur] + 2)
        endpos.append(i)
        nxt.append({})
        cnt.append(1)
        if length[node] == 1:
            link.append(1)
        else:
            w = link[cur]
            while not (i - length[w] - 1 >= 0 and s[i - length[w] - 1] == ch):
                w = link[w]
            link.append(nxt[w][ch])
        nxt[cur][ch] = node
        last = node
    for v in range(len(length) - 1, 1, -1):
        cnt[link[v]] += cnt[v]
    nodes = list(range(2, len(length)))
    lens = np.array([length[v] for v in nodes], dtype=np.int64)
    starts = np.array([endpos[v] - length[v] + 1 for v in nodes], dtype=np.int64)

    sa, rank = suffix_array(s)
    sa_l, rk = sa.tolist(), rank.tolist()
    lcp = [0] * n                               # lcp[r] = LCP(suffix sa[r-1], suffix sa[r])
    h = 0
    for i in range(n):
        r = rk[i]
        if r == 0:
            h = 0
            continue
        j = sa_l[r - 1]
        while i + h < n and j + h < n and s[i + h] == s[j + h]:
            h += 1
        lcp[r] = h
        if h:
            h -= 1
    table = [np.array(lcp, dtype=np.int64)]
    while (1 << len(table)) <= n:
        prev = table[-1]
        half = 1 << (len(table) - 1)
        table.append(np.minimum(prev[:-half], prev[half:]))
    LOG2 = [0] * (n + 2)
    for i in range(2, n + 2):
        LOG2[i] = LOG2[i >> 1] + 1
    LOG2 = np.array(LOG2, dtype=np.int64)

    def range_min(lo, hi):                      # min lcp[lo..hi], vectorised
        k = LOG2[hi - lo + 1]
        out = np.empty(len(lo), dtype=np.int64)
        for kk in np.unique(k).tolist():
            m = k == kk
            out[m] = np.minimum(table[kk][lo[m]], table[kk][hi[m] - (1 << kk) + 1])
        return out

    my = rank[starts]
    lo = np.zeros(len(nodes), dtype=np.int64)
    hi = my.copy()
    while True:                                 # first rank sharing the palindrome as prefix
        act = lo < hi
        if not act.any():
            break
        mid = (lo + hi) // 2
        ok = np.zeros(len(nodes), dtype=bool)
        a = np.flatnonzero(act)
        ok[a] = range_min(mid[a] + 1, my[a]) >= lens[a]
        hi = np.where(act & ok, mid, hi)
        lo = np.where(act & ~ok, mid + 1, lo)
    order = np.lexsort((lens, lo))

    H = [0] * (n + 1)
    pw = [1] * (n + 1)
    for i, ch in enumerate(s):
        H[i + 1] = (H[i] * BASE + ord(ch)) % MOD
        pw[i + 1] = pw[i] * BASE % MOD
    cum, vals = [], []
    run = 0
    st_l, ln_l = starts.tolist(), lens.tolist()
    for t in order.tolist():
        run += cnt[nodes[t]]
        cum.append(run)
        a = st_l[t]
        b = a + ln_l[t]
        vals.append((H[b] - H[a] * pw[b - a]) % MOD)
    out = [vals[bisect_left(cum, k)] if k <= run else -1 for k in ks]
    sys.stdout.write('\n'.join(map(str, out)) + '\n')


main()
```

**Watch out.**
- Occurrences count separately: in `abcba` the order is `a, a, abcba, b, b, bcb, c`.
- An eertree node's count is only complete after adding the counts of all longer palindromes that link to it (reverse creation order).
- `k` can be as large as `n(n+1)/2`, so values beyond the total give `-1`.

```stdin
5 7
abcba
1
2
3
4
6
7
8
```

```stdout
97
97
696207567
98
29493435
99
-1
```

### Lazy White Falcon

**Problem.** In a tree with values that start at 0: `1 u x` sets node `u` to `x`, and `2 u v` prints the sum of the values on the path `u–v`.

**Idea.** Let `R(v)` be the sum on the path root → `v`. A node's value contributes to `R` for every node in its subtree, so changing it by `d` is a **range add of `d` over its Euler interval**, and `R(v)` is a Fenwick point query. The path sum is `R(u) + R(v) − 2·R(lca) + value(lca)`.

**Steps.**
1. BFS for parents and depths; preorder `tin` and `size`; binary lifting.
2. Assign: `d = x − old`, then range-add `d`.
3. Query: LCA, then the formula above.

```python
import sys


def main():
    data = sys.stdin.buffer.read().split()
    n, q = int(data[0]), int(data[1])
    adj = [[] for _ in range(n)]
    p = 2
    for _ in range(n - 1):
        a = int(data[p]); b = int(data[p + 1]); p += 2
        adj[a].append(b)
        adj[b].append(a)
    parent = [0] * n
    depth = [0] * n
    order = [0]
    seen = [False] * n
    seen[0] = True
    for u in order:
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                parent[v] = u
                depth[v] = depth[u] + 1
                order.append(v)
    size = [1] * n
    for u in reversed(order):
        if u:
            size[parent[u]] += size[u]
    tin = [0] * n
    st = [0]
    t = 0
    while st:                                   # preorder: subtrees become contiguous
        u = st.pop()
        t += 1
        tin[u] = t
        for v in adj[u]:
            if v and parent[v] == u:
                st.append(v)
    LOG = max(1, (n - 1).bit_length())
    up = [parent[:]]
    for _ in range(LOG - 1):
        prev = up[-1]
        up.append([prev[prev[v]] for v in range(n)])

    def lca(a, b):
        if depth[a] < depth[b]:
            a, b = b, a
        d = depth[a] - depth[b]
        k = 0
        while d:
            if d & 1:
                a = up[k][a]
            d >>= 1
            k += 1
        if a == b:
            return a
        for k in range(LOG - 1, -1, -1):
            if up[k][a] != up[k][b]:
                a = up[k][a]
                b = up[k][b]
        return up[0][a]

    tree = [0] * (n + 2)

    def add(i, v):
        while i <= n:
            tree[i] += v
            i += i & -i

    def root_sum(u):
        i = tin[u]
        s = 0
        while i:
            s += tree[i]
            i -= i & -i
        return s

    val = [0] * n
    out = []
    for _ in range(q):
        typ = data[p]; u = int(data[p + 1]); v = int(data[p + 2]); p += 3
        if typ == b'1':
            d = v - val[u]
            if d:
                val[u] = v
                add(tin[u], d)
                add(tin[u] + size[u], -d)
        else:
            l = lca(u, v)
            out.append(root_sum(u) + root_sum(v) - 2 * root_sum(l) + val[l])
    sys.stdout.write('\n'.join(map(str, out)) + ('\n' if out else ''))


main()
```

**Watch out.**
- The query **assigns** a value rather than adding one, so keep the current values and add the difference.
- Nodes are 0-based here.
- `R(lca)` is subtracted twice, so the LCA's own value is added back once.

```stdin
3 3
0 1
1 2
1 0 1
1 1 2
2 0 2
```

```stdout
3
```
