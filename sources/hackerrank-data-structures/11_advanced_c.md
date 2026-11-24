## Advanced

### Ticket to Ride

**Problem.** A tree has weighted roads, and there are `m` tickets `(a, b, c)`. Choose a path `u–v`. You gain every ticket whose two cities both lie on the path, and you pay the path length. Maximise the profit; `u = v` gives 0.

**Idea.** Fix `u` and look at `value(v) = (tickets inside path(u, v)) − dist(u, v)`. A ticket `(a, b)` lies inside `path(u, v)` exactly when `u` is in the "a-side" region and `v` in the "b-side" region, or the other way round. With the tree rooted at 0:
- if neither endpoint is an ancestor of the other, the regions are `subtree(a)` and `subtree(b)`;
- if `a` is an ancestor of `b` with child `ch` toward `b`, the regions are "everything outside `subtree(ch)`" and `subtree(b)`.

Walk `u` through the tree in DFS order. Each time `u` enters or leaves a subtree, a few **range additions over `v`'s preorder positions** fire. Moving across an edge of length `L` adds `+L` inside the subtree and `−L` everywhere else. The `−L` part is kept as a scalar offset. We need the global maximum after every step, over about `2n + 4m` range additions. That is done offline in **chunks of ~√n events**:
- inside a chunk, the chunk's endpoints cut the positions into segments that receive identical additions;
- a `(events × segments)` matrix with two cumulative sums gives every intermediate maximum at once;
- then the whole chunk is applied to the full array.

**Steps.**
1. Root the tree. Compute `tin`/`tout`, distances, and binary lifting (to find the child of `a` toward `b`).
2. Turn every ticket into a starting addition and per-node enter events (undone on exit).
3. Generate the DFS event stream and record, for each visited `u`, how many events came before it and the current offset.
4. Process the events in chunks; the answer is the largest value seen (and at least 0).

```python
import sys

import numpy as np


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    adj = [[] for _ in range(n)]
    p = 1
    for _ in range(n - 1):
        a = int(data[p]) - 1; b = int(data[p + 1]) - 1; w = int(data[p + 2]); p += 3
        adj[a].append((b, w))
        adj[b].append((a, w))
    m = int(data[p]); p += 1
    tickets = []
    for _ in range(m):
        tickets.append((int(data[p]) - 1, int(data[p + 1]) - 1, int(data[p + 2])))
        p += 3
    parent = [-1] * n
    plen = [0] * n
    depth = [0] * n
    dist = [0] * n
    order = []
    st = [0]
    seen = [False] * n
    seen[0] = True
    while st:
        u = st.pop()
        order.append(u)
        for v, w in adj[u]:
            if not seen[v]:
                seen[v] = True
                parent[v] = u
                plen[v] = w
                depth[v] = depth[u] + 1
                dist[v] = dist[u] + w
                st.append(v)
    tin = [0] * n
    for i, u in enumerate(order):
        tin[u] = i
    size = [1] * n
    for u in reversed(order):
        if parent[u] >= 0:
            size[parent[u]] += size[u]
    tout = [tin[u] + size[u] for u in range(n)]
    LOG = max(1, (n - 1).bit_length())
    up = [[x if x >= 0 else 0 for x in parent]]
    for _ in range(LOG - 1):
        prev = up[-1]
        up.append([prev[prev[v]] for v in range(n)])

    def lift(v, d):                             # ancestor of v at depth d
        k = 0
        diff = depth[v] - d
        while diff:
            if diff & 1:
                v = up[k][v]
            diff >>= 1
            k += 1
        return v

    def is_anc(a, b):
        return tin[a] <= tin[b] < tout[a]

    on_enter = [[] for _ in range(n)]           # (l, r, w): added when u enters x, undone on exit
    base = np.array([-dist[v] for v in order], dtype=np.int64)    # u = root
    diff0 = np.zeros(n + 1, dtype=np.int64)
    for a, b, c in tickets:
        if a == b:
            continue
        if is_anc(b, a):
            a, b = b, a
        if is_anc(a, b):
            ch = lift(b, depth[a] + 1)
            diff0[tin[b]] += c                  # the root is outside subtree(ch)
            diff0[tout[b]] -= c
            on_enter[ch].append((tin[b], tout[b], -c))
            if tin[ch] > 0:
                on_enter[b].append((0, tin[ch], c))
            if tout[ch] < n:
                on_enter[b].append((tout[ch], n, c))
        else:
            on_enter[a].append((tin[b], tout[b], c))
            on_enter[b].append((tin[a], tout[a], c))
    base += np.cumsum(diff0[:n])

    ev_l, ev_r, ev_w = [], [], []
    q_at, q_off = [], []
    offset = 0
    kids = [[] for _ in range(n)]
    for u in order[1:]:
        kids[parent[u]].append(u)
    stack = [(0, True)]
    while stack:
        x, enter = stack.pop()
        if enter:
            if x:                               # u moves down the edge (parent, x)
                offset -= plen[x]
                ev_l.append(tin[x]); ev_r.append(tout[x]); ev_w.append(2 * plen[x])
            for l, r, w in on_enter[x]:
                ev_l.append(l); ev_r.append(r); ev_w.append(w)
            q_at.append(len(ev_l))
            q_off.append(offset)
            stack.append((x, False))
            for v in kids[x]:
                stack.append((v, True))
        else:
            for l, r, w in on_enter[x]:
                ev_l.append(l); ev_r.append(r); ev_w.append(-w)
            if x:
                offset += plen[x]
                ev_l.append(tin[x]); ev_r.append(tout[x]); ev_w.append(-2 * plen[x])
    E = len(ev_l)
    ev_l = np.array(ev_l, dtype=np.int64)
    ev_r = np.array(ev_r, dtype=np.int64)
    ev_w = np.array(ev_w, dtype=np.int64)
    q_at = np.array(q_at, dtype=np.int64)
    q_off = np.array(q_off, dtype=np.int64)

    best = 0
    V = base
    K = max(64, int((n / 2) ** 0.5))
    qi, nq = 0, len(q_at)
    while qi < nq and q_at[qi] == 0:
        best = max(best, int(V.max()) + int(q_off[qi]))
        qi += 1
    for e0 in range(0, E, K):
        e1 = min(E, e0 + K)
        l, r, w = ev_l[e0:e1], ev_r[e0:e1], ev_w[e0:e1]
        bounds = np.unique(np.concatenate(([0, n], l, r)))
        seg_max = np.maximum.reduceat(V, bounds[:-1])
        S = len(bounds) - 1
        k = e1 - e0
        M = np.zeros((k, S + 1), dtype=np.int64)
        rows = np.arange(k)
        M[rows, np.searchsorted(bounds, l)] = w
        M[rows, np.searchsorted(bounds, r)] -= w
        np.cumsum(M, axis=1, out=M)             # per-event addition on each segment
        np.cumsum(M, axis=0, out=M)             # accumulated after each event
        qj = qi
        while qj < nq and q_at[qj] <= e1:
            qj += 1
        if qj > qi:
            vals = (M[q_at[qi:qj] - e0 - 1, :S] + seg_max).max(axis=1) + q_off[qi:qj]
            best = max(best, int(vals.max()))
            qi = qj
        d = np.zeros(n + 1, dtype=np.int64)
        np.add.at(d, l, w)
        np.add.at(d, r, -w)
        V = V + np.cumsum(d[:n])
    print(best)


main()
```

**Watch out.**
- The two regions of a ticket are disjoint, so a ticket is never counted twice.
- The root starts **outside** `subtree(ch)`, which is why ancestor-type tickets contribute to the starting array.
- Values reach about `10¹⁴`, which is fine in int64.
- About 3–4 s for `n = 2·10⁵` and `m = 10⁵`.

```stdin
7
1 2 1
1 3 1
1 4 4
4 5 1
4 6 1
4 7 1
5
5 7 3
3 6 2
3 4 10
2 7 15
1 6 7
```

```stdout
13
```

### Heavy Light White Falcon

**Problem.** In a tree with values that start at 0: `1 u x` assigns `x` to node `u`, and `2 u v` prints the maximum value on the path `u–v`.

**Idea.** Use **heavy-light decomposition**: every heavy chain is a contiguous block of positions, so a path splits into `O(log n)` position ranges. An iterative max segment tree over those positions answers each range. A point assignment updates one leaf and its ancestors.

**Steps.**
1. BFS for parents and depths, then subtree sizes and heavy children. Lay the chains out to get `head` and `pos`.
2. Query: while the heads differ, take the range of the deeper head's chain and jump above it; finish with the range between the two nodes.

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
    for u in reversed(order):
        if parent[u] >= 0:
            size[parent[u]] += size[u]
    heavy = [-1] * n
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
    while st:
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
    size2 = 1
    while size2 < n:
        size2 *= 2
    seg = [0] * (2 * size2)

    def range_max(l, r):                        # inclusive
        l += size2
        r += size2 + 1
        res = 0
        while l < r:
            if l & 1:
                if seg[l] > res:
                    res = seg[l]
                l += 1
            if r & 1:
                r -= 1
                if seg[r] > res:
                    res = seg[r]
            l >>= 1
            r >>= 1
        return res

    out = []
    for _ in range(q):
        t = data[p]; u = int(data[p + 1]); v = int(data[p + 2]); p += 3
        if t == b'1':
            i = pos[u] + size2
            seg[i] = v
            i >>= 1
            while i:
                a, b = seg[2 * i], seg[2 * i + 1]
                seg[i] = a if a > b else b
                i >>= 1
        else:
            res = 0
            while head[u] != head[v]:
                if depth[head[u]] < depth[head[v]]:
                    u, v = v, u
                res = max(res, range_max(pos[head[u]], pos[u]))
                u = parent[head[u]]
            a, b = sorted((pos[u], pos[v]))
            out.append(max(res, range_max(a, b)))
    sys.stdout.write('\n'.join(map(str, out)) + ('\n' if out else ''))


main()
```

**Watch out.**
- Values are positive and start at 0, so 0 is a safe identity for max.
- The chain layout must put each chain's nodes in consecutive positions from head to tail; the inner `while u != -1` loop does exactly that.

```stdin
3 3
0 1
1 2
1 0 1
1 1 2
2 0 2
```

```stdout
2
```

### Sum of the Maximums

**Problem.** For each query `[L, R]`, print the sum of `max(A[l..r])` over all `L ≤ l ≤ r ≤ R`.

**Idea.** Let `m` be the position of a maximum of `[L, R]`.
- Subsegments containing `m` contribute `A_m·(m−L+1)·(R−m+1)`.
- For subsegments inside `(m, R]`, use `E[r] = Σ_{l ≤ r} max(A[l..r])` over **all** `l` (found with the previous-greater stack). For `l ≤ m`, `max(A[l..r]) = max(A[l..m])`, because `A_m` dominates `[m, r]`. So `Σ_{l=m+1}^{r} max = E[r] − E[m]`, and the whole right part is a prefix-sum expression.
- The left part is symmetric, using `E2[l] = Σ_{r ≥ l} max(A[l..r])`.

Each query is `O(1)` after an argmax sparse table (vectorised). The sums exceed int64, so the final arithmetic uses Python ints.

**Steps.**
1. Monotonic stacks give `E` and `E2`, plus prefix sums `PE` and `PE2`.
2. Argmax sparse table; compute `m` for every query with numpy.
3. `ans = A_m(m−L+1)(R−m+1) + (PE[R+1]−PE[m+1]−(R−m)E[m]) + (PE2[m]−PE2[L]−(m−L)E2[m])`.

```python
import sys

import numpy as np


def main():
    data = sys.stdin.buffer.read().split()
    n, m = int(data[0]), int(data[1])
    a = [int(x) for x in data[2:2 + n]]
    E = [0] * n                                 # sum over l <= r of max(a[l..r])
    st = []
    for r in range(n):
        while st and a[st[-1]] <= a[r]:
            st.pop()
        p = st[-1] if st else -1
        E[r] = (E[p] if p >= 0 else 0) + a[r] * (r - p)
        st.append(r)
    E2 = [0] * n                                # sum over r >= l of max(a[l..r])
    st = []
    for l in range(n - 1, -1, -1):
        while st and a[st[-1]] <= a[l]:
            st.pop()
        p = st[-1] if st else n
        E2[l] = (E2[p] if p < n else 0) + a[l] * (p - l)
        st.append(l)
    PE = [0] * (n + 1)
    PE2 = [0] * (n + 1)
    for i in range(n):
        PE[i + 1] = PE[i] + E[i]
        PE2[i + 1] = PE2[i] + E2[i]
    A = np.array(a, dtype=np.int64)
    idx = [np.arange(n, dtype=np.int64)]        # sparse table of argmax
    while (1 << len(idx)) <= n:
        prev = idx[-1]
        h = 1 << (len(idx) - 1)
        x, y = prev[:-h], prev[h:]
        idx.append(np.where(A[x] >= A[y], x, y))
    L = np.array(data[2 + n:2 + n + 2 * m:2], dtype=np.int64) - 1
    R = np.array(data[3 + n:3 + n + 2 * m:2], dtype=np.int64) - 1
    span = R - L + 1
    lg = np.zeros(m, dtype=np.int64)
    for j in range(1, len(idx)):
        lg += span >= (1 << j)
    M = np.empty(m, dtype=np.int64)
    for j in np.unique(lg).tolist():
        s = lg == j
        x = idx[j][L[s]]
        y = idx[j][R[s] - (1 << j) + 1]
        M[s] = np.where(A[x] >= A[y], x, y)
    out = []
    for l, r, mx in zip(L.tolist(), R.tolist(), M.tolist()):
        res = a[mx] * (mx - l + 1) * (r - mx + 1)
        res += PE[r + 1] - PE[mx + 1] - (r - mx) * E[mx]
        res += PE2[mx] - PE2[l] - (mx - l) * E2[mx]
        out.append(res)
    sys.stdout.write('\n'.join(map(str, out)) + '\n')


main()
```

**Watch out.**
- With ties any maximum position works, because the argument only needs `A_m ≥` everything in `[L, R]`.
- The total over all subsegments can reach about `10¹⁹`, past int64, which is why the prefix sums are Python lists.

```stdin
3 6
1 3 2
1 1
1 2
1 3
2 2
2 3
3 3
```

```stdout
1
7
15
3
8
2
```

### Number Game on a Tree

**Problem.** For a path's multiset of edge weights, players alternately remove a number that is `≤` the previous removal, and whoever cannot move loses. Count the unordered node pairs whose path lets the first player win.

**Idea.** The first player wins **iff some weight occurs an odd number of times**.
- If every count is even, the second player removes the same value again; that is always legal, and it restores the all-even state.
- Otherwise the first player removes the **smallest** odd-count value. That leaves every playable value (all `≤` it) with an even count.

So count the pairs where every weight's count is even. Give each distinct weight a random 63-bit label and XOR the labels along root paths into `h(v)`. A path is all-even exactly when `h(u) = h(v)`, up to negligible collision chance. The answer is `C(n,2) − Σ C(cnt,2)` over equal `h` groups.

**Steps.**
1. Per game: random labels per distinct weight, then BFS to get `h`.
2. Count equal values with `np.unique`.

```python
import random
import sys

import numpy as np


def main():
    data = sys.stdin.buffer.read().split()
    g = int(data[0])
    p = 1
    rng = random.Random(20240531)
    out = []
    for _ in range(g):
        n = int(data[p]); p += 1
        e = np.array(data[p:p + 3 * (n - 1)], dtype=np.int64).reshape(-1, 3)
        p += 3 * (n - 1)
        uniq, inv = np.unique(e[:, 2], return_inverse=True)
        labels = np.array([rng.getrandbits(63) for _ in range(len(uniq))], dtype=np.int64)
        lab = labels[inv].tolist()
        adj = [[] for _ in range(n)]
        for i, (u, v) in enumerate((e[:, :2] - 1).tolist()):
            adj[u].append((v, lab[i]))
            adj[v].append((u, lab[i]))
        h = [0] * n
        seen = [False] * n
        seen[0] = True
        order = [0]
        for u in order:
            hu = h[u]
            for v, w in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    h[v] = hu ^ w
                    order.append(v)
        _, cnt = np.unique(np.array(h, dtype=np.int64), return_counts=True)
        out.append(n * (n - 1) // 2 - int((cnt * (cnt - 1) // 2).sum()))
    sys.stdout.write('\n'.join(map(str, out)) + '\n')


main()
```

**Watch out.**
- The empty list (`u = v`) is excluded because the pairs are distinct.
- An XOR hash is the standard parity fingerprint; a collision needs two different weight multisets to hash alike, which has probability about `n²/2⁶³`.
- Weights can be 0; they get labels like any other value.

```stdin
3
5
1 2 2
1 3 1
3 4 1
3 5 2
5
1 2 0
2 3 2
3 4 2
4 5 0
5
1 2 0
1 3 1
3 4 0
3 5 2
```

```stdout
9
8
10
```

### Heavy Light 2 White Falcon

**Problem.** In a tree with values that start at 0, `1 u v x` adds `i·x` to the `i`-th node of the path `u → v` (with `i` starting at 1), and `2 u v` prints the path sum mod `10⁹+7`.

**Idea.** Use **heavy-light decomposition**. Positions increase down each chain. Going up from `u`, the path index **falls** as the position rises; on `v`'s side it **rises** with the position. So on every chain range the added amount is a linear function `A + B·pos`, which makes it a **range add of a linear function** with range-sum queries. A Fenwick tree stores, at the range start, the coefficients of the prefix-sum polynomial `S(x) = c₂x² + c₁x + c₀`. At `r+1` it cancels them and leaves the constant total. All three coefficients are packed into one Python int.

**Steps.**
1. Compute the path length `k`. Walk the chains, tracking the index of the current `u` end (counting up from 1) and of the `v` end (counting down from `k`).
2. Up-going range `[pos[h], pos[u]]`: `A = x·(iu + pos[u])`, `B = −x`. Down-going range `[pos[h], pos[v]]`: `A = x·(rv − pos[v])`, `B = x`.
3. Sum query: add `S(r) − S(l−1)` over the path's chain ranges.

```python
import sys

MOD = 10 ** 9 + 7
INV2 = (MOD + 1) // 2
SH = 64
MASK = (1 << SH) - 1


def main():
    data = sys.stdin.buffer.read().split()
    n, q = int(data[0]), int(data[1])
    adj = [[] for _ in range(n)]
    p = 2
    for _ in range(n - 1):
        a = int(data[p]); b = int(data[p + 1]); p += 2
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
    for u in reversed(order):
        if parent[u] >= 0:
            size[parent[u]] += size[u]
    heavy = [-1] * n
    for u in order:
        best = 0
        for v in adj[u]:
            if v != parent[u] and size[v] > best:
                best = size[v]
                heavy[u] = v
    head = [0] * n
    pos = [0] * n
    cur = 1                                     # 1-based for the Fenwick tree
    st = [0]
    while st:
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
    tree = [0] * (n + 2)                        # packed (c0, c1, c2) of S(x) = c2 x^2 + c1 x + c0

    def bit_add(i, packed):
        while i <= n:
            tree[i] += packed
            i += i & -i

    def prefix(x):
        i = x
        tot = 0
        while i:
            tot += tree[i]
            i -= i & -i
        c0 = tot & MASK
        c1 = (tot >> SH) & MASK
        c2 = tot >> (2 * SH)
        return (c2 * x * x + c1 * x + c0) % MOD

    def add_linear(l, r, A, B):                 # add A + B*pos for pos in [l, r]
        A %= MOD
        B %= MOD
        c2 = B * INV2 % MOD
        c1 = (A + B * INV2) % MOD
        c0 = (A * (1 - l) - B * (l - 1) * l % MOD * INV2) % MOD
        bit_add(l, c0 | (c1 << SH) | (c2 << (2 * SH)))
        if r + 1 <= n:
            total = (A * (r - l + 1) + B * ((l + r) * (r - l + 1) // 2 % MOD)) % MOD
            bit_add(r + 1, ((total - c0) % MOD) | (((-c1) % MOD) << SH) | (((-c2) % MOD) << (2 * SH)))

    out = []
    for _ in range(q):
        if data[p] == b'1':
            u = int(data[p + 1]); v = int(data[p + 2]); x = int(data[p + 3]); p += 4
            a, b = u, v
            while head[a] != head[b]:
                if depth[head[a]] < depth[head[b]]:
                    a, b = b, a
                a = parent[head[a]]
            lca = a if depth[a] < depth[b] else b
            iu, rv = 1, depth[u] + depth[v] - 2 * depth[lca] + 1
            while head[u] != head[v]:
                if depth[head[u]] >= depth[head[v]]:
                    h = head[u]
                    add_linear(pos[h], pos[u], x * (iu + pos[u]), -x)
                    iu += pos[u] - pos[h] + 1
                    u = parent[h]
                else:
                    h = head[v]
                    add_linear(pos[h], pos[v], x * (rv - pos[v]), x)
                    rv -= pos[v] - pos[h] + 1
                    v = parent[h]
            if pos[u] >= pos[v]:
                add_linear(pos[v], pos[u], x * (iu + pos[u]), -x)
            else:
                add_linear(pos[u], pos[v], x * (rv - pos[v]), x)
        else:
            u = int(data[p + 1]); v = int(data[p + 2]); p += 3
            res = 0
            while head[u] != head[v]:
                if depth[head[u]] < depth[head[v]]:
                    u, v = v, u
                h = head[u]
                res += prefix(pos[u]) - prefix(pos[h] - 1)
                u = parent[h]
            a, b = sorted((pos[u], pos[v]))
            res += prefix(b) - prefix(a - 1)
            out.append(res % MOD)
    sys.stdout.write('\n'.join(map(str, out)) + ('\n' if out else ''))


main()
```

**Watch out.**
- `S(x)` for a range `[l, r]` is `A(x−l+1) + B(x(x+1)/2 − (l−1)l/2)`. Halving uses the modular inverse of 2.
- Every packed field is reduced mod `p` before packing, so all fields stay non-negative and never borrow into each other.

```stdin
3 2
0 1
1 2
1 0 2 1
2 1 2
```

```stdout
5
```

### Library Query

**Problem.** For several test cases, handle two kinds of queries on shelves with `1..1000` books each: `1 x k` sets shelf `x` to `k`, and `0 x y k` prints the `k`-th smallest count among shelves `x..y`.

**Idea.** The values are tiny, so keep **per-block prefix histograms**: `P[b, v]` is the number of shelves holding `v` books in the first `b` blocks of 128. A range histogram is one row difference plus two `bincount`s for the partial ends, and the `k`-th smallest is a `searchsorted` on its cumulative sum. An update changes one column of the later rows.

**Steps.**
1. Build `P` by `np.add.at` and a cumulative sum over blocks.
2. Update: `P[b+1:, old] −= 1` and `P[b+1:, new] += 1`.
3. Query: if it spans at most 2 blocks, sort the slice; otherwise combine the full blocks and the edges, then `searchsorted(cumsum, k)`.

```python
import sys

import numpy as np


def main():
    data = sys.stdin.buffer.read().split()
    t = int(data[0])
    p = 1
    out = []
    V = 1001
    B = 128
    for _ in range(t):
        n = int(data[p]); p += 1
        a = np.array(data[p:p + n], dtype=np.int64); p += n
        nb = (n + B - 1) // B
        cnt = np.zeros((nb, V), dtype=np.int32)
        np.add.at(cnt, (np.arange(n) // B, a), 1)
        P = np.zeros((nb + 1, V), dtype=np.int32)
        np.cumsum(cnt, axis=0, out=P[1:])
        q = int(data[p]); p += 1
        for _ in range(q):
            if data[p] == b'1':
                x = int(data[p + 1]) - 1; k = int(data[p + 2]); p += 3
                old = a[x]
                if old != k:
                    b = x // B
                    P[b + 1:, old] -= 1
                    P[b + 1:, k] += 1
                    a[x] = k
            else:
                x = int(data[p + 1]) - 1; y = int(data[p + 2]) - 1; k = int(data[p + 3]); p += 4
                bx, by = x // B, y // B
                if by - bx <= 1:
                    out.append(int(np.sort(a[x:y + 1])[k - 1]))
                    continue
                c = (P[by] - P[bx + 1]).astype(np.int64)       # full blocks bx+1 .. by-1
                c += np.bincount(a[x:(bx + 1) * B], minlength=V)
                c += np.bincount(a[by * B:y + 1], minlength=V)
                out.append(int(np.searchsorted(np.cumsum(c), k)))
    sys.stdout.write('\n'.join(map(str, out)) + '\n')


main()
```

**Watch out.**
- `searchsorted` (left side) on the cumulative counts returns the first value whose running count reaches `k`, which is the answer itself because the index equals the book count.
- Outputs from all test cases go one per line.

```stdin
2
2
1 2
2
0 1 2 1
0 1 2 2
4
4 3 2 1
4
0 1 1 1
1 1 1
0 1 1 1
0 1 4 3
```

```stdout
1
2
4
1
2
```

### Starfleet

**Problem.** Ships at `(x, y)` with frequencies `f` all move along the X axis. A query `YU YD T` takes the horizontal band `YD ≤ y ≤ YU` (unbounded in `x`) and asks how many ships share the most common frequency in it.

**Idea.** The band ignores `x`, so time and speed are irrelevant. Sort the ships by `y`; each query becomes an index range, and the task is **range mode frequency**, split by how often each frequency occurs (`S = √n`):
- **heavy frequencies** (more than `S` ships, at most `√n` of them): prefix-count columns `P`. A query's best heavy count is `max(P[hi] − P[lo])`, vectorised over chunks of queries.
- **light frequencies**: their mode is at most `S`. For `k = 1..S`, let `R_k[l]` be the smallest end position of `k` consecutive same-frequency ships starting at or after `l` (a suffix minimum). A light mode `≥ k` exists iff `R_k[lo] < hi`.

**Steps.**
1. Sort by `y`, compress the frequencies, and turn every query into `[lo, hi)` with `searchsorted`.
2. Heavy part with prefix-count columns.
3. Light part: group the light ships by frequency; for each `k`, pair every occurrence with the one `k−1` later in the same group.
4. The answer is the maximum of the two (0 for an empty band).

```python
import sys

import numpy as np


def main():
    data = sys.stdin.buffer.read().split()
    n, q = int(data[0]), int(data[1])
    ys = np.array(data[4:4 + 3 * n:3], dtype=np.int64)
    fs = np.array(data[5:5 + 3 * n:3], dtype=np.int64)
    order = np.argsort(ys, kind='stable')
    ys = ys[order]
    _, col = np.unique(fs[order], return_inverse=True)
    qa = np.array(data[3 + 3 * n::3][:q], dtype=np.int64)          # YU
    qb = np.array(data[4 + 3 * n::3][:q], dtype=np.int64)          # YD
    lo = np.searchsorted(ys, qb, side='left')
    hi = np.searchsorted(ys, qa, side='right')                    # ships lo .. hi-1
    ans = np.zeros(q, dtype=np.int64)
    S = max(1, int(n ** 0.5))
    counts = np.bincount(col)
    heavy = np.flatnonzero(counts > S)
    if len(heavy):
        P = np.zeros((n + 1, len(heavy)), dtype=np.int32)
        for j, f in enumerate(heavy.tolist()):
            P[1:, j] = np.cumsum(col == f)
        for s in range(0, q, 2048):
            e = min(q, s + 2048)
            ans[s:e] = (P[hi[s:e]] - P[lo[s:e]]).max(axis=1)
    occ = np.flatnonzero(counts[col] <= S)
    occ = occ[np.argsort(col[occ], kind='stable')]                # grouped by frequency
    grp = col[occ]
    best_light = np.zeros(q, dtype=np.int64)
    for k in range(1, S + 1):
        if k > len(occ):
            break
        same = grp[k - 1:] == grp[:len(grp) - k + 1]
        if not same.any():
            break
        R = np.full(n + 1, n + 1, dtype=np.int64)
        R[occ[:len(occ) - k + 1][same]] = occ[k - 1:][same]
        R = np.minimum.accumulate(R[::-1])[::-1]
        best_light[R[lo] < hi] = k
    ans = np.maximum(ans, best_light)
    sys.stdout.write('\n'.join(map(str, ans.tolist())) + '\n')


main()
```

**Watch out.**
- Boundary ships count, so `lo` uses `side='left'` on `YD` and `hi` uses `side='right'` on `YU`.
- Positions are distinct, so each start position receives exactly one end and a plain assignment replaces `minimum.at`.
- `R_k[lo]` never decreases as `k` grows, so the last `k` that passes is the light mode.

```stdin
5 5 82
-4 1 4
-3 -2 2
-3 5 1
0 -5 2
1 -1 2
1 -1 57
-2 -5 11
5 -5 40
-1 -5 16
5 -1 93
```

```stdout
1
2
3
3
1
```

### Almost Equal - Advanced

**Problem.** For each query `[l, r]`, count the pairs `i < j` inside it with `|H_i − H_j| ≤ K`. `N, Q ≤ 10⁵`.

**Idea.** Use **sqrt decomposition with heavy precomputation**, so that each query costs `O(1)` lookups plus one small merge. With blocks of `B = 1024`:
- `T[b, v]` is the number of elements in the first `b` blocks with value rank `< v`. Every element's partners lie in a rank window `[lo_r, hi_r)`, so `below[b, y]` (partners of `y` in blocks `< b`) is two gathers.
- `Pre` and `Suf` accumulate `below` inside each block. Then the partners of a **partial edge** inside the full middle blocks cost four lookups.
- `inner_pre` and `inner_suf` count the pairs inside a block prefix or suffix, using one `B×B` comparison per block.
- `W[b, c]` counts the pairs between blocks (from `Pre` at each block's last element), and `F` is its 2-D accumulation over block ranges.
- The only per-query merge is **left edge × right edge**, done with pre-sorted blocks and `searchsorted`.

**Steps.**
1. Pad the array to whole blocks with values far from everything, then build all the tables.
2. Query in a single block: sort it and count directly. Otherwise:
   `inner_suf[l] + inner_pre[r] + edge-vs-middle + F[f1, f2] + left×right`.

```python
import sys

import numpy as np


def main():
    data = sys.stdin.buffer.read().split()
    n, K = int(data[0]), int(data[1])
    H = np.array(data[2:2 + n], dtype=np.int64)
    q = int(data[2 + n])
    Ls = np.array(data[3 + n:3 + n + 2 * q:2], dtype=np.int64).tolist()
    Rs = np.array(data[4 + n:4 + n + 2 * q:2], dtype=np.int64).tolist()
    B = 1024
    nb = (n + B - 1) // B
    N = nb * B
    far = int(H.max()) + 2 * K + 10
    Hp = np.concatenate((H, far + (2 * K + 10) * np.arange(1, N - n + 1, dtype=np.int64)))
    uniq = np.unique(Hp)
    U = len(uniq)
    rank = np.searchsorted(uniq, Hp)
    lo_r = np.searchsorted(uniq, Hp - K, side='left')      # partners have rank in [lo_r, hi_r)
    hi_r = np.searchsorted(uniq, Hp + K, side='right')
    T = np.zeros((nb + 1, U + 1), dtype=np.int32)          # T[b, v]: blocks < b, rank < v
    for b in range(nb):
        T[b + 1, 1:] = T[b, 1:] + np.cumsum(np.bincount(rank[b * B:(b + 1) * B], minlength=U))
    below = T[:, hi_r] - T[:, lo_r]                       # partners of y inside blocks < b
    blk = below.reshape(nb + 1, nb, B)
    Pre = np.cumsum(blk, axis=2, dtype=np.int32).reshape(nb + 1, N)
    Suf = np.cumsum(blk[:, :, ::-1], axis=2, dtype=np.int32)[:, :, ::-1].reshape(nb + 1, N)
    del below, blk
    W = np.zeros((nb, nb), dtype=np.int64)
    inner_pre = np.zeros(N, dtype=np.int64)
    inner_suf = np.zeros(N, dtype=np.int64)
    tri = np.tri(B, B, -1, dtype=bool)                    # j < i
    for b in range(nb):
        v = Hp[b * B:(b + 1) * B]
        ok = (np.abs(v[:, None] - v[None, :]) <= K) & tri
        row = ok.sum(axis=1)                              # partners before i in the block
        inner_pre[b * B:(b + 1) * B] = np.cumsum(row)
        col = ok.sum(axis=0)                              # partners after j in the block
        inner_suf[b * B:(b + 1) * B] = np.cumsum(col[::-1])[::-1]
        W[b, b] = row.sum()
        G = Pre[:, (b + 1) * B - 1].astype(np.int64)      # block b's partners in blocks < c
        W[b, b + 1:] = G[b + 2:] - G[b + 1:-1]
    F = np.cumsum(W, axis=1)
    F = np.cumsum(F[::-1], axis=0)[::-1]                  # F[x, y]: x <= b <= c <= y
    order = np.argsort(Hp.reshape(nb, B), axis=1, kind='stable')
    sval = np.take_along_axis(Hp.reshape(nb, B), order, axis=1)
    spos = order + (np.arange(nb) * B)[:, None]
    out = []
    for l, r in zip(Ls, Rs):
        bl, br = l // B, r // B
        if bl == br:
            s = np.sort(H[l:r + 1])
            out.append(int((np.searchsorted(s, s + K, side='right') - np.arange(1, len(s) + 1)).sum()))
            continue
        f1, f2 = bl + 1, br - 1
        res = int(inner_suf[l] + inner_pre[r])
        res += int(Suf[f2 + 1, l]) - int(Suf[f1, l]) + int(Pre[f2 + 1, r]) - int(Pre[f1, r])
        if f1 <= f2:
            res += int(F[f1, f2])
        left = sval[bl][spos[bl] >= l]
        right = sval[br][spos[br] <= r]
        res += int((np.searchsorted(right, left + K, side='right')
                    - np.searchsorted(right, left - K, side='left')).sum())
        out.append(res)
    sys.stdout.write('\n'.join(map(str, out)) + '\n')


main()
```

**Watch out.**
- The padding values are spaced `2K+10` apart and start beyond `max + 2K`, so they never pair with anything.
- Prefix counts within one block stay below `1024 · 10⁵`, which fits int32 and keeps the tables near 120 MB.
- About 2.2 s for `N = Q = 10⁵`.

```stdin
5 2
1 3 4 3 0
3
0 1
1 3
0 4
```

```stdout
1
3
6
```

### Almost sorted interval

**Problem.** Count the intervals of a permutation whose first element is the minimum and whose last element is the maximum.

**Idea.** Fix the right end `r`. Two conditions must hold:
- `a_r` is the maximum, which means `l > pg(r)`, the previous greater element.
- `a_l` is the minimum, which means no smaller element lies in `(l, r]`. That holds exactly for the indices still on the **increasing (min) stack** after pushing `r`.

So the count for `r` is the number of min-stack entries above `pg(r)`. The stack holds increasing indices, so one `bisect` finds it. Both stacks run in the same loop.

**Steps.**
1. For each `r`: pop larger values from the min stack and push `r`. Pop smaller values from the max stack; its top is `pg(r)`; push `r`.
2. Add `len(mins) − bisect_right(mins, pg)`.

```python
import sys
from bisect import bisect_right


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    a = list(map(int, data[1:1 + n]))
    mins = []                                   # indices l with no smaller value after them so far
    maxs = []                                   # decreasing stack for previous greater
    total = 0
    for r in range(n):
        x = a[r]
        while mins and a[mins[-1]] > x:
            mins.pop()
        mins.append(r)
        while maxs and a[maxs[-1]] < x:
            maxs.pop()
        pg = maxs[-1] if maxs else -1
        maxs.append(r)
        total += len(mins) - bisect_right(mins, pg)
    print(total)


main()
```

**Watch out.**
- `r` itself is always counted (the single-element interval), because it is on the min stack and `r > pg(r)`.
- The answer can reach `n(n+1)/2 ≈ 5·10¹¹` for a sorted input.
- About 0.3 s for `N = 10⁶`.

```stdin
5
3 1 2 5 4
```

```stdout
8
```
