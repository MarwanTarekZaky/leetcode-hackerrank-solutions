## Dynamic Programming

### Tree Pruning

**Problem.** A tree is rooted at vertex 1 and its vertices have weights. Remove at most `k` whole subtrees so that the total weight of the vertices left is as large as possible.

**Idea.** In a preorder listing, every subtree is a contiguous block `[i, i + size_i)`. Walk the listing backwards. `f[i][j]` is the best weight of the vertices from position `i` on when `j` removals are allowed. At vertex `i` there are two choices:
- **keep it:** `w_i + f[i+1][j]`;
- **cut its subtree:** jump past the whole block, giving `f[i + size_i][j−1]`.

Each row is one NumPy vector of length `k+1`.

**Steps.**
1. Root the tree with a BFS and compute the subtree sizes.
2. Build the preorder with the **heaviest child visited last**.
3. Fill the rows from `i = n−1` down to `0`, starting from `f[n] = 0`. Keep a row only while some later vertex still jumps to it. The answer is `f[0][k]`.

```python
import sys

import numpy as np


def main():
    data = sys.stdin.buffer.read().split()
    n, k = int(data[0]), int(data[1])
    w = list(map(int, data[2:2 + n]))
    adj = [[] for _ in range(n)]
    pos = 2 + n
    for _ in range(n - 1):
        u, v = int(data[pos]) - 1, int(data[pos + 1]) - 1
        pos += 2
        adj[u].append(v)
        adj[v].append(u)
    parent = [-1] * n
    order = [0]
    seen = [False] * n
    seen[0] = True
    for x in order:
        for y in adj[x]:
            if not seen[y]:
                seen[y] = True
                parent[y] = x
                order.append(y)
    size = [1] * n
    for x in reversed(order[1:]):
        size[parent[x]] += size[x]
    children = [[] for _ in range(n)]
    for x in order[1:]:
        children[parent[x]].append(x)
    pre = []
    stack = [0]
    while stack:
        x = stack.pop()
        pre.append(x)
        # push the heaviest child first so that it is visited last
        stack.extend(sorted(children[x], key=lambda c: -size[c]))
    ends = [i + size[pre[i]] for i in range(n)]
    refs = {}
    for e in ends:
        refs[e] = refs.get(e, 0) + 1
    rows = {n: np.zeros(k + 1, dtype=np.int64)}
    nxt = rows[n]
    for i in range(n - 1, -1, -1):
        e = ends[i]
        cur = nxt + w[pre[i]]                         # keep vertex i
        cur[1:] = np.maximum(cur[1:], rows[e][:-1])   # or cut its subtree
        refs[e] -= 1
        if refs[e] == 0:
            del rows[e]
        if refs.get(i, 0):
            rows[i] = cur
        nxt = cur
    print(int(nxt[k]))


main()
```

**Watch out.** Visiting the heaviest child last keeps memory small. The positions that the vertices still to be processed will jump to are ends of ancestor blocks. With heavy-last order, ancestors joined by heavy edges share the same end, so only O(log n) rows are alive at once. Otherwise a deep tree could keep `n` rows of length 201 alive. `f[i][j]` already means "at most `j` removals", because `f[n][j] = 0` for every `j`.

```stdin
5 2
1 1 -1 -1 -1
1 2
2 3
4 1
4 5
```

```stdout
2
```

### Ones and Twos

**Problem.** Use at most `A` ones and at most `B` twos in an expression with `+` and `*`. How many different values can it have? Answer modulo 10⁹+7.

**Idea.** A term is a product, so its value is `2^j` (a lone `1` is `2^0`); extra ones inside a product change nothing. So a value is `c + S`, where:
- `c ≤ A` is the number of `+1` terms;
- `S` is a sum of powers `2^j` with `j ≥ 1` and `Σ j ≤ B`.

Two equal powers `2^j + 2^j` cost `2j` twos, but `2^{j+1}` costs only `j+1`. So the cheapest way to make `S` is its binary expansion. The values are therefore exactly `c + S` with:
- `S` even and the sum of its set-bit positions ("cost") `≤ B`;
- `0 ≤ c ≤ A`;
- not both zero.

Count these distinct values without listing them.
- **Blocks.** Let `L = bit_length(A) + 1` (at least 2), so a block of width `2^L` is longer than `A + 1`. Split `S` into a *high* part (bits `≥ L`) and a *low* part (bits `1..L−1`).
- **Within one block.** For a fixed high part, the values form the union of the intervals `[low, low + A]`. A DP over the low bits, from small to large, tracks `U[b]` (size of the union for low cost `≤ b`) and `MX[b]` (its largest low sum). Adding bit `p` puts a shifted copy at `2^p`. The two copies overlap by `max(0, MX + A + 1 − 2^p)`.
- **Across blocks.** The number of high parts with cost exactly `c` is the number of sets of distinct integers `≥ L` summing to `c`, which is a small knapsack. The union of a block can spill past `2^L` into the next block, `H + 2^L`. Suppose `H` has `t` trailing set bits starting at `L`. Then `H + 2^L` clears them and sets bit `L + t`. Their costs are `tL + t(t−1)/2` and `L + t`, plus a shared rest made of distinct parts `≥ L + t + 1`. The spill is subtracted once for every such pair.

The formula was checked against a brute force for every `A ≤ 200`, `B ≤ 11`.

**Steps.**
1. Low DP over bits `1..L−1` gives `U[b]` and `MX[b]` for every budget `b`.
2. `total = Σ_c parts_{≥L}[c] · U[B − c]`.
3. For each `t ≥ 0` with `tL + t(t−1)/2 ≤ B`, subtract `parts_{≥L+t+1}[c] · max(0, MX[B − c − trail] + A + 1 − 2^L)`, counted only when the neighbour also fits (`c + L + t ≤ B`).
4. Subtract 1 for the value 0.

```python
import sys

import numpy as np

MOD = 10 ** 9 + 7


def ones_twos(A, B):
    L = max(1, A.bit_length()) + 1                 # block width 2^L > A + 1
    span = 1 << L
    U = [A + 1] * (B + 1)                          # low sums with bits 1..p-1
    MX = [0] * (B + 1)
    for bit in range(1, L):
        nu, nm = U[:], MX[:]
        for b in range(bit, B + 1):
            overlap = max(0, MX[b] + A + 1 - (1 << bit))
            nu[b] = U[b] + U[b - bit] - overlap
            nm[b] = (1 << bit) + MX[b - bit]
        U, MX = nu, nm

    def distinct_parts(min_part):
        dp = np.zeros(B + 1, dtype=object)
        dp[0] = 1
        for part in range(min_part, B + 1):
            dp[part:] = dp[part:] + dp[:B + 1 - part].copy()
        return dp

    high = distinct_parts(L)
    total = 0
    for c in range(B + 1):
        if high[c]:
            total += high[c] * U[B - c]
    t = 0
    while t * L + t * (t - 1) // 2 <= B:
        trail = t * L + t * (t - 1) // 2
        rest = distinct_parts(L + t + 1)
        for c in range(B + 1):
            if rest[c] and c + trail <= B and c + L + t <= B:
                spill = max(0, MX[B - c - trail] + A + 1 - span)
                total -= rest[c] * spill
        t += 1
    return (total - 1) % MOD


def main():
    data = sys.stdin.read().split()
    t = int(data[0])
    out = [ones_twos(int(data[1 + 2 * i]), int(data[2 + 2 * i])) for i in range(t)]
    print('\n'.join(map(str, out)))


main()
```

**Watch out.** Counting expressions instead of values is far too many; removing duplicates is the whole problem. Because `2^L > A + 1`, a block can only overlap the very next high part, never one further away. `A = B = 0` gives 0. The high-part counts are exact integers (object arrays); only the final total is reduced modulo 10⁹+7.

```stdin
4
0 0
2 2
0 2
2 0
```

```stdout
0
6
2
2
```

### Count Scorecards

**Problem.** In a round-robin tournament with `n` players, some final scores are erased (`−1`). How many score sequences are possible? Answer modulo 10⁹+7.

**Idea.** **Landau's theorem:** a sorted sequence `s_1 ≤ … ≤ s_n` is a tournament score sequence exactly when every prefix of `k` players has sum `≥ C(k, 2)`, and the total is `C(n, 2)`.

The erased players are distinguishable positions, so count the ways to give each one a value. Process the values `v = 0, 1, …, n−1` in increasing order. State `(k, S)` means `k` players placed so far, with score sum `S`.
- **Who gets value `v`.** All the known players with value `v`, plus `x` erased players. There are `C(free, x)` ways to choose which erased players.
- **Landau check.** After each newly placed player, check `S ≥ C(k, 2)`. The players with equal value are consecutive in sorted order, so every prefix gets checked.
- **Prune.** The players still to come score at most `n−1` each, so drop sums that can no longer reach `C(n, 2)`.

With `S` as a NumPy axis, each `(v, k, x)` triple moves a slice of the array.

**Steps.**
1. Count the known players per value and the number of erased players.
2. Run the DP above. The answer is `dp[n][C(n, 2)]`.

```python
import sys
from math import comb

import numpy as np

MOD = 10 ** 9 + 7


def count_scorecards(s):
    n = len(s)
    known = [0] * n
    erased = 0
    for v in s:
        if v == -1:
            erased += 1
        else:
            known[v] += 1
    full = n * (n - 1) // 2
    binom = [[comb(a, b) % MOD for b in range(n + 1)] for a in range(n + 1)]
    dp = np.zeros((n + 1, full + 1), dtype=np.int64)       # dp[k][sum]
    dp[0][0] = 1
    known_before = 0
    for v in range(n):
        new = np.zeros_like(dp)
        for k in range(n + 1):
            row = dp[k]
            if not row.any():
                continue
            free = erased - (k - known_before)              # erased players not placed yet
            if free < 0:
                continue
            need = 0                                         # smallest allowed old sum
            for m in range(1, known[v] + 1):
                need = max(need, (k + m) * (k + m - 1) // 2 - m * v)
            for x in range(free + 1):
                m = known[v] + x
                if k + m > n:
                    break
                if m:
                    need = max(need, (k + m) * (k + m - 1) // 2 - m * v)
                lo = max(need, full - (n - k - m) * (n - 1) - m * v)
                hi = full - m * v
                if lo > hi:
                    continue
                tgt = new[k + m, lo + m * v:hi + m * v + 1]
                tgt += row[lo:hi + 1] * binom[free][x] % MOD
                tgt %= MOD
        dp = new
        known_before += known[v]
    return int(dp[n][full])


def main():
    data = sys.stdin.read().split()
    t = int(data[0])
    pos = 1
    out = []
    for _ in range(t):
        n = int(data[pos])
        out.append(count_scorecards(list(map(int, data[pos + 1:pos + 1 + n]))))
        pos += 1 + n
    print('\n'.join(map(str, out)))


main()
```

**Watch out.** Counting sorted sequences would be wrong: two erased players with values 0 and 1 give two different scorecards, which is what `C(free, x)` accounts for. A known score sequence that breaks Landau's condition, such as `1 1`, gives 0. The products stay below 2⁶³ because both factors are reduced modulo 10⁹+7 first.

```stdin
5
3
-1 -1 2
3
-1 -1 -1
4
0 1 2 3
2
1 1
4
-1 -1 -1 2
```

```stdout
2
7
1
0
12
```

### Vim War

**Problem.** Each of `N` soldiers has a set of `M ≤ 20` skills. Count the non-empty groups of soldiers whose combined skills are **exactly** the required set `R`. Answer modulo 10⁹+7.

**Idea.** A soldier with any skill outside `R` can never be used, so drop them. Then only the bits of `R` matter; relabel them `0..r−1`.
- **Groups inside a set.** `f(T)` = number of soldiers whose skills are a subset of `T`. That is a subset-sum (zeta) transform, computed with NumPy one bit at a time. Groups whose union is inside `T`: `2^{f(T)}`, including the empty group.
- **Exactly `R`.** Inclusion–exclusion: `Σ_{T ⊆ R} (−1)^{|R∖T|} 2^{f(T)}`.

**Steps.**
1. Map each usable soldier to a mask over the bits of `R`, and count the masks.
2. Zeta transform; raise 2 to each count; sum with signs.
3. If `R` is empty, subtract the empty group.

```python
import sys

import numpy as np

MOD = 10 ** 9 + 7


def main():
    data = sys.stdin.read().split()
    n, m = int(data[0]), int(data[1])
    skills = data[2:2 + n]
    req = data[2 + n]
    R = int(req, 2)
    bits = [m - 1 - i for i in range(m) if req[i] == '1']     # bit positions of R
    r = len(bits)
    cnt = np.zeros(1 << r, dtype=np.int64)
    for s in skills:
        x = int(s, 2)
        if x & ~R:
            continue                                         # has a skill nobody wants
        mask = 0
        for t, b in enumerate(bits):
            if x >> b & 1:
                mask |= 1 << t
        cnt[mask] += 1
    for t in range(r):                                       # subset sums
        v = cnt.reshape(-1, 2, 1 << t)
        v[:, 1, :] += v[:, 0, :]
    pw = np.ones(n + 1, dtype=np.int64)
    for i in range(1, n + 1):
        pw[i] = pw[i - 1] * 2 % MOD
    pop = np.zeros(1 << r, dtype=np.int64)
    for t in range(r):
        pop[1 << t:2 << t] = pop[:1 << t] + 1
    sign = np.where((r - pop) % 2 == 0, 1, -1)
    ans = int((pw[cnt] * sign).sum() % MOD)
    if R == 0:
        ans = (ans - 1) % MOD
    print(ans)


main()
```

**Watch out.** The sample lines carry trailing spaces, so read whitespace-separated tokens. `r` can be 20, so the arrays have about a million entries, which NumPy handles easily. The signed sum stays far below 2⁶³ before the final modulo.

```stdin
4 2
00
10
01
11
11
```

```stdout
10
```

### Best spot

**Problem.** Slide an `H×W` "perfect store" over an `R×C` height grid and minimise the sum of squared differences. Print the minimum and the 1-based top-left corner, preferring the smallest row, then the smallest column.

**Idea.** Expand the square: `Σ (land − store)² = Σ land² + Σ store² − 2·Σ land·store`.
- **`Σ land²`** over every window comes from a 2-D prefix sum.
- **`Σ store²`** is a constant.
- **The cross term** is a 2-D correlation, computed for all positions at once with an FFT (multiply by the flipped store). Heights are at most 20 in absolute value, so the sums stay below about 10⁸. Floating-point FFT rounds them back exactly.

**Steps.**
1. Correlate with `rfft2` and read the window results.
2. Add the window sums of squares and the constant.
3. `argmin` on the row-major array gives the tie-break for free.

```python
import sys

import numpy as np


def main():
    data = sys.stdin.read().split()
    R, C = int(data[0]), int(data[1])
    land = np.array(data[2:2 + R * C], dtype=np.int64).reshape(R, C)
    pos = 2 + R * C
    H, W = int(data[pos]), int(data[pos + 1])
    store = np.array(data[pos + 2:pos + 2 + H * W], dtype=np.int64).reshape(H, W)
    shape = (R + H, C + W)
    conv = np.fft.irfft2(np.fft.rfft2(land.astype(float), shape) *
                         np.fft.rfft2(store[::-1, ::-1].astype(float), shape), shape)
    corr = np.rint(conv[H - 1:R, W - 1:C]).astype(np.int64)   # window with top-left (i, j)
    sq = np.zeros((R + 1, C + 1), dtype=np.int64)
    sq[1:, 1:] = (land ** 2).cumsum(0).cumsum(1)
    win = sq[H:, W:] - sq[:-H, W:] - sq[H:, :-W] + sq[:-H, :-W]
    cost = win + int((store ** 2).sum()) - 2 * corr
    i, j = divmod(int(np.argmin(cost)), cost.shape[1])
    print(int(cost[i, j]))
    print(i + 1, j + 1)


main()
```

**Watch out.** The convolution of the flipped store puts the window with top-left `(i, j)` at index `(i + H − 1, j + W − 1)`. Padding to `(R+H)×(C+W)` avoids wrap-around. The answer is printed on two lines.

```stdin
3 3
19 19 -12
5 8 -14
-12 -11 9
2 2
-18 -12
-10 -7
```

```stdout
937
2 2
```

### Divisible Numbers

**Problem.** Find the length of the smallest multiple `m` of `n` (with `n ≤ 3·10⁴` and not divisible by 10) such that `m` has no zero digit and its digit sum is at least its digit product.

**Idea.** The smallest such multiple is the one with the fewest digits, so search length by length.
- **The key quantity.** Let `P` be the digit product and `S' = Σ(d − 1)`. A number of length `ℓ` has digit sum `ℓ + S'`, so it qualifies when `Δ = P − S' ≤ ℓ`.
- **`Δ` never decreases.** Appending a digit `d` gives `Δ' = Δ + (P − 1)(d − 1)`. So any state with `Δ` above a limit can be thrown away for good.
- **DP.** The state is `(remainder, P)` and the value is the smallest `Δ`. Only products whose best possible `Δ` fits the limit get a row. Double the limit until an answer appears.
- **Splitting off the 2s or 5s.** Write `n = n₂·n₁`, where `n₂ = 2^a` or `5^b` and `n₁` is coprime to 10. Divisibility by `n₂` depends only on the last `t = a` or `b` digits.
  - Run the DP modulo `n` for the first `t` digits. This finds short answers and also yields the table of valid `t`-digit suffixes.
  - Longer numbers are prefix + suffix. The prefix DP runs **modulo `n₁` only**, and digit appends are permutations there, so each step is a cheap gather.
  - At each prefix length, combine with the suffix table: the total `Δ` is `(P_p − 1)(P_s − 1) − 1 + Δ_p + Δ_s`.
- **Why it matters.** `n = 15625 = 5⁶` needs 465 digits, but there `n₁ = 1`, so each layer is tiny.

**Steps.**
1. Factor out `n₂` and set `t`.
2. Run the full DP for `t` layers (answers of length `≤ t`), then filter the remainders `≡ 0 (mod n₂)` into the suffix table, keyed by remainder mod `n₁`.
3. Run the prefix DP mod `n₁`; after each layer, check every suffix row. Double the `Δ` limit if nothing is found.

```python
import sys

import numpy as np

INF = 1 << 29


def smax_table(cap):
    smax = {1: 0}                    # best sum(d - 1) over digit factorisations of P
    for P in range(2, cap + 1):
        best = -1
        for d in range(2, 10):
            if P % d == 0 and P // d in smax:
                best = max(best, smax[P // d] + d - 1)
        if best >= 0:
            smax[P] = best
    return smax


def make_gather(mod):
    rems = np.arange(mod)
    out = {}
    for d in range(1, 10):
        rm = (10 * rems + d) % mod
        if len(np.unique(rm)) == mod:
            inv = np.empty(mod, dtype=np.int64)
            inv[rm] = rems
            out[d] = ('perm', inv)
        else:
            order = np.argsort(rm, kind='stable')
            srt = rm[order]
            starts = np.flatnonzero(np.r_[True, srt[1:] != srt[:-1]])
            out[d] = ('red', (order, starts, srt[starts]))
    return out


def step(best, prods, row_of, mod, limit, gather):
    new = np.full((len(prods), mod), INF, dtype=np.int64)
    for d in range(1, 10):
        src, tgt, add = [], [], []
        for i, P in enumerate(prods):
            j = row_of.get(P * d)
            if j is not None:
                src.append(i)
                tgt.append(j)
                add.append((P - 1) * (d - 1))
        if not src:
            continue
        tgt = np.array(tgt)
        vals = best[np.array(src)] + np.array(add)[:, None]
        kind, g = gather[d]
        if kind == 'perm':
            new[tgt] = np.minimum(new[tgt], vals[:, g])
        else:
            order, starts, targets = g
            red = np.minimum.reduceat(vals[:, order], starts, axis=1)
            new[np.ix_(tgt, targets)] = np.minimum(new[np.ix_(tgt, targets)], red)
    new[new > limit] = INF
    return new


def first_layer(prods, row_of, mod):
    best = np.full((len(prods), mod), INF, dtype=np.int64)
    for d in range(1, 10):
        if d in row_of:
            best[row_of[d], d % mod] = 1
    return best


def solve(n, limit):
    n2, t, n1 = 1, 0, n
    while n1 % 2 == 0:
        n1, n2, t = n1 // 2, n2 * 2, t + 1
    while n1 % 5 == 0:
        n1, n2, t = n1 // 5, n2 * 5, t + 1
    smax = smax_table(2 * limit + 100)
    prods = [P for P in sorted(smax) if P - smax[P] <= limit]
    row_of = {P: i for i, P in enumerate(prods)}
    P_arr = np.array(prods, dtype=np.int64)
    suf = np.full((len(prods), n1), INF, dtype=np.int64)
    if t:
        g = make_gather(n)
        best = first_layer(prods, row_of, n)
        for L in range(1, t + 1):
            if L > 1:
                best = step(best, prods, row_of, n, limit, g)
            if (best[:, 0] <= L).any():
                return L
        for r in range(0, n, n2):                       # suffixes divisible by n2
            np.minimum(suf[:, r % n1], best[:, r], out=suf[:, r % n1])
    else:
        suf[0, 0] = 1                                    # empty suffix: P = 1, delta = 1
    need = (-np.arange(n1) * pow(10, t, n1)) % n1
    suffixes = [(prods[i], suf[i][need]) for i in range(len(prods)) if (suf[i] < INF).any()]
    g = make_gather(n1)
    best = first_layer(prods, row_of, n1)
    lp = 1
    while lp + t <= limit:
        if lp > 1:
            best = step(best, prods, row_of, n1, limit, g)
        for Ps, col in suffixes:
            tot = (best + col[None, :]).min(axis=1) + (P_arr - 1) * (Ps - 1) - 1
            if (tot <= lp + t).any():
                return lp + t
        lp += 1
    return None


def main():
    n = int(sys.stdin.read().split()[0])
    limit = 16
    while True:
        ans = solve(n, limit)
        if ans is not None:
            print(ans)
            return
        limit *= 2


main()
```

**Watch out.** Searching multiples of `n` one by one never finishes: `5⁶` needs a 465-digit answer. Storing the *minimum `Δ`* per `(remainder, P)` is safe, because `P` fixes how future digits change `Δ`, so a smaller `Δ` dominates. If a solution of length `≤ limit` exists, every `Δ` along its path is `≤ limit`, so the pruning never loses it.

```stdin
1
```

```stdout
1
```

### Unique Divide And Conquer

**Problem.** Count the labelled trees on `n` vertices in which centroid decomposition has a **unique** centroid at every step. Answer modulo a prime `m > n`.

**Idea.** A tree has two centroids exactly when some edge splits it into two halves of size `n/2`. So the centroid is unique when every component left after removing it has size `≤ lim = ⌊(n−1)/2⌋`, and each component must be good recursively.
- **Rooted good trees.** `w(s) = s·f(s)`: a good tree of size `s` plus the vertex that touches the centroid.
- **Forests.** `H(k)` counts forests of rooted good trees on `k` labelled vertices, with no size limit. Take the component containing the smallest label: `H(k) = Σ_s C(k−1, s−1)·w(s)·H(k−s)`.
- **The size limit.** At most one component can exceed `lim`, so subtract those forests directly:

  `f(n) = n · ( H(n−1) − Σ_{s>lim} C(n−1, s)·w(s)·H(n−1−s) )`

  The factor `n` chooses the centroid.

Check: `f(1..4) = 1, 0, 3, 4`. A brute force over all labelled trees also matches for `n ≤ 7` (e.g. `f(7) = 6937`).

**Steps.**
1. Factorials and inverse factorials modulo `m` (prime and `> n`, so they exist).
2. For `k = 1..n`: compute `f(k)` and `w(k)`, then `H(k)`. The `H` sum is a convolution; write it as a dot product of `w(s)/(s−1)!` and `H(j)/j!`.
3. Split one factor into 15-bit halves so the NumPy dot products cannot overflow.

```python
import sys

import numpy as np


def unique_dc(n, p):
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = fact[i - 1] * i % p
    inv = [pow(x, p - 2, p) for x in fact]
    w = [0] * (n + 1)
    f = [0] * (n + 1)
    H = [1] + [0] * n
    a = np.zeros(n + 1, dtype=np.int64)          # a[s] = w(s) / (s-1)!
    b = np.zeros(n + 1, dtype=np.int64)          # b[j] = H(j) / j!
    b[0] = 1

    def dot(x, y):
        lo, hi = y & 32767, y >> 15
        return (int(np.dot(x, lo) % p) + (int(np.dot(x, hi) % p) << 15)) % p

    for k in range(1, n + 1):
        lim = (k - 1) // 2
        bad = 0
        for s in range(lim + 1, k):
            bad += fact[k - 1] * inv[s] % p * inv[k - 1 - s] % p * w[s] % p * H[k - 1 - s]
        f[k] = k * (H[k - 1] - bad) % p
        w[k] = k * f[k] % p
        a[k] = w[k] * inv[k - 1] % p
        H[k] = fact[k - 1] * dot(a[1:k + 1], b[k - 1::-1][:k]) % p
        b[k] = H[k] * inv[k] % p
    return f[n]


n, m = map(int, sys.stdin.read().split()[:2])
print(unique_dc(n, m))
```

**Watch out.** `n = 2` gives 0: both vertices are centroids. The modulus changes per test, so nothing can be precomputed. The `H` recurrence picks the component of the smallest label, which avoids counting the same forest in several orders.

```stdin
1 103
```

```stdout
1
```

### King and Four Sons

**Problem.** Choose a subsequence of `K` battalions, and from the `j`-th chosen battalion a squad whose size is a multiple of 4 (size 0 allowed). Count the ways modulo 10⁹+7.

**Idea.** For one battalion of size `A`, the number of subsets with size `≡ 0 (mod 4)` uses the roots of unity filter:

`w(A) = (2^A + (1+i)^A + 0^A + (1−i)^A) / 4`

- **No complex numbers needed.** `(1+i)² = 2i`, so `(1+i)^A + (1−i)^A = 2·Re((1+i)^A)`. With `q = ⌊A/2⌋`, `Re((1+i)^A) = 2^q·s`, where `s` comes from `[1, 0, −1, 0][q mod 4]` for even `A` and `[1, −1, −1, 1][q mod 4]` for odd `A`.
- **Choosing `K` battalions.** The answer is the elementary symmetric polynomial `e_K(w_1, …, w_N)`, built with one NumPy step per battalion.

**Steps.**
1. Compute `w(A_i)` with modular powers.
2. `dp[j] += dp[j−1]·w` for `j = 1..K`, all at once, battalion by battalion. Print `dp[K]`.

```python
import sys

import numpy as np

MOD = 10 ** 9 + 7


def main():
    data = sys.stdin.read().split()
    n, k = int(data[0]), int(data[1])
    inv4 = pow(4, MOD - 2, MOD)
    dp = np.zeros(k + 1, dtype=np.int64)
    dp[0] = 1
    for A in map(int, data[2:2 + n]):
        q = A // 2
        s = [1, 0, -1, 0][q % 4] if A % 2 == 0 else [1, -1, -1, 1][q % 4]
        w = (pow(2, A, MOD) + 2 * s * pow(2, q, MOD)) * inv4 % MOD
        dp[1:] = (dp[1:] + dp[:-1] * w) % MOD
    print(int(dp[k]))


main()
```

**Watch out.** `dp[:-1]` on the right is read before the assignment, so every battalion is used at most once, as a 0/1 knapsack needs. Sample: `w(3) = 1`, `w(4) = 2`, `w(5) = 6`, and `1·2 + 1·6 + 2·6 = 20`.

```stdin
3 2
3 4 5
```

```stdout
20
```

### Dortmund Dilemma

**Problem.** Count the names of length `N` that use **exactly** `K` distinct lowercase letters and have a proper prefix equal to a proper suffix (a *border*). Up to 10⁵ queries, answer modulo 10⁹+9.

**Idea.**
- **Unbordered strings.** Over an alphabet of `j` letters, the count `u_j(n)` satisfies `u(1) = j`, `u(2m+1) = j·u(2m)` and `u(2m) = j·u(2m−1) − u(m)`. The reason: a shortest border is itself unbordered and at most half the length.
- **Bordered strings.** Over `j` letters (not all necessarily used): `B_j(n) = j^n − u_j(n)`.
- **Exactly `K` letters.** For a fixed set of `K` letters, inclusion–exclusion gives `Σ_{j=1..K} (−1)^{K−j}·C(K, j)·B_j(N)`. Multiply by `C(26, K)` for the choice of letters.

**Steps.**
1. Precompute `B_j(n)` for `j ≤ 26` and `n` up to the largest `N` asked.
2. Answer each query with the 26-term sum (cached per `(N, K)`).

```python
import sys
from math import comb

MOD = 10 ** 9 + 9


def main():
    data = sys.stdin.read().split()
    t = int(data[0])
    qs = [(int(data[1 + 2 * i]), int(data[2 + 2 * i])) for i in range(t)]
    maxn = max(n for n, _ in qs)
    bordered = [None] * 27
    for j in range(1, 27):
        u = [0] * (maxn + 1)
        row = [0] * (maxn + 1)
        pw = 1
        for n in range(1, maxn + 1):
            if n == 1:
                u[n] = j
            elif n % 2 == 0:
                u[n] = (j * u[n - 1] - u[n // 2]) % MOD
            else:
                u[n] = j * u[n - 1] % MOD
            pw = pw * j % MOD
            row[n] = (pw - u[n]) % MOD
        bordered[j] = row
    cache = {}
    out = []
    for n, k in qs:
        if (n, k) not in cache:
            tot = 0
            for j in range(1, k + 1):
                term = comb(k, j) * bordered[j][n]
                tot += term if (k - j) % 2 == 0 else -term
            cache[(n, k)] = tot % MOD * comb(26, k) % MOD
        out.append(cache[(n, k)])
    print('\n'.join(map(str, out)))


main()
```

**Watch out.** "Proper" excludes the whole word, so length 1 always gives 0. Here the modulus is 10⁹+**9**. The sample output lines have trailing spaces on HackerRank; the checker ignores them.

```stdin
3
1 1
2 1
4 2
```

```stdout
0
26
2600
```

### Super Kth LIS

**Problem.** Among all longest increasing subsequences (different index sets count separately), print the `K`-th in lexicographic order of values, or `-1` if there are fewer than `K`.

**Idea.**
- **Counts from the right.** Scan from the right with a Fenwick tree over values. For each index, find `len[i]` (the longest increasing run starting at `i`) and `cnt[i]` (how many such runs). Cap the counts at `K + 1`, since only "≥ K" matters.
- **Choosing the values.** Build the answer one value at a time. Positions with `len = L − t` form layer `t`.
- **Weights.** Every chosen prefix ends at a group of indices (all with the same value) with weights `ω` (ways to reach each). A candidate `j` in the next layer, with a larger value, gets weight `ω'_j = Σ ω_i over i < j`, which is a running sum while both lists are scanned in index order.
- **Picking the next value.** Group the candidates by value in increasing order. Each group covers `Σ ω'_j·cnt[j]` sequences. Skip whole groups while `K` exceeds them; the group where `K` lands is the next value.

Each index is examined only in its own layer, so the walk is linear after sorting.

**Steps.**
1. Fenwick tree from the right over reversed values: `(len, cnt)` with capped counts.
2. If the total for `len = L` is below `K`, print `-1`.
3. Walk the layers as above and print the chosen values.

```python
import sys


def super_kth(k, a):
    n = len(a)
    cap = k + 1
    size = n + 1
    bl = [0] * (size + 1)
    bc = [0] * (size + 1)

    def update(pos, L, c):
        while pos <= size:
            if bl[pos] < L:
                bl[pos], bc[pos] = L, c
            elif bl[pos] == L:
                bc[pos] = min(cap, bc[pos] + c)
            pos += pos & -pos

    def query(pos):
        L, c = 0, 1
        while pos > 0:
            if bl[pos] > L:
                L, c = bl[pos], bc[pos]
            elif bl[pos] == L and L > 0:
                c = min(cap, c + bc[pos])
            pos -= pos & -pos
        return L, c

    lf = [0] * n
    cf = [0] * n
    for i in range(n - 1, -1, -1):
        r = n + 1 - a[i]                      # larger values get smaller indices
        L, c = query(r - 1)
        lf[i], cf[i] = L + 1, c
        update(r, L + 1, c)
    L = max(lf)
    layers = [[] for _ in range(L + 1)]
    for i in range(n):
        layers[lf[i]].append(i)
    total = 0
    for i in layers[L]:
        total = min(cap, total + cf[i])
    if total < k:
        return [-1]
    res = []
    prev_pos, prev_w, prev_val = [-1], [1], 0
    for t in range(L, 0, -1):
        cand = {}
        p = acc = 0
        for j in layers[t]:
            while p < len(prev_pos) and prev_pos[p] < j:
                acc = min(cap, acc + prev_w[p])
                p += 1
            if acc and a[j] > prev_val:
                cand.setdefault(a[j], []).append((j, acc))
        for v in sorted(cand):
            cnt = 0
            for j, w in cand[v]:
                cnt = min(cap, cnt + w * cf[j])
            if k <= cnt:
                res.append(v)
                prev_pos = [j for j, _ in cand[v]]
                prev_w = [w for _, w in cand[v]]
                prev_val = v
                break
            k -= cnt
    return res


def main():
    data = sys.stdin.read().split()
    n, k = int(data[0]), int(data[1])
    a = list(map(int, data[2:2 + n]))
    print(' '.join(map(str, super_kth(k, a))))


main()
```

**Watch out.** Equal value sequences from different index sets are separate entries, so they take up several consecutive ranks. In the sample, `1 2 5` occupies ranks 1 and 2 and `1 3 5` is the 3rd. `K` reaches 10¹⁸, so capping at `K + 1` keeps the numbers small without changing any comparison.

```stdin
5 3
1 3 1 2 5
```

```stdout
1 3 5
```

### Counting the Ways

**Problem.** There are `N ≤ 10` weight types, used any number of times, with `Π a_i ≤ 10⁵`. `F(X)` is the number of ways to reach total weight `X`. Find `F(L) + … + F(R)` for `R ≤ 10¹⁷`, modulo 10⁹+7.

**Idea.** The generating function is `Π 1/(1 − x^{a_i})`, and the prefix sums add one more factor `1/(1 − x)`.
- **Common period.** Let `M = Π a_i`. Each `1/(1 − x^{a})` equals `(1 + x^a + … + x^{a(M/a − 1)}) / (1 − x^M)`. The same holds for `1/(1−x)` with `a = 1`. So

  `Σ_{x ≤ X} F(x) = [x^X] Q(x) / (1 − x^M)^{N+1}`,

  where `Q` is a polynomial of degree `< (N+1)·M ≈ 10⁶`.
- **Reading off coefficients.** `[x^q] 1/(1−x^M)^{N+1}` is `C(q/M + N, N)` when `M | q`. So `G(X) = Σ_{t ≡ X (mod M), t ≤ X} Q_t · C((X − t)/M + N, N)`, which has only about `N + 1` terms.
- **Building `Q`.** Multiplying by `1 + x^a + … + x^{a(c−1)}` is a strided prefix sum minus a shifted copy. Use NumPy `cumsum` on a reshaped array.

**Steps.**
1. Build `Q` modulo 10⁹+7, one factor per weight type plus the `1/(1−x)` factor.
2. `C(q + N, N)` for huge `q`: multiply `(q+1)…(q+N)` modulo p and divide by `N!`.
3. Print `G(R) − G(L − 1)`.

```python
import sys

import numpy as np

MOD = 10 ** 9 + 7


def times_block(poly, step, cnt):
    """poly * (1 + x^step + ... + x^(step*(cnt-1))) modulo MOD."""
    out_len = len(poly) + step * (cnt - 1)
    res = np.zeros(out_len + (-out_len) % step, dtype=np.int64)
    res[:len(poly)] = poly
    flat = (np.cumsum(res.reshape(-1, step), axis=0) % MOD).reshape(-1)[:out_len]
    sub = np.zeros(out_len, dtype=np.int64)
    if step * cnt < out_len:
        sub[step * cnt:] = flat[:out_len - step * cnt]
    return (flat - sub) % MOD


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    arr = list(map(int, data[1:1 + n]))
    l, r = int(data[1 + n]), int(data[2 + n])
    M = 1
    for x in arr:
        M *= x
    q = np.ones(1, dtype=np.int64)
    for x in arr:
        q = times_block(q, x, M // x)
    q = times_block(q, 1, M)                      # the prefix-sum factor 1/(1-x)
    nf = 1
    for i in range(1, n + 1):
        nf = nf * i % MOD
    inv_nf = pow(nf, MOD - 2, MOD)

    def binom(t):                                 # C(t + n, n) mod p
        num = 1
        for i in range(1, n + 1):
            num = num * ((t + i) % MOD) % MOD
        return num * inv_nf % MOD

    def G(X):
        if X < 0:
            return 0
        return sum(int(q[t]) * binom((X - t) // M) for t in range(X % M, min(len(q), X + 1), M)) % MOD

    print((G(r) - G(l - 1)) % MOD)


main()
```

**Watch out.** The prefix sums inside each stride column stay below `10⁶·10⁹`, so `int64` is safe before the modulo. `C(t + N, N)` is a polynomial in `t`, so reducing `t + i` modulo p first is fine. `N!` is invertible because `N < p`.

```stdin
3
1 2 3
1 6
```

```stdout
22
```

### Hard Disk Drives

**Problem.** There are `n` pairs of HDD positions and `k` computers. Each pair connects both of its drives to one computer. Place the computers to minimise the total wire length (`n·k ≤ 10⁵`).

**Idea.**
- **Contiguous groups.** Sort the pairs by midpoint `a + b`. Some optimal solution assigns each computer a contiguous run of pairs. A computer serving a group sits at the median of its `2m` drive positions, at cost `(sum of the top m) − (sum of the bottom m)`.
- **Layered DP.** `dp_c[i] = min_j dp_{c−1}[j] + cost(j, i)`. The best split point is monotone in `i`, so the divide-and-conquer optimisation applies.
- **Batching.** Process every segment of one recursion depth together, so each depth is a single batch of `cost(j, i)` queries.
- **Answering the cost queries.** "Sum of the `m` smallest values among positions `[2j, 2i)`" is answered for the whole batch at once by a **wavelet matrix** walked with NumPy, one bit level at a time.

**Steps.**
1. Sort the pairs by `a + b` and lay the drives out as an array of `2n` values. Compress the values to ranks and build the wavelet levels: zero-ranks and prefix sums of the zero side.
2. Layer 1 is `cost(0, i)`. Each further layer runs the batched D&C, with ties broken by the smallest `j`.
3. Print `dp_k[n]`.

```python
import sys

import numpy as np


def main():
    data = sys.stdin.read().split()
    n, k = int(data[0]), int(data[1])
    pairs = sorted(((int(data[2 + 2 * i]), int(data[3 + 2 * i])) for i in range(n)),
                   key=lambda p: p[0] + p[1])
    pts = np.array([x for p in pairs for x in p], dtype=np.int64)
    N = 2 * n
    pre = np.zeros(N + 1, dtype=np.int64)
    pre[1:] = np.cumsum(pts)
    uniq, rank = np.unique(pts, return_inverse=True)
    bits = max(1, int(len(uniq) - 1).bit_length())
    levels = []
    cur, curv = rank.astype(np.int64), pts.copy()
    for lev in range(bits - 1, -1, -1):
        b = (cur >> lev) & 1
        z = np.zeros(N + 1, dtype=np.int64)
        z[1:] = np.cumsum(b == 0)
        s0 = np.zeros(N + 1, dtype=np.int64)
        s0[1:] = np.cumsum(np.where(b == 0, curv, 0))
        levels.append((lev, z, s0, int(z[-1])))
        order = np.argsort(b, kind='stable')
        cur, curv = cur[order], curv[order]

    def cost(j, i):                     # pairs j..i-1, vectorised over arrays j, i
        l, r = 2 * j, 2 * i
        kk = i - j                      # sum of the kk smallest of 2*kk drives
        low = np.zeros_like(kk)
        val = np.zeros_like(kk)
        for lev, z, s0, nz in levels:
            zl, zr = z[l], z[r]
            c0 = zr - zl
            go0 = kk <= c0
            low += np.where(go0, 0, s0[r] - s0[l])
            kk = np.where(go0, kk, kk - c0)
            l = np.where(go0, zl, nz + l - zl)
            r = np.where(go0, zr, nz + r - zr)
            val |= (~go0).astype(np.int64) << lev
        low += kk * uniq[val]
        return pre[2 * i] - pre[2 * j] - 2 * low

    INF = 1 << 60
    prev = np.full(n + 1, INF, dtype=np.int64)
    prev[1:] = cost(np.zeros(n, dtype=np.int64), np.arange(1, n + 1))
    for layer in range(2, k + 1):
        dp = np.full(n + 1, INF, dtype=np.int64)
        lo = np.array([layer]); hi = np.array([n])
        olo = np.array([layer - 1]); ohi = np.array([n - 1])
        while len(lo):
            mid = (lo + hi) // 2
            cnt = np.minimum(ohi, mid - 1) - olo + 1
            seg = np.repeat(np.arange(len(lo)), cnt)
            starts = np.cumsum(cnt) - cnt
            jj = olo[seg] + (np.arange(int(cnt.sum())) - starts[seg])
            vals = prev[jj] + cost(jj, mid[seg])
            first = np.lexsort((jj, vals, seg))[starts]   # best (smallest j on ties) per segment
            opt = jj[first]
            dp[mid] = vals[first]
            lm, rm = lo <= mid - 1, mid + 1 <= hi
            lo, hi, olo, ohi = (np.concatenate([lo[lm], (mid + 1)[rm]]),
                                np.concatenate([(mid - 1)[lm], hi[rm]]),
                                np.concatenate([olo[lm], opt[rm]]),
                                np.concatenate([opt[lm], ohi[rm]]))
        prev = dp
    print(int(prev[n]))


main()
```

**Watch out.** Both drives of a pair go to the same computer, which is why the groups are cut along the midpoint order, not the raw positions. Checked against a brute force over all assignments of pairs to computers. Since `k ≤ n`, using exactly `k` non-empty groups is never worse than leaving a computer idle.

```stdin
5 2
6 7
-1 1
0 1
5 2
7 3
```

```stdout
13
```

### Separate the chocolate

**Problem.** Colour every cell of an `M×N` bar (`M, N ≤ 8`) as Tom's or Derpina's. `T` cells must be Tom's, `D` cells must be Derpina's, and `U` cells are free. Both pieces must be non-empty and connected, neither may contain a 2×2 block, and the sizes may differ by at most `K`. Count the ways.

**Idea.** Use a broken-profile DP over the cells in row-major order. The frontier is the last `N` cells placed.
- **State.**
  - their colours and connectivity labels (normalised);
  - the colour of the cell diagonally up-left, needed for the 2×2 test;
  - for each colour, whether its component has already been **closed**.
- **Values.** A map from "number of Tom's cells" to ways.
- **Placing a cell.** It merges with its up and left neighbours of the same colour.
- **The cell leaving the frontier.** This is the cell above. If no other frontier cell carries its label, its component is finished. That is only allowed if no other cell of that colour is in the frontier, and afterwards that colour may never appear again.

**Steps.**
1. Start with an empty frontier; place the cells one by one.
2. At the end, each colour must have exactly one component: either already closed, or exactly one label in the last row.
3. Add the ways with `|T − D| ≤ K`.

```python
import sys


def separate(grid, K):
    M = len(grid)
    N = len(grid[0]) if M else 0
    if M * N < 2:
        return 0
    NONE = 2
    states = {((NONE,) * N, (0,) * N, NONE, (False, False)): {0: 1}}
    for r in range(M):
        for c in range(N):
            ch = grid[r][c]
            allowed = (0,) if ch == 'T' else (1,) if ch == 'D' else (0, 1)
            nxt = {}
            for (cols, labs, diag, closed), cnts in states.items():
                up = cols[c]
                left = cols[c - 1] if c > 0 else NONE
                for col in allowed:
                    if closed[col]:
                        continue
                    if r > 0 and c > 0 and diag == col and up == col and left == col:
                        continue                              # 2x2 block of one piece
                    ncols, nlabs = list(cols), list(labs)
                    if up == col and left == col:
                        a, b = labs[c], labs[c - 1]
                        nlabs = [a if x == b else x for x in nlabs]
                        lab = a
                    elif up == col:
                        lab = labs[c]
                    elif left == col:
                        lab = labs[c - 1]
                    else:
                        lab = max(labs) + 1
                    ncl = list(closed)
                    if up != NONE and up != col:              # the cell above leaves the frontier
                        upl = nlabs[c]
                        if not any(nlabs[x] == upl and ncols[x] == up for x in range(N) if x != c):
                            if any(ncols[x] == up for x in range(N) if x != c):
                                continue                      # that colour would be split
                            ncl[up] = True
                    ncols[c], nlabs[c] = col, lab
                    mp, norm = {}, []
                    for x in range(N):
                        if ncols[x] == NONE:
                            norm.append(0)
                        else:
                            norm.append(mp.setdefault(nlabs[x], len(mp) + 1))
                    key = (tuple(ncols), tuple(norm), up, tuple(ncl))
                    dst = nxt.setdefault(key, {})
                    add = 1 if col == 0 else 0
                    for tc, w in cnts.items():
                        dst[tc + add] = dst.get(tc + add, 0) + w
            states = nxt
    ans = 0
    for (cols, labs, diag, closed), cnts in states.items():
        good = True
        for col in (0, 1):
            ls = {labs[x] for x in range(N) if cols[x] == col}
            if (closed[col] and ls) or (not closed[col] and len(ls) != 1):
                good = False
        if good:
            ans += sum(w for tc, w in cnts.items() if abs(2 * tc - M * N) <= K)
    return ans


def main():
    data = sys.stdin.read().split()
    if len(data) < 3:
        print(0)
        return
    m, n, k = int(data[0]), int(data[1]), int(data[2])
    grid = data[3:3 + m] if n > 0 else []
    print(separate(grid, k))


main()
```

**Watch out.** The HackerRank template calls `separateTheChocolate(chocolate)` without `K`, so this program reads the input itself. A 1-cell or empty bar cannot be split into two pieces, so it gives 0. In the sample, 12 of the 16 colourings of a 2×2 bar survive: the two single-colour ones and the two diagonal ones fail.

```stdin
2 2 4
UU
UU
```

```stdout
12
```

