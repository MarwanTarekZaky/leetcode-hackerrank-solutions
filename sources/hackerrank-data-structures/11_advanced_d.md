## Advanced

### Burger Happiness

**Problem.** Restaurant `i` opens on day `i` at position `X_i`. Eating there gives `A_i`. Walking from `p` to the next restaurant `n` costs `B_k` for every **opened** restaurant `k` passed, counting `p` itself but not `n`. Tim starts at any restaurant, may jump only to the restaurant that opens that day, and can stop at any time. Print the best total, or 0.

**Idea.** Let `dp[i]` be the best total that ends by eating at `i`: `dp[i] = A_i + max(0, best jump into i)`. Let `S(x)` be the sum of `B` over opened restaurants left of `x`, and `S'(x)` the same for `≤ x`.
- A jump from the left gives `dp[j] + S(X_j) − S(X_i)`.
- A jump from the right gives `dp[j] − S'(X_j) + S'(X_i)`.

So keep, over the sorted positions, `V1[j] = dp[j] + S(X_j)` and `V2[j] = dp[j] − S'(X_j)`. Query a prefix max of `V1` and a suffix max of `V2`. When restaurant `i` opens, every `S(x)` with `x > X_i` grows by `B_i`, which is a **range add** on `V1` (and on `V2` for `x ≥ X_i`). Both arrays are numpy blocks with a lazy add per block. A Fenwick tree gives `S`.

**Steps.**
1. Compress the `X` values. For each day `i`, read `S(X_i)`, query both maxima, and set `dp[i]`.
2. Open `i`: suffix adds on `V1` and `V2`, Fenwick add. Then insert `V1[i]` and `V2[i]`.
3. Print the best `dp` (at least 0).

```python
import sys

import numpy as np

NEG = -(1 << 60)


class Blocks:
    """Range add / range max over numpy blocks with a lazy add per block."""

    def __init__(self, n, B):
        self.B = B
        self.nb = (n + B - 1) // B
        self.raw = np.full((self.nb, B), NEG, dtype=np.int64)
        self.flat = self.raw.reshape(-1)
        self.lazy = np.zeros(self.nb, dtype=np.int64)
        self.bmax = np.full(self.nb, NEG, dtype=np.int64)

    def add(self, l, r, v):                     # [l, r)
        if l >= r:
            return
        B = self.B
        bl, br = l // B, (r - 1) // B
        if bl == br:
            self.raw[bl, l - bl * B:r - bl * B] += v
            self.bmax[bl] = self.raw[bl].max()
            return
        self.raw[bl, l - bl * B:] += v
        self.bmax[bl] = self.raw[bl].max()
        self.raw[br, :r - br * B] += v
        self.bmax[br] = self.raw[br].max()
        if br > bl + 1:
            self.lazy[bl + 1:br] += v

    def max(self, l, r):                        # [l, r)
        if l >= r:
            return NEG
        B = self.B
        bl, br = l // B, (r - 1) // B
        if bl == br:
            return int(self.raw[bl, l - bl * B:r - bl * B].max()) + int(self.lazy[bl])
        res = max(int(self.raw[bl, l - bl * B:].max()) + int(self.lazy[bl]),
                  int(self.raw[br, :r - br * B].max()) + int(self.lazy[br]))
        if br > bl + 1:
            res = max(res, int((self.bmax[bl + 1:br] + self.lazy[bl + 1:br]).max()))
        return res

    def set(self, p, v):
        b = p // self.B
        val = v - int(self.lazy[b])
        self.flat[p] = val
        if val > self.bmax[b]:
            self.bmax[b] = val


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    X = [int(x) for x in data[1:1 + 3 * n:3]]
    A = [int(x) for x in data[2:2 + 3 * n:3]]
    Bv = [int(x) for x in data[3:3 + 3 * n:3]]
    rank = {x: i for i, x in enumerate(sorted(X))}
    pos = [rank[x] for x in X]
    fw = [0] * (n + 1)

    def fw_add(i, v):
        i += 1
        while i <= n:
            fw[i] += v
            i += i & -i

    def fw_sum(i):                              # opened B over positions < i
        s = 0
        while i:
            s += fw[i]
            i -= i & -i
        return s

    blk = max(64, int(n ** 0.5))
    V1 = Blocks(n, blk)                         # dp[j] + S(X_j)
    V2 = Blocks(n, blk)                         # dp[j] - S'(X_j)
    best = 0
    for i in range(n):
        p = pos[i]
        s = fw_sum(p)                           # S(X_i) = S'(X_i) while i is still closed
        cand = 0
        m1 = V1.max(0, p)
        if m1 > NEG // 2:
            cand = max(cand, m1 - s)
        m2 = V2.max(p + 1, n)
        if m2 > NEG // 2:
            cand = max(cand, m2 + s)
        dp = A[i] + cand
        best = max(best, dp)
        b = Bv[i]
        if b:                                   # restaurant i opens
            V1.add(p + 1, n, b)
            V2.add(p, n, -b)
            fw_add(p, b)
        V1.set(p, dp + s)
        V2.set(p, dp - (s + b))
    print(best)


main()
```

**Watch out.**
- The walking cost includes the **starting** restaurant's window (`X_p ≤ X_k`) but not the destination's.
- `dp[i]` may start fresh at `i`, which is the `max(0, …)`.
- Restaurant `i` is not open yet when `dp[i]` is computed.
- About 1.2 s for `N = 10⁵`.

```stdin
3
2 -5 1
1 5 1
3 5 1
```

```stdout
8
```

### Roy and alpha-beta trees

**Problem.** Over all BSTs that can be built from the `N` keys, sum `α·(keys on even levels) − β·(keys on odd levels)` (root at level 0), modulo `10⁹+9`.

**Idea.** The shapes depend only on the **sorted order**, so the answer is `Σ_p A_sorted[p]·(α·ev[N][p] − β·od[N][p])`. Here `ev[L][p]` and `od[L][p]` count the BSTs on `L` keys in which the key at sorted position `p` sits on an even or odd level. Build these tables once for every `L ≤ 150`. With root `r`, position `r` is even in `cnt[r]·cnt[L−1−r]` trees. Positions in a subtree flip parity, and their counts are scaled by the number of shapes of the other side. Each `(L, r)` pair is a few vectorised slice updates.

**Steps.**
1. `cnt[L]` (Catalan numbers mod p), then `ev` and `od` by length with numpy slices.
2. Per test: sort the keys and take the dot product with `α·ev − β·od`.

```python
import sys

import numpy as np

MOD = 10 ** 9 + 9
NMAX = 150


def tables():
    cnt = [1] * (NMAX + 1)
    for L in range(1, NMAX + 1):
        cnt[L] = sum(cnt[r] * cnt[L - 1 - r] for r in range(L)) % MOD
    ev = [np.zeros(0, dtype=np.int64)]
    od = [np.zeros(0, dtype=np.int64)]
    for L in range(1, NMAX + 1):
        e = np.zeros(L, dtype=np.int64)
        o = np.zeros(L, dtype=np.int64)
        for r in range(L):                      # root at sorted position r
            left, right = r, L - 1 - r
            cl, cr = cnt[left], cnt[right]
            e[r] = (e[r] + cl * cr) % MOD
            if left:                            # one level deeper: parity flips
                e[:r] = (e[:r] + od[left] * cr) % MOD
                o[:r] = (o[:r] + ev[left] * cr) % MOD
            if right:
                e[r + 1:] = (e[r + 1:] + od[right] * cl) % MOD
                o[r + 1:] = (o[r + 1:] + ev[right] * cl) % MOD
        ev.append(e)
        od.append(o)
    return ev, od


def main():
    data = sys.stdin.buffer.read().split()
    t = int(data[0])
    p = 1
    ev, od = tables()
    out = []
    for _ in range(t):
        n = int(data[p]); alpha = int(data[p + 1]); beta = int(data[p + 2]); p += 3
        a = sorted(int(x) for x in data[p:p + n]); p += n
        e, o = ev[n].tolist(), od[n].tolist()
        out.append(sum(a[i] * (alpha * e[i] - beta * o[i]) for i in range(n)) % MOD)
    sys.stdout.write('\n'.join(map(str, out)) + '\n')


main()
```

**Watch out.**
- Python's `%` already returns a non-negative result, which is what "keep adding `10⁹+9`" means.
- Products of two residues stay below `1.1·10¹⁸`, inside int64, as long as each is reduced before adding.

```stdin
4
1
1 1
1
2
1 1
1 2
3
1 1
1 2 3
5
1 1
1 2 3 4 5
```

```stdout
1
0
6
54
```

### Coloring Tree

**Problem.** For a rooted tree with node colours, answer queries "how many distinct colours are in the subtree of `s`?".

**Idea.** **Small-to-large merging**: process the nodes bottom-up, reuse the largest child's colour set, and pour the smaller sets into it. Each colour entry moves `O(log n)` times. Record the size of every node's set as its answer.

**Steps.**
1. BFS from the given root for the parents and the order.
2. In reverse order, merge the children's sets (keeping the biggest), add the node's own colour, and store `len(set)`.
3. Answer the queries by lookup.

```python
import sys


def main():
    data = sys.stdin.buffer.read().split()
    n, m, root = int(data[0]), int(data[1]), int(data[2]) - 1
    adj = [[] for _ in range(n)]
    p = 3
    for _ in range(n - 1):
        a = int(data[p]) - 1; b = int(data[p + 1]) - 1; p += 2
        adj[a].append(b)
        adj[b].append(a)
    color = data[p:p + n]; p += n
    parent = [-1] * n
    parent[root] = root
    order = [root]
    for u in order:
        for v in adj[u]:
            if parent[v] == -1:
                parent[v] = u
                order.append(v)
    sets = [None] * n
    ans = [0] * n
    for u in reversed(order):
        s = None
        for v in adj[u]:
            if parent[v] == u:                  # children only (parent[root] = root)
                t = sets[v]
                sets[v] = None
                if s is None:
                    s = t
                elif len(t) > len(s):
                    t.update(s)
                    s = t
                else:
                    s.update(t)
        if s is None:
            s = set()
        s.add(color[u])
        sets[u] = s
        ans[u] = len(s)
    out = [ans[int(x) - 1] for x in data[p:p + m]]
    sys.stdout.write('\n'.join(map(str, out)) + ('\n' if out else ''))


main()
```

**Watch out.**
- The root is given in the input, not fixed at 1.
- Colours are compared as raw byte strings, which is fine because equal integers have equal decimal text.
- `M` can be 0.

```stdin
4 2 1
1 2
2 4
2 3
10
20
20
30
1
2
```

```stdout
3
2
```

### Recalling Early Days GP with Trees

**Problem.** Every update adds a geometric progression along a path: `X` on `i`, `X·R` on the next node, and so on up to `j`. All `U` updates come before the `Q` path-sum queries, so the problem is **offline**. Answers are mod `100711433`, which is prime.

**Idea.** Split each update at the LCA:
- **Upward part (`i` to lca):** a term travels up, multiplying by `R` per level. Start it at `i` with `X`, accumulate bottom-up as `up[v] = start[v] + R·Σ up[children]`, and cancel `X·R^{a+1}` at `parent(lca)`, where `a = depth(i) − depth(lca)`.
- **Downward part (lca to `j`):** seen from `j` it is a progression with ratio `R⁻¹`. Start it at `j` with `X·R^{dist}`, accumulate with `R⁻¹`, and cancel `X·R^a` at the LCA, which already belongs to the upward part.

After one bottom-up pass the node values are known. Root prefix sums answer each query as `S(i) + S(j) − 2S(lca) + val(lca)`. The LCAs of all pairs come from **vectorised binary lifting**. If `R ≡ 0 (mod p)`, only the first term survives.

**Steps.**
1. BFS order and depths; a lifting table as numpy arrays; LCAs for all updates and all queries at once.
2. Accumulate the start and cancel terms, then do one reverse-BFS pass with ratios `R` and `R⁻¹`.
3. Prefix sums and the query formula.

```python
import sys

import numpy as np

P = 100711433


def main():
    data = sys.stdin.buffer.read().split()
    n, R = int(data[0]), int(data[1]) % P
    adj = [[] for _ in range(n)]
    p = 2
    for _ in range(n - 1):
        a = int(data[p]) - 1; b = int(data[p + 1]) - 1; p += 2
        adj[a].append(b)
        adj[b].append(a)
    U, Q = int(data[p]), int(data[p + 1]); p += 2
    upd = np.array(data[p:p + 3 * U], dtype=np.int64).reshape(U, 3); p += 3 * U
    qry = np.array(data[p:p + 2 * Q], dtype=np.int64).reshape(Q, 2)
    parent = [-1] * n
    parent[0] = 0
    depth = [0] * n
    order = [0]
    for u in order:
        for v in adj[u]:
            if parent[v] == -1:
                parent[v] = u
                depth[v] = depth[u] + 1
                order.append(v)
    dep = np.array(depth, dtype=np.int64)
    LOG = max(1, (n - 1).bit_length())
    up = [np.array(parent, dtype=np.int64)]
    for _ in range(LOG - 1):
        up.append(up[-1][up[-1]])

    def lca(a, b):                              # vectorised binary lifting
        swap = dep[a] < dep[b]
        a, b = np.where(swap, b, a), np.where(swap, a, b)
        diff = dep[a] - dep[b]
        for k in range(LOG):
            a = np.where((diff >> k) & 1 == 1, up[k][a], a)
        for k in range(LOG - 1, -1, -1):
            ua, ub = up[k][a], up[k][b]
            m = ua != ub
            a = np.where(m, ua, a)
            b = np.where(m, ub, b)
        return np.where(a == b, a, up[0][a])

    val = [0] * n
    ui, uj, ux = upd[:, 0] - 1, upd[:, 1] - 1, upd[:, 2]
    if R == 0:                                  # every term after the first is 0
        for i, x in zip(ui.tolist(), ux.tolist()):
            val[i] = (val[i] + x) % P
    else:
        pw = [1] * (2 * n + 2)
        for k in range(1, 2 * n + 2):
            pw[k] = pw[k - 1] * R % P
        Rinv = pow(R, P - 2, P)
        start_up = [0] * n
        start_dn = [0] * n
        for i, j, x, l in zip(ui.tolist(), uj.tolist(), ux.tolist(), lca(ui, uj).tolist()):
            a = depth[i] - depth[l]
            dist = a + depth[j] - depth[l]
            start_up[i] += x
            if l != 0:
                start_up[parent[l]] -= x * pw[a + 1]
            start_dn[j] += x * pw[dist]
            start_dn[l] -= x * pw[a]
        acc_up = [0] * n
        acc_dn = [0] * n
        for v in reversed(order):
            cu = (start_up[v] + R * acc_up[v]) % P
            cd = (start_dn[v] + Rinv * acc_dn[v]) % P
            val[v] = (cu + cd) % P
            if v:
                acc_up[parent[v]] += cu
                acc_dn[parent[v]] += cd
    S = [0] * n
    for v in order:
        S[v] = (val[v] + (S[parent[v]] if v else 0)) % P
    qi, qj = qry[:, 0] - 1, qry[:, 1] - 1
    ql = lca(qi, qj)
    Sa = np.array(S, dtype=np.int64)
    Va = np.array(val, dtype=np.int64)
    ans = (Sa[qi] + Sa[qj] - 2 * Sa[ql] + Va[ql]) % P
    sys.stdout.write('\n'.join(map(str, ans.tolist())) + '\n')


main()
```

**Watch out.**
- When `j` is the LCA, the downward start and cancel hit the same node with the same value and cancel out, as they should.
- `R` can be a multiple of the modulus (`R ≤ 10⁹`), in which case `R⁻¹` does not exist and the special case applies.

```stdin
6 2
1 2
1 4
2 6
4 5
4 3
2 2
1 6 3
5 3 5
6 4
5 1
```

```stdout
31
18
```

### Swaps and Sum

**Problem.** Query type 1 swaps the elements of `[l, r]` in adjacent pairs; type 2 prints the sum of `[l, r]`. `n, q ≤ 2·10⁵`.

**Idea.** Split the array into the **odd-position** sequence and the **even-position** sequence. A pair swap on `[l, r]` exchanges equal-length pieces between them: `odd[a:a+h] ↔ even[a:a+h]` when `l` is odd, and `even[a:a+h] ↔ odd[a+1:a+1+h]` when `l` is even. Store each sequence as a **rope of numpy views** with cached sums. Cutting at a position splits one chunk, and the swap just exchanges chunk lists. When the number of chunks grows too large, flatten and rebuild.

**Steps.**
1. Build ropes of chunks of up to 2048 elements for the odd and even sequences.
2. Type 1: cut both ropes at the piece boundaries and swap the chunk slices.
3. Type 2: odd indices `[l//2, (r+1)//2)` plus even indices `[(l−1)//2, r//2)`, using cached chunk sums and partial numpy sums.

```python
import sys
from bisect import bisect_right
from itertools import accumulate

import numpy as np


class Rope:
    def __init__(self, arr, B):
        self.B = B
        self.build(arr)

    def build(self, arr):
        B = self.B
        self.chunks = [arr[i:i + B] for i in range(0, len(arr), B)]
        self.sums = [int(c.sum()) for c in self.chunks]
        self.lens = [len(c) for c in self.chunks]
        self.dirty = True

    def starts(self):
        if self.dirty:
            self.st = [0] + list(accumulate(self.lens))
            self.dirty = False
        return self.st

    def cut(self, pos):                         # make pos a chunk boundary, return its index
        st = self.starts()
        k = bisect_right(st, pos) - 1
        if k >= len(self.chunks) or st[k] == pos:
            return k
        c = self.chunks[k]
        off = pos - st[k]
        left, right = c[:off], c[off:]
        if off <= len(c) - off:
            sl = int(left.sum())
            sr = self.sums[k] - sl
        else:
            sr = int(right.sum())
            sl = self.sums[k] - sr
        self.chunks[k:k + 1] = [left, right]
        self.sums[k:k + 1] = [sl, sr]
        self.lens[k:k + 1] = [off, len(c) - off]
        self.dirty = True
        return k + 1

    def flatten(self):
        return np.concatenate(self.chunks) if self.chunks else np.zeros(0, dtype=np.int64)

    def range_sum(self, l, r):                  # [l, r)
        if l >= r:
            return 0
        st = self.starts()
        kl = bisect_right(st, l) - 1
        kr = bisect_right(st, r - 1) - 1
        if kl == kr:
            return int(self.chunks[kl][l - st[kl]:r - st[kl]].sum())
        res = int(self.chunks[kl][l - st[kl]:].sum()) + int(self.chunks[kr][:r - st[kr]].sum())
        if kr > kl + 1:
            res += sum(self.sums[kl + 1:kr])
        return res


def main():
    data = sys.stdin.buffer.read().split()
    n, q = int(data[0]), int(data[1])
    a = np.array(data[2:2 + n], dtype=np.int64)
    B = max(16, min(2048, n // 64))
    odd = Rope(a[0::2].copy(), B)               # positions 1, 3, 5, ...
    even = Rope(a[1::2].copy(), B)              # positions 2, 4, 6, ...
    out = []
    p = 2 + n
    for _ in range(q):
        t = data[p]; l = int(data[p + 1]); r = int(data[p + 2]); p += 3
        if t == b'1':
            half = (r - l + 1) // 2
            if l % 2 == 1:
                oa = ea = (l - 1) // 2
            else:
                ea = l // 2 - 1
                oa = ea + 1
            o1, o2 = odd.cut(oa), odd.cut(oa + half)
            e1, e2 = even.cut(ea), even.cut(ea + half)
            oc, os_, ol = odd.chunks[o1:o2], odd.sums[o1:o2], odd.lens[o1:o2]
            ec, es, el = even.chunks[e1:e2], even.sums[e1:e2], even.lens[e1:e2]
            odd.chunks[o1:o2], odd.sums[o1:o2], odd.lens[o1:o2] = ec, es, el
            even.chunks[e1:e2], even.sums[e1:e2], even.lens[e1:e2] = oc, os_, ol
            odd.dirty = even.dirty = True
            if len(odd.chunks) + len(even.chunks) > 3 * (n // B + 2):
                odd.build(odd.flatten())
                even.build(even.flatten())
        else:
            out.append(odd.range_sum(l // 2, (r + 1) // 2) + even.range_sum((l - 1) // 2, r // 2))
    sys.stdout.write('\n'.join(map(str, out)) + ('\n' if out else ''))


main()
```

**Watch out.**
- When `l` is even, the pair `(l, l+1)` is `(even, odd)` and the odd index is **one ahead** of the even index. That shift is why a plain two-array swap is not enough without a rope.
- Chunks are views and are never written to, so sharing them between ropes is safe.
- About 2 s for `n = q = 2·10⁵`.

```stdin
6 4
1 2 3 4 5 6
1 2 5
2 2 3
2 3 4
2 4 5
```

```stdout
5
7
9
```

### Arithmetic Progressions

**Problem.** Take the product of the sequences `(a_k + d_k·t)^{p_k}` over a range of APs. Print the smallest `K` for which the `K`-th difference is constant, and that constant mod `1000003`. Updates add `v` to every `p_k` in a range.

**Idea.** The product is a polynomial in `t` of degree `K = Σ p_k` with leading coefficient `Π d_k^{p_k}`. Its `K`-th difference is the constant `K!·Π d_k^{p_k}`. Using a **primitive root** `g` modulo the prime `1000003`, write `d_k = g^{e_k}`. Then `Π d_k^{p_k} = g^{Σ e_k p_k}`, so both `Σ p` and `Σ e·p` under range adds to `p` are range-add/range-sum problems. Three Fenwick arrays (diff, diff·(j−1), diff·W[j−1], with `W` the prefix sums of `e`) handle them. If `K ≥ 1000003`, then `K! ≡ 0`.

**Steps.**
1. Find a primitive root, the discrete logs of the needed `d` values, and the factorials mod p.
2. Update: `diff[i] += v` and `diff[j+1] −= v` in the three Fenwick arrays.
3. Query: `K` and `E = Σ e·p` from prefix differences, then `V = K!·g^{E mod (p−1)}`.

```python
import sys

MOD = 1000003


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    d = [int(x) for x in data[2:2 + 3 * n:3]]
    pp = [int(x) for x in data[3:3 + 3 * n:3]]
    pos = 1 + 3 * n
    q = int(data[pos]); pos += 1
    m, f, fac = MOD - 1, 2, []
    while f * f <= m:
        if m % f == 0:
            fac.append(f)
            while m % f == 0:
                m //= f
        f += 1
    if m > 1:
        fac.append(m)
    g = 2
    while any(pow(g, (MOD - 1) // f, MOD) == 1 for f in fac):
        g += 1
    need = set(d)
    log = {}
    x = 1
    for k in range(MOD - 1):                    # discrete logs of the d values
        if x in need and x not in log:
            log[x] = k
            if len(log) == len(need):
                break
        x = x * g % MOD
    e = [log[v] for v in d]
    fact = [1] * MOD
    for i in range(1, MOD):
        fact[i] = fact[i - 1] * i % MOD
    W = [0] * (n + 1)
    P0 = [0] * (n + 1)
    PE = [0] * (n + 1)
    for i in range(n):
        W[i + 1] = W[i] + e[i]
        P0[i + 1] = P0[i] + pp[i]
        PE[i + 1] = PE[i] + e[i] * pp[i]
    b1 = [0] * (n + 2)
    b2 = [0] * (n + 2)
    b3 = [0] * (n + 2)

    def upd(j, v):                              # diff[j] += v (1-based)
        v2 = v * (j - 1)
        v3 = v * W[j - 1]
        while j <= n:
            b1[j] += v
            b2[j] += v2
            b3[j] += v3
            j += j & -j

    def pref(x):                                # (sum of p, sum of e*p) over 1..x
        s1 = s2 = s3 = 0
        i = x
        while i:
            s1 += b1[i]
            s2 += b2[i]
            s3 += b3[i]
            i -= i & -i
        return P0[x] + s1 * x - s2, PE[x] + s1 * W[x] - s3

    out = []
    for _ in range(q):
        if data[pos] == b'0':
            i = int(data[pos + 1]); j = int(data[pos + 2]); pos += 3
            k1, e1 = pref(j)
            k0, e0 = pref(i - 1)
            K = k1 - k0
            V = 0 if K >= MOD else fact[K] * pow(g, (e1 - e0) % (MOD - 1), MOD) % MOD
            out.append(f"{K} {V}")
        else:
            i = int(data[pos + 1]); j = int(data[pos + 2]); v = int(data[pos + 3]); pos += 4
            upd(i, v)
            if j + 1 <= n:
                upd(j + 1, -v)
    sys.stdout.write('\n'.join(out) + ('\n' if out else ''))


main()
```

**Watch out.**
- `d_k ≤ 10⁴ < 1000003`, so every `d_k` is invertible and has a discrete log.
- `K` is printed exactly (it can reach about `10¹³`); only `V` is reduced.
- The `a_k` values do not matter at all.

```stdin
2
1 2 1
5 3 1
3
0 1 2
1 1 1 1
0 1 1
```

```stdout
2 12
2 8
```

### Coolguy and Two Subsequences

**Problem.** Sum `min(min A[a..b], min A[c..d])` over all `a ≤ b < c ≤ d`, mod `10⁹+7`. `N ≤ 2·10⁵`.

**Idea.** Write the minimum as a sum over thresholds: `min = Σ_k (u_k − u_{k+1})·[min ≥ u_k]` over the sorted distinct values `u₁ > u₂ > …`. So we need `F(t)`, the number of ordered disjoint pairs of subarrays lying entirely in `{i : A_i ≥ t}`. Those positions form runs. A run of length `L` has `g(L) = L(L+1)/2` subarrays and `h(L) = C(L+2, 4)` ordered disjoint pairs inside it. Then `F = Σh + ((Σg)² − Σg²)/2`. Activate positions in decreasing value order and merge runs with a DSU, keeping `Σh`, `Σg` and `Σg²` up to date.

**Steps.**
1. Sort the indices by value, descending.
2. For each distinct value: activate its positions, merging with active neighbours (remove the old run terms, add the merged one).
3. Add `(v − next lower value)·F`.

```python
import sys

MOD = 10 ** 9 + 7


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    a = [int(x) for x in data[1:1 + n]]
    order = sorted(range(n), key=lambda i: -a[i])
    parent = list(range(n))
    length = [0] * n
    active = [False] * n

    def find(x):
        root = x
        while parent[root] != root:
            root = parent[root]
        while parent[x] != root:
            parent[x], x = root, parent[x]
        return root

    def g(L):                                   # subarrays inside a run
        return L * (L + 1) // 2

    def h(L):                                   # ordered disjoint pairs inside a run = C(L+2, 4)
        return (L + 2) * (L + 1) * L * (L - 1) // 24

    sum_h = sum_g = sum_g2 = 0
    ans = 0
    k = 0
    while k < n:
        v = a[order[k]]
        while k < n and a[order[k]] == v:
            i = order[k]
            k += 1
            active[i] = True
            length[i] = 1
            sum_g += 1
            sum_g2 += 1
            for j in (i - 1, i + 1):
                if 0 <= j < n and active[j]:
                    ri, rj = find(i), find(j)
                    for r in (ri, rj):
                        L = length[r]
                        sum_h -= h(L); sum_g -= g(L); sum_g2 -= g(L) ** 2
                    parent[rj] = ri
                    length[ri] += length[rj]
                    L = length[ri]
                    sum_h += h(L); sum_g += g(L); sum_g2 += g(L) ** 2
        F = sum_h + (sum_g * sum_g - sum_g2) // 2
        nxt = a[order[k]] if k < n else 0
        ans += (v - nxt) * F
    print(ans % MOD)


main()
```

**Watch out.**
- `a ≤ b < c ≤ d` means the first subarray ends strictly before the second starts. Inside one run of length `L` that gives `C(L+2, 4)` pairs.
- A new single position adds `g = 1` and `h = 0` before any merges.
- Python's big ints make the exact sum easy; only the final answer is reduced.

```stdin
3
3 2 1
```

```stdout
6
```

### White Falcon And Tree

**Problem.** Every node holds a linear function. `1 u v a b` assigns `ax + b` to all nodes on the path. `2 u v x` applies the path's functions in order from `u` to `v`, starting from `x`. Work mod `10⁹+7`.

**Idea.** Use **heavy-light decomposition** with a segment tree over chain positions. Each node stores two compositions:
- **forward**: apply the positions in increasing order;
- **backward**: apply them in decreasing order.

The path climbs from `u` (decreasing positions, so use the backward compositions) and then descends to `v` (increasing positions, so use the forward ones). An assignment makes a node of length `2^j` equal to `f` composed with itself `2^j` times. Precompute that table once per update and use **the table itself as the lazy tag**, so pushing a tag costs no exponentiation.

**Steps.**
1. Build the HLD and a power-of-two segment tree. Composition rules: forward `(a, b) = (aR·aL, aR·bL + bR)`, backward is the mirror.
2. Assign: push along the two boundary paths, tag the covering nodes, and rebuild upward (skipping tagged nodes).
3. Query: collect the `u`-side ranges (apply each range's nodes in reverse with the backward compositions), then the `v`-side ranges in top-down order (forward compositions).

```python
import sys

MOD = 10 ** 9 + 7


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    fa0 = [int(x) for x in data[1:1 + 2 * n:2]]
    fb0 = [int(x) for x in data[2:2 + 2 * n:2]]
    p = 1 + 2 * n
    adj = [[] for _ in range(n)]
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
    S = 1
    while S < n:
        S *= 2
    FA = [1] * (2 * S); FB = [0] * (2 * S)       # forward composition
    GA = [1] * (2 * S); GB = [0] * (2 * S)       # backward composition
    LZ = [None] * (2 * S)                       # lazy: pw[j] = f composed 2^j times
    LV = [0] * (2 * S)                          # log2 of node length
    for i in range(S - 1, 0, -1):
        LV[i] = LV[2 * i] + 1
    for u in range(n):
        i = S + pos[u]
        FA[i] = GA[i] = fa0[u]
        FB[i] = GB[i] = fb0[u]

    def pull(i):
        l, r = 2 * i, 2 * i + 1
        FA[i] = FA[r] * FA[l] % MOD
        FB[i] = (FA[r] * FB[l] + FB[r]) % MOD
        GA[i] = GA[l] * GA[r] % MOD
        GB[i] = (GA[l] * GB[r] + GB[l]) % MOD

    for i in range(S - 1, 0, -1):
        pull(i)
    H = LV[1]

    def powers(a, b):
        pw = [(a, b)]
        for _ in range(H):
            a, b = a * a % MOD, (a * b + b) % MOD
            pw.append((a, b))
        return pw

    def put(i, pw):
        pa, pb = pw[LV[i]]
        FA[i] = GA[i] = pa
        FB[i] = GB[i] = pb
        if i < S:
            LZ[i] = pw

    def push_path(leaf):
        for s in range(H, 0, -1):
            i = leaf >> s
            pw = LZ[i]
            if pw is not None:
                put(2 * i, pw)
                put(2 * i + 1, pw)
                LZ[i] = None

    def assign(l, r, pw):                       # positions [l, r)
        l += S
        r += S
        l0, r0 = l, r - 1
        push_path(l0)
        push_path(r0)
        while l < r:
            if l & 1:
                put(l, pw)
                l += 1
            if r & 1:
                r -= 1
                put(r, pw)
            l >>= 1
            r >>= 1
        for leaf in (l0, r0):
            i = leaf >> 1
            while i:
                if LZ[i] is None:
                    pull(i)
                i >>= 1

    def collect(l, r):                          # covering nodes of [l, r), increasing
        l += S
        r += S
        push_path(l)
        push_path(r - 1)
        left, right = [], []
        while l < r:
            if l & 1:
                left.append(l)
                l += 1
            if r & 1:
                r -= 1
                right.append(r)
            l >>= 1
            r >>= 1
        return left + right[::-1]

    out = []
    q = int(data[p]); p += 1
    for _ in range(q):
        if data[p] == b'1':
            u = int(data[p + 1]) - 1; v = int(data[p + 2]) - 1
            pw = powers(int(data[p + 3]), int(data[p + 4])); p += 5
            while head[u] != head[v]:
                if depth[head[u]] < depth[head[v]]:
                    u, v = v, u
                assign(pos[head[u]], pos[u] + 1, pw)
                u = parent[head[u]]
            lo, hi = sorted((pos[u], pos[v]))
            assign(lo, hi + 1, pw)
        else:
            u = int(data[p + 1]) - 1; v = int(data[p + 2]) - 1; x = int(data[p + 3]); p += 4
            up_ranges, down_ranges = [], []
            while head[u] != head[v]:
                if depth[head[u]] >= depth[head[v]]:
                    up_ranges.append((pos[head[u]], pos[u] + 1))
                    u = parent[head[u]]
                else:
                    down_ranges.append((pos[head[v]], pos[v] + 1))
                    v = parent[head[v]]
            if pos[u] >= pos[v]:
                up_ranges.append((pos[v], pos[u] + 1))
            else:
                down_ranges.append((pos[u], pos[v] + 1))
            for l, r in up_ranges:
                for i in reversed(collect(l, r)):
                    x = (GA[i] * x + GB[i]) % MOD
            for l, r in reversed(down_ranges):
                for i in collect(l, r):
                    x = (FA[i] * x + FB[i]) % MOD
            out.append(x)
    sys.stdout.write('\n'.join(map(str, out)) + ('\n' if out else ''))


main()
```

**Watch out.**
- Function composition is not commutative. Forward combines as "left, then right"; backward as "right, then left".
- A node holding a lazy tag must not be rebuilt from its (stale) children, hence the `LZ[i] is None` check.
- About 1.2 s on a path and 5 s on a perfect binary tree (many short chains), for `N = Q = 5·10⁴`.

```stdin
2
1 1
1 2
1 2
2
1 2 2 1 1
2 1 2 1
```

```stdout
3
```

### Subtrees And Paths

**Problem.** In a tree rooted at 1 with values that start at 0: `add t value` adds `value` to the whole subtree of `t`, and `max a b` prints the maximum value on the path `a–b`.

**Idea.** Run the **heavy-light DFS that visits the heavy child first**. Then every subtree is a contiguous range **and** every heavy chain is a contiguous range. A subtree add becomes one range add, and a path max becomes `O(log n)` range maxima. Both run on numpy blocks with a lazy add per block.

**Steps.**
1. BFS for parents, sizes and heavy children. Iterative DFS pushing the light children first and the heavy child last, so the heavy child is popped next.
2. `add`: range add on `[pos, pos + size)`.
3. `max`: walk the chains, taking range maxima.

```python
import sys

import numpy as np


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    adj = [[] for _ in range(n)]
    p = 1
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
    while st:                                   # heavy child popped right after its parent
        u = st.pop()
        pos[u] = cur
        cur += 1
        for v in adj[u]:
            if v != parent[u] and v != heavy[u]:
                head[v] = v
                st.append(v)
        if heavy[u] != -1:
            head[heavy[u]] = head[u]
            st.append(heavy[u])
    B = max(64, int(n ** 0.5))
    nb = (n + B - 1) // B
    raw = np.zeros((nb, B), dtype=np.int64)
    raw.reshape(-1)[n:] = -(1 << 60)            # padding never wins
    lazy = np.zeros(nb, dtype=np.int64)
    bmax = raw.max(axis=1)

    def add(l, r, v):                           # [l, r)
        bl, br = l // B, (r - 1) // B
        if bl == br:
            raw[bl, l - bl * B:r - bl * B] += v
            bmax[bl] = raw[bl].max()
            return
        raw[bl, l - bl * B:] += v
        bmax[bl] = raw[bl].max()
        raw[br, :r - br * B] += v
        bmax[br] = raw[br].max()
        if br > bl + 1:
            lazy[bl + 1:br] += v

    def rmax(l, r):                             # [l, r)
        bl, br = l // B, (r - 1) // B
        if bl == br:
            return int(raw[bl, l - bl * B:r - bl * B].max() + lazy[bl])
        res = max(int(raw[bl, l - bl * B:].max() + lazy[bl]), int(raw[br, :r - br * B].max() + lazy[br]))
        if br > bl + 1:
            res = max(res, int((bmax[bl + 1:br] + lazy[bl + 1:br]).max()))
        return res

    q = int(data[p]); p += 1
    out = []
    for _ in range(q):
        op = data[p]; x = int(data[p + 1]); y = int(data[p + 2]); p += 3
        if op == b'add':
            u = x - 1
            add(pos[u], pos[u] + size[u], y)
        else:
            u, v = x - 1, y - 1
            res = -(1 << 62)
            while head[u] != head[v]:
                if depth[head[u]] < depth[head[v]]:
                    u, v = v, u
                res = max(res, rmax(pos[head[u]], pos[u] + 1))
                u = parent[head[u]]
            a, b = sorted((pos[u], pos[v]))
            out.append(max(res, rmax(a, b + 1)))
    sys.stdout.write('\n'.join(map(str, out)) + ('\n' if out else ''))


main()
```

**Watch out.**
- The plain "walk the chain, push light children" layout keeps chains contiguous but **not** subtrees. The heavy-first DFS order is required.
- Values can be negative, so the path max starts from a very small number rather than 0.

```stdin
5
1 2
2 3
2 4
5 1
6
add 4 30
add 5 20
max 4 5
add 2 -20
max 4 5
max 3 4
```

```stdout
30
20
10
```
