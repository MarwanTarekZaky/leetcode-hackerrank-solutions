## Advanced

### Kindergarten Adventures

**Problem.** Students `1..n` sit in a circle. Collection starts at student `x` and takes one minute per student, so student `x + d` (circularly) gets `d` extra minutes, and student `i` finishes if they get at least `t_i`. Choose the `x` that maximises the number of finished drawings (the smallest on ties).

**Idea.** Student `i` gets `d = (i − x) mod n` minutes, which is `≥ t_i` exactly for the starts `x` in the circular range `[i + 1, i − t_i]`. That range has `n − t_i` starts, and it is empty when `t_i ≥ n`. Add +1 over each student's range with a **circular difference array**; the best `x` is the first maximum of the prefix sums.

**Steps.**
1. For each `i` with `t_i < n`: add 1 on the circular range from `i+1` to `i − t_i` (0-based), splitting it if it wraps.
2. Prefix sums; print the first argmax (1-based).

```python
import sys

import numpy as np


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    t = np.array(data[1:1 + n], dtype=np.int64)
    diff = np.zeros(n + 1, dtype=np.int64)
    i = np.arange(n)
    ok = t < n
    start = (i[ok] + 1) % n
    length = n - t[ok]
    end = start + length                         # exclusive, may pass n (wrap)
    np.add.at(diff, start, 1)
    np.add.at(diff, np.minimum(end, n), -1)
    wrap = end > n
    np.add.at(diff, np.zeros(int(wrap.sum()), dtype=np.int64), 1)
    np.add.at(diff, end[wrap] - n, -1)
    cover = np.cumsum(diff[:n])
    print(int(np.argmax(cover)) + 1)


main()
```

**Watch out.** A student with `t_i = 0` can be served from every start (`n` starts). A wrapping range is split into `[start, n)` and `[0, end − n)`. `argmax` returns the first maximum, which is exactly the "smallest ID" tie-break.

```stdin
3
1 0 0
```

```stdout
2
```

### Cube Summation

**Problem.** In an `N×N×N` cube of zeros, `UPDATE x y z W` **sets** a cell to `W`, and `QUERY x1 y1 z1 x2 y2 z2` sums a box.

**Idea.** A **3-D Fenwick tree**. An update adds the difference from the cell's previous value, which is kept in a dictionary. A box sum combines 8 prefix sums by inclusion–exclusion. With `N ≤ 100` and `M ≤ 1000`, each operation costs `O(log³ N)`.

**Steps.**
1. `add(x, y, z, d)` and `prefix(x, y, z)` as nested Fenwick loops.
2. The box sum from the 8 corner prefixes with alternating signs.

```python
import sys


def main():
    data = sys.stdin.read().split()
    t = int(data[0])
    pos = 1
    out = []
    for _ in range(t):
        n, m = int(data[pos]), int(data[pos + 1])
        pos += 2
        tree = {}
        val = {}

        def add(x, y, z, d):
            i = x
            while i <= n:
                j = y
                while j <= n:
                    k = z
                    while k <= n:
                        tree[(i, j, k)] = tree.get((i, j, k), 0) + d
                        k += k & -k
                    j += j & -j
                i += i & -i

        def prefix(x, y, z):
            s = 0
            i = x
            while i > 0:
                j = y
                while j > 0:
                    k = z
                    while k > 0:
                        s += tree.get((i, j, k), 0)
                        k -= k & -k
                    j -= j & -j
                i -= i & -i
            return s

        for _ in range(m):
            if data[pos] == 'UPDATE':
                x, y, z, w = (int(v) for v in data[pos + 1:pos + 5])
                pos += 5
                add(x, y, z, w - val.get((x, y, z), 0))
                val[(x, y, z)] = w
            else:
                x1, y1, z1, x2, y2, z2 = (int(v) for v in data[pos + 1:pos + 7])
                pos += 7
                s = 0
                for dx, sx in ((x2, 1), (x1 - 1, -1)):
                    for dy, sy in ((y2, 1), (y1 - 1, -1)):
                        for dz, sz in ((z2, 1), (z1 - 1, -1)):
                            s += sx * sy * sz * prefix(dx, dy, dz)
                out.append(s)
    print('\n'.join(map(str, out)))


main()
```

**Watch out.** `UPDATE` *sets* a value, so updating the same cell twice must add only the change. A dictionary keeps the tree sparse: only the touched paths are stored.

```stdin
2
4 5
UPDATE 2 2 2 4
QUERY 1 1 1 3 3 3
UPDATE 1 1 1 23
QUERY 2 2 2 4 4 4
QUERY 1 1 1 3 3 3
2 4
UPDATE 2 2 2 1
QUERY 1 1 1 1 1 1
QUERY 1 1 1 2 2 2
QUERY 2 2 2 2 2 2
```

```stdout
4
4
27
0
1
1
```

### Mr. X and His Shots

**Problem.** Count the overlapping (shot interval, player interval) pairs.

**Idea.** A shot `[A, B]` misses the player `[C, D]` exactly when `A > D` or `B < C`, and both cannot happen at once. So a player stops `N − #(A > D) − #(B < C)` shots. Sort all the `A`s and all the `B`s once; each count is then a `searchsorted`, done for all players together.

**Steps.**
1. Sort `A` and `B`.
2. `total = N·M − Σ #(A > D) − Σ #(B < C)`.

```python
import sys

import numpy as np


def main():
    data = np.array(sys.stdin.buffer.read().split(), dtype=np.int64)
    n, m = int(data[0]), int(data[1])
    shots = data[2:2 + 2 * n].reshape(n, 2)
    players = data[2 + 2 * n:2 + 2 * n + 2 * m].reshape(m, 2)
    A = np.sort(shots[:, 0])
    B = np.sort(shots[:, 1])
    C, D = players[:, 0], players[:, 1]
    greater = n - np.searchsorted(A, D, side='right')      # A > D
    smaller = np.searchsorted(B, C, side='left')            # B < C
    print(int(n * m - greater.sum() - smaller.sum()))


main()
```

**Watch out.** Touching endpoints count as overlapping (`A = D` stops the shot), which is why one search uses `side='right'` and the other `side='left'`.

```stdin
4 4
1 2
2 3
4 5
6 7
1 5
2 3
4 7
5 7
```

```stdout
9
```

### Direct Connections

**Problem.** Cities on a line, with populations; each pair needs `max(P_i, P_j)` cables of length `|x_i − x_j|`. Sum this over all pairs, modulo 10⁹+7 (`N ≤ 2·10⁵`, up to 20 tests).

**Idea.** Order the cities by population: a city is the maximum for its pairs with every less populous city. So each city contributes `P_i · Σ |x_i − x_j|` over the earlier cities `j`. Compute these sums with **CDQ divide and conquer**, vectorised by levels:
- At block size `2^k`, each right block (higher populations) is matched against its left partner.
- The left blocks are sorted by `x` and turned into prefix sums. Each right city's sum of distances comes from one global `searchsorted`, with block ids added as large offsets.

**Steps.**
1. Sort the cities by population (ties in any order: the maximum is the same).
2. For each level, compute every right element's distance sum to its partner left block; accumulate `P · sum` modulo p.

```python
import sys

import numpy as np

MOD = 10 ** 9 + 7


def solve(x, p):
    order = np.argsort(p, kind='stable')
    x = x[order]
    p = p[order]
    n = len(x)
    total = 0
    big = int(x.max()) + 1 if n else 1
    size = 1
    while size < n:
        idx = np.arange(n)
        blk = idx // size
        right = (blk % 2 == 1)
        partner_start = (blk - 1) * size              # start of the left partner block
        ridx = idx[right]
        if len(ridx) == 0:
            size *= 2
            continue
        # sorted x within each left block, with a per-block offset to search globally
        left_mask = ~right
        lidx = idx[left_mask]
        lblk = blk[left_mask]
        key = lblk * big + x[lidx]
        o = np.argsort(key, kind='stable')
        skey = key[o]
        sx = x[lidx][o]
        csum = np.concatenate(([0], np.cumsum(sx)))
        # first position of each left block in the sorted arrays
        lstart = np.searchsorted(skey, (blk[ridx] - 1) * big)
        lend = np.searchsorted(skey, (blk[ridx] - 1) * big + big)
        cut = np.searchsorted(skey, (blk[ridx] - 1) * big + x[ridx], side='right')
        xr = x[ridx]
        cnt_le = cut - lstart
        cnt_gt = lend - cut
        sum_le = csum[cut] - csum[lstart]
        sum_gt = csum[lend] - csum[cut]
        dist = (xr * cnt_le - sum_le + sum_gt - xr * cnt_gt) % MOD
        total = (total + int((dist * (p[ridx] % MOD) % MOD).sum())) % MOD
        size *= 2
    return total


def main():
    data = sys.stdin.buffer.read().split()
    t = int(data[0])
    pos = 1
    out = []
    for _ in range(t):
        n = int(data[pos])
        x = np.array(data[pos + 1:pos + 1 + n], dtype=np.int64)
        p = np.array(data[pos + 1 + n:pos + 1 + 2 * n], dtype=np.int64)
        pos += 1 + 2 * n
        out.append(solve(x, p))
    print('\n'.join(map(str, out)))


main()
```

**Watch out.** The distance sums reach about `2·10⁵ · 10⁹ = 2·10¹⁴`, which is safe in `int64`. The product with `P ≤ 10⁴` could overflow, so reduce modulo p first. Every pair is counted exactly once, at the level where the two cities first fall into sibling blocks.

```stdin
2
3
1 3 6
10 20 30
5
5 55 555 55555 555555
3333 333 333 33 35
```

```stdout
280
463055586
```

### Subsequence Weighting

**Problem.** Find the maximum total weight of a strictly increasing subsequence of `a`.

**Idea.** `best[i] = w_i + max(best[j])` over the earlier `j` with `a_j < a_i`. A **Fenwick tree for prefix maxima** over the compressed values answers the inner maximum in `O(log n)`; process the elements left to right.

**Steps.**
1. Compress `a` to ranks.
2. For each element: `q = prefix_max(rank − 1)`, `v = q + w`, `update(rank, v)`; track the maximum.

```python
import sys


def main():
    data = sys.stdin.buffer.read().split()
    t = int(data[0])
    pos = 1
    out = []
    for _ in range(t):
        n = int(data[pos])
        a = list(map(int, data[pos + 1:pos + 1 + n]))
        w = list(map(int, data[pos + 1 + n:pos + 1 + 2 * n]))
        pos += 1 + 2 * n
        rank = {v: i + 1 for i, v in enumerate(sorted(set(a)))}
        size = len(rank)
        tree = [0] * (size + 1)
        best = 0
        for x, wt in zip(a, w):
            r = rank[x]
            i = r - 1
            q = 0
            while i > 0:
                if tree[i] > q:
                    q = tree[i]
                i -= i & -i
            v = q + wt
            if v > best:
                best = v
            i = r
            while i <= size:
                if tree[i] < v:
                    tree[i] = v
                i += i & -i
        out.append(best)
    print('\n'.join(map(str, out)))


main()
```

**Watch out.** "Strictly increasing" means the query stops at `rank − 1`. Equal values must not extend each other.

```stdin
2
4
1 2 3 4
10 20 30 40
8
1 2 3 4 1 2 3 4
10 20 30 40 15 15 15 50
```

```stdout
100
110
```

### Jim and the Skyscrapers

**Problem.** Count the ordered pairs `(i, j)`, `i ≠ j`, of equal-height buildings with no taller building between them.

**Idea.** Use a **monotonic stack of (height, count)**, decreasing from bottom to top. A new building first pops every lower height; those can no longer pair with anything to the right. If the top then has the same height, every building in that group pairs with the new one (2 ordered pairs each), and the group grows; otherwise a new group starts.

**Steps.**
1. Pop the heights lower than `h`.
2. If the top equals `h`: `answer += 2·count`, `count += 1`; otherwise push `(h, 1)`.

```python
import sys


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    st = []
    ans = 0
    for h in map(int, data[1:1 + n]):
        while st and st[-1][0] < h:
            st.pop()
        if st and st[-1][0] == h:
            ans += 2 * st[-1][1]
            st[-1][1] += 1
        else:
            st.append([h, 1])
    print(ans)


main()
```

**Watch out.** Pairs are ordered, which is where the factor 2 comes from. A group of `k` equal buildings contributes `k(k−1)` pairs in total.

```stdin
6
3 2 1 2 3 3
```

```stdout
8
```

### Palindromic Subsets

**Problem.** Range "shift every letter by `t`" updates, and range queries counting the non-empty index subsets whose letters can be rearranged into a palindrome (modulo 10⁹+7).

**Idea.** **Counting.** If letter `k` occurs `c_k` times, its even-sized and odd-sized selections number `2^{c_k − 1}` each (for `c_k ≥ 1`). A palindrome allows at most one odd letter. So the count is `E · (1 + #{letters present}) − 1`, where `E = Π 2^{c_k − 1}` over the present letters.

**Data structure.** **Square-root decomposition** with NumPy.
- Each block keeps its 26 letter counts and a pending shift.
- A shift on whole blocks only changes the pending shifts.
- Partial blocks are rebuilt from their characters.
- A query sums the rolled counts of its whole blocks (one fancy-indexed NumPy gather) plus the partial pieces.

**Steps.**
1. Store the letters as an array; blocks of size about 300, with counts and lazy shifts.
2. Update and query as above; the answer comes from the 26 counts.

```python
import sys

import numpy as np

MOD = 10 ** 9 + 7


def main():
    data = sys.stdin.buffer.read().split()
    n, q = int(data[0]), int(data[1])
    s = np.frombuffer(data[2], dtype=np.uint8).astype(np.int64) - 97
    B = 320
    nb = (n + B - 1) // B
    cnt = np.zeros((nb, 26), dtype=np.int64)
    lazy = np.zeros(nb, dtype=np.int64)
    blk = np.arange(n) // B
    np.add.at(cnt, (blk, s), 1)
    letters = np.arange(26)
    pow2 = [1] * (n + 1)
    for i in range(1, n + 1):
        pow2[i] = pow2[i - 1] * 2 % MOD

    def push(b):                                   # apply the pending shift to block b
        if lazy[b]:
            lo, hi = b * B, min(n, (b + 1) * B)
            s[lo:hi] = (s[lo:hi] + lazy[b]) % 26
            lazy[b] = 0

    def rebuild(b):
        lo, hi = b * B, min(n, (b + 1) * B)
        cnt[b] = np.bincount(s[lo:hi], minlength=26)

    out = []
    pos = 3
    for _ in range(q):
        if data[pos] == b'1':
            i, j, t = int(data[pos + 1]), int(data[pos + 2]), int(data[pos + 3]) % 26
            pos += 4
            if t == 0:
                continue
            bi, bj = i // B, j // B
            if bi == bj:
                push(bi)
                s[i:j + 1] = (s[i:j + 1] + t) % 26
                rebuild(bi)
            else:
                push(bi)
                s[i:(bi + 1) * B] = (s[i:(bi + 1) * B] + t) % 26
                rebuild(bi)
                push(bj)
                s[bj * B:j + 1] = (s[bj * B:j + 1] + t) % 26
                rebuild(bj)
                lazy[bi + 1:bj] = (lazy[bi + 1:bj] + t) % 26
        else:
            i, j = int(data[pos + 1]), int(data[pos + 2])
            pos += 3
            bi, bj = i // B, j // B
            if bi == bj:
                push(bi)
                c = np.bincount(s[i:j + 1], minlength=26)
            else:
                push(bi)
                push(bj)
                c = np.bincount(s[i:(bi + 1) * B], minlength=26) + np.bincount(s[bj * B:j + 1], minlength=26)
                if bj > bi + 1:
                    mid = np.arange(bi + 1, bj)
                    # letter k in a block with shift L came from letter (k - L) % 26
                    src = (letters[None, :] - lazy[mid][:, None]) % 26
                    c = c + cnt[mid[:, None], src].sum(axis=0)
            E = 1
            present = 0
            for v in c.tolist():
                if v:
                    E = E * pow2[v - 1] % MOD
                    present += 1
            out.append((E * (1 + present) - 1) % MOD)
    print('\n'.join(map(str, out)))


main()
```

**Watch out.**
- **Large shifts.** Shifts are taken modulo 26, since `t` can be 10⁹.
- **Pending shifts.** A block's pending shift must be applied to its characters before they are touched or counted directly; a block's own counts stay "unshifted" until then.
- **Testing.** Checked against a brute force over all subsets of small strings.

```stdin
3 5
aba
2 0 2
2 0 0
2 1 2
1 0 1 1
2 0 2
```

```stdout
5
1
2
3
```

### Polynomial Division

**Problem.** Point updates on the coefficients `c`, and queries asking whether `P(x) = Σ_{k} c_{l+k} x^k` is divisible by `a·x + b` over `Z_p`.

**Idea.** By the factor theorem, `a·x + b` divides `P` exactly when `P(r) = 0` for the root `r = −b·a⁻¹`. Since `P(r) = r^{−l} · Σ_{i=l}^{r} c_i r^i`, it is enough to test whether `Σ c_i r^i` over the range is 0. A **Fenwick tree** holds `c_i · r^i mod p`, which handles updates and range sums. If `b = 0`, then `r = 0` and `P(0) = c_l`.

**Steps.**
1. `r = −b·a^{p−2} mod p`; precompute the powers `r^i`.
2. Fenwick over `c_i r^i`; an update adds the difference; a query checks the range sum.

```python
import sys

MOD = 10 ** 9 + 7


def main():
    data = sys.stdin.buffer.read().split()
    n, a, b, q = (int(v) for v in data[:4])
    c = [int(v) for v in data[4:4 + n]]
    r = (-b * pow(a, MOD - 2, MOD)) % MOD
    pw = [1] * n
    for i in range(1, n):
        pw[i] = pw[i - 1] * r % MOD
    tree = [0] * (n + 1)
    vals = [ci * pi % MOD for ci, pi in zip(c, pw)]
    for i, v in enumerate(vals, 1):               # O(n) Fenwick build
        tree[i] = (tree[i] + v) % MOD
        j = i + (i & -i)
        if j <= n:
            tree[j] = (tree[j] + tree[i]) % MOD

    def prefix(i):
        s = 0
        while i > 0:
            s += tree[i]
            i -= i & -i
        return s % MOD

    out = []
    pos = 4 + n
    for _ in range(q):
        t, u, v = int(data[pos]), int(data[pos + 1]), int(data[pos + 2])
        pos += 3
        if t == 1:
            c[u] = v
            new = v * pw[u] % MOD
            d = (new - vals[u]) % MOD
            vals[u] = new
            i = u + 1
            while i <= n:
                tree[i] = (tree[i] + d) % MOD
                i += i & -i
        else:
            if r == 0:
                ok = c[u] % MOD == 0
            else:
                ok = (prefix(v + 1) - prefix(u)) % MOD == 0
            out.append('Yes' if ok else 'No')
    print('\n'.join(out))


main()
```

**Watch out.** With `r = 0`, every term past the first vanishes, so only `c_l` decides. Dividing by `r^l` is not needed when testing for zero, since `r ≠ 0` is invertible.

```stdin
3 2 2 3
1 2 3
2 0 2
1 2 1
2 0 2
```

```stdout
No
Yes
```
