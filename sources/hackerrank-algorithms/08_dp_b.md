## Dynamic Programming

### Angry Children 2

**Problem.** Choose `k` packets minimising the unfairness `Σ_{i<j} |x_i − x_j|`.

**Idea.** Sort the packets. The best choice is a contiguous window, since replacing an outer element with one closer to the rest can only shrink the differences. In a sorted window the unfairness is `Σ x_i·(2i − (k−1))`. Sliding the window drops the first element `x_l`, which removes `(S − x_l) − (k−1)·x_l`, and adds `x_r`, which adds `(k−1)·x_r − (S − x_l)`. Each slide is O(1).

**Steps.**
1. Sort, then compute the first window's unfairness and sum directly.
2. Slide, updating the unfairness and the sum, and keep the minimum.

```python
import os


def angryChildren(k, packets):
    x = sorted(packets)
    u = sum(x[i] * (2 * i - (k - 1)) for i in range(k))
    s = sum(x[:k])
    best = u
    for l in range(len(x) - k):
        r = l + k
        u = u - ((s - x[l]) - (k - 1) * x[l]) + ((k - 1) * x[r] - (s - x[l]))
        s += x[r] - x[l]
        best = min(best, u)
    return best


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    k = int(input().strip())
    packets = [int(input().strip()) for _ in range(n)]
    fptr.write(str(angryChildren(k, packets)) + '\n')
    fptr.close()
```

**Watch out.** Recomputing each window's pairwise sum costs O(n·k²). The values reach about `10⁹·k²`, which exceeds 64 bits in other languages for large `k`.

```stdin
7
3
10
100
300
200
1000
20
30
```

```stdout
40
```

### Sherlock's Array Merging Algorithm

**Problem.** Sherlock's merge takes the first element of every non-empty array, sorts those, appends them, and repeats. Given the output `M`, count the collections of arrays that produce it (modulo 10⁹+7).

**Idea.**
- **Shape of `M`.** It splits into consecutive *rounds*. Each round is increasing, and the round sizes never increase, because an empty array stays empty.
- **Counting choices.** The first round fixes the arrays: the collection is unordered, so there is 1 way. In each later round of size `j` following a round of size `i`, the elements can go to any `j` of the `i` still-alive arrays in any order: `i!/(i−j)!` ways.
- **The DP.** Let `dp[pos][i]` count the ways with `pos` elements consumed and a last round of size `i`. Then `dp[pos+j][j] += Σ_{i≥j} dp[pos][i]·i!/(i−j)!`. With `dp'[i] = dp[pos][i]·i!`, that sum is a dot product of `dp'` with `inv_fact[i−j]`, which NumPy does per `(pos, j)`.

**Steps.**
1. `run[pos]` = the length of the increasing run starting at `pos`.
2. Every increasing first round `M[0:k]` seeds `dp[k][k] = 1`.
3. For each `pos` with states, and each `j ≤ min(run[pos], max i)`, add the dot product into `dp[pos+j][j]`.
4. The answer is `Σ_i dp[n][i]`.

```python
import os

import numpy as np

MOD = 10 ** 9 + 7


def arrayMerging(m):
    n = len(m)
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = fact[i - 1] * i % MOD
    inv_fact = [pow(f, MOD - 2, MOD) for f in fact]
    invf = np.array(inv_fact, dtype=np.int64)
    run = [1] * n
    for i in range(n - 2, -1, -1):
        if m[i] < m[i + 1]:
            run[i] = run[i + 1] + 1
    dp = [np.zeros(n + 1, dtype=np.int64) for _ in range(n + 1)]
    for k in range(1, run[0] + 1):
        dp[k][k] = 1
    for pos in range(1, n):
        row = dp[pos]
        if not row.any():
            continue
        scaled = row * np.array(fact, dtype=np.int64) % MOD      # dp'[i] = dp[i] * i!
        top = int(np.nonzero(row)[0].max())
        for j in range(1, min(run[pos], top) + 1):
            seg = scaled[j:top + 1]
            val = int((seg * invf[:len(seg)] % MOD).sum() % MOD)
            if val:
                dp[pos + j][j] = (dp[pos + j][j] + val) % MOD
    return int(dp[n].sum() % MOD)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    m_count = int(input().strip())
    m = list(map(int, input().split()))
    fptr.write(str(arrayMerging(m)) + '\n')
    fptr.close()
```

**Watch out.** The first round contributes no `k!` factor because the collection is a set of arrays. Later rounds do get the `i!/(i−j)!` factor, because by then the arrays are told apart by their earlier elements. Each multiplication is reduced before summing, so the `int64` dot product cannot overflow.

```stdin
3
1 2 3
```

```stdout
4
```

### Prime Digit Sums

**Problem.** Count the `n`-digit numbers in which every 3, 4 and 5 consecutive digits sum to a prime (modulo 10⁹+7), for many `n` up to 4·10⁵.

**Idea.** Every rule looks at most 5 digits back, so the state is the last 4 digits. Precompute the valid 4-digit windows and the transitions `(a,b,c,d) → (b,c,d,e)` that keep all the new 3-, 4- and 5-digit sums prime. Then advance the counts one digit at a time for every `n` up to the largest query, as one NumPy `bincount` per step. The answers for `n ≤ 4` are computed directly.

**Steps.**
1. For `n ≤ 4`: count directly, with a non-zero first digit.
2. Seed the 4-digit states (first digit ≥ 1, valid windows) and step until `max(n)`, recording the total after each step.

```python
import os
from itertools import product

import numpy as np

MOD = 10 ** 9 + 7
PRIMES = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43}


def ok(ds):
    return all(sum(ds[i:i + w]) in PRIMES for w in (3, 4, 5) for i in range(len(ds) - w + 1))


def precompute(limit):
    small = [0, 9, 90]
    small.append(sum(1 for t in product(range(10), repeat=3) if t[0] and ok(t)))
    states = [t for t in product(range(10), repeat=4) if ok(t)]
    index = {t: i for i, t in enumerate(states)}
    src, dst = [], []
    for t in states:
        for e in range(10):
            if ok(t + (e,)):
                src.append(index[t])
                dst.append(index[t[1:] + (e,)])
    src, dst = np.array(src), np.array(dst)
    cur = np.array([1.0 if t[0] else 0.0 for t in states])
    answers = small + [int(cur.sum()) % MOD]
    for _ in range(5, limit + 1):
        cur = np.bincount(dst, weights=cur[src], minlength=len(states)) % MOD
        answers.append(int(cur.sum()) % MOD)
    return answers


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    ns = [int(input().strip()) for _ in range(q)]
    ans = precompute(max(max(ns), 4))
    fptr.write('\n'.join(str(ans[n]) for n in ns) + '\n')
    fptr.close()
```

**Watch out.** The `float64` weights stay exact because every value is below `10·MOD ≈ 10¹⁰`, far under 2⁵³. Leading zeros are allowed inside the sliding state, but the first digit of the number must be non-zero.

```stdin
1
6
```

```stdout
95
```

### HackerRank City

**Problem.** The city doubles twice per step: four copies of the current tree, joined by an H of 2 new nodes and 5 new edges of length `A_i`. Find the sum of all pairwise distances (modulo 10⁹+7).

**Idea.** Track four quantities: `n` (number of nodes), `S` (the answer), `D` (the sum of distances from a corner, where copies attach) and `L` (the corner-to-corner distance). All four corners are symmetric, so one `D` serves for all of them. With copies 1 and 2 hanging off the new node `u`, and copies 3 and 4 off `v`:
- `n' = 4n + 2`
- `L' = 2L + 3A`
- `D' = 4D + n(3L + 8A) + 2L + 3A`
- `S' = 4S + 12nD + 16An² + 8D + 12nA + A`

**Steps.**
1. Start with `n = 1` and the rest 0, apply the formulas for each `A` modulo `MOD`, and return `S`.

```python
import os

MOD = 10 ** 9 + 7


def hackerrankCity(A):
    n, s, d, l = 1, 0, 0, 0
    for a in A:
        s = (4 * s + 12 * n * d + 16 * a * n * n + 8 * d + 12 * n * a + a) % MOD
        d = (4 * d + n * (3 * l + 8 * a) + 2 * l + 3 * a) % MOD
        l = (2 * l + 3 * a) % MOD
        n = (4 * n + 2) % MOD
    return s


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    input()
    A = list(map(int, input().split()))
    fptr.write(str(hackerrankCity(A)) + '\n')
    fptr.close()
```

**Watch out.** Update `S` first and `n` last: each formula needs the *old* values of the others. The cross-copy pairs are `2nD + 2An²` for the two "same-side" pairs and `2nD + 3An²` for the four "opposite" pairs.

```stdin
2
2 1
```

```stdout
2641
```

### Summing Pieces

**Problem.** Over all ways to cut the array into contiguous pieces, sum `Σ (piece sum × piece length)`, modulo 10⁹+7.

**Idea.** Count each element's contribution: `a_i` contributes `(r − l + 1)` for every piece `[l, r]` containing it, times the number of ways to cut the rest. Left of `l` there are `w_L(l) = 2^(l−1)` cuts (1 if `l = 0`); right of `r` there are `w_R(r) = 2^(n−r−2)` (1 if `r = n−1`). The sum splits into products of prefix sums over `l ≤ i` and suffix sums over `r ≥ i`: `c_i = (Σ w_L)(Σ w_R·(r+1)) − (Σ w_L·l)(Σ w_R)`. That is O(n).

**Steps.**
1. Build the prefix sums `P0`, `P1` and the suffix sums `Q0`, `Q1` modulo `MOD`.
2. Answer `Σ a_i·(P0·Q1 − P1·Q0)`.

```python
import os

MOD = 10 ** 9 + 7


def summingPieces(arr):
    n = len(arr)
    pw = [1] * (n + 1)
    for i in range(1, n + 1):
        pw[i] = pw[i - 1] * 2 % MOD
    wl = [1] + [pw[l - 1] for l in range(1, n)]
    wr = [pw[n - r - 2] for r in range(n - 1)] + [1]
    q0, q1 = [0] * (n + 1), [0] * (n + 1)
    for r in range(n - 1, -1, -1):
        q0[r] = (q0[r + 1] + wr[r]) % MOD
        q1[r] = (q1[r + 1] + wr[r] * (r + 1)) % MOD
    total = p0 = p1 = 0
    for i in range(n):
        p0 = (p0 + wl[i]) % MOD
        p1 = (p1 + wl[i] * i) % MOD
        total = (total + arr[i] * (p0 * q1[i] - p1 * q0[i])) % MOD
    return total


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    arr = list(map(int, input().split()))
    fptr.write(str(summingPieces(arr)) + '\n')
    fptr.close()
```

**Watch out.** The edge weights are 1, not 2⁻¹: a piece touching the array's end leaves nothing to cut on that side. With `n` up to 10⁶, any O(n²) scheme times out.

```stdin
5
4 2 9 10 1
```

```stdout
971
```

### Mr K marsh

**Problem.** Find the largest perimeter of a rectangle whose four *border* lines avoid marsh cells (the interior may contain marsh), or print `impossible`.

**Idea.** Fix the top row `r1` and the bottom row `r2`. A column `c` works as a side if the vertical segment from `r1` to `r2` has no marsh (column prefix sums answer that in O(1)). The top and bottom rows must be clean across the whole span. So within each stretch of columns where both rows are clean, the best rectangle uses the first and last usable side columns. NumPy handles each row pair in vectorised passes, and pairs that can't beat the current best are skipped.

**Steps.**
1. Build column prefix sums of marsh cells and a per-row "clean" boolean array.
2. For each `r1 < r2`: skip it if `2(r2−r1) + 2(n−1) ≤ best`. Otherwise label the stretches where both rows are clean, keep the usable side columns, and measure the first-to-last width per stretch.
3. Print the best `2(r2−r1) + 2·width`, or `impossible`.

```python
import numpy as np


def kMarsh(grid):
    m, n = len(grid), len(grid[0])
    g = np.array([[ch == 'x' for ch in row] for row in grid], dtype=np.int32)
    col = np.vstack([np.zeros(n, dtype=np.int32), np.cumsum(g, axis=0)])
    clean = g == 0
    best = 0
    cols = np.arange(n)
    for r1 in range(m - 1):
        for r2 in range(m - 1, r1, -1):
            if 2 * (r2 - r1) + 2 * (n - 1) <= best:
                break
            both = clean[r1] & clean[r2]
            side = both & ((col[r2 + 1] - col[r1]) == 0)
            if side.sum() < 2:
                continue
            seg = np.cumsum(~both)          # stretch id: changes at every dirty column
            idx = cols[side]
            sid = seg[idx]
            starts = np.r_[True, sid[1:] != sid[:-1]]
            ends = np.r_[sid[1:] != sid[:-1], True]
            width = int((idx[ends] - idx[starts]).max())
            if width > 0:
                best = max(best, 2 * (r2 - r1) + 2 * width)
    print(best if best else 'impossible')


if __name__ == '__main__':
    m, n = map(int, input().split())
    grid = [input().strip() for _ in range(m)]
    kMarsh(grid)
```

**Watch out.** The fence needs four distinct corners, so both the height and the width must be at least 1; a single line is `impossible`. Only the perimeter cells matter, so an `x` strictly inside is fine, as in the sample.

```stdin
4 5
.....
.x.x.
.....
.....
```

```stdout
14
```

### Substring Diff

**Problem.** Find the longest `L` such that some length-`L` substrings of `s1` and `s2` differ in at most `k` positions.

**Idea.** A pair of substrings is an aligned window on one *diagonal* (a fixed offset between the strings). For each diagonal, take the mismatch array and its prefix sums `P`. For every end `j`, the earliest valid start is the first `i` with `P[i] ≥ P[j+1] − k`, found with `searchsorted`. That is O(n log n) per diagonal, all in NumPy.

**Steps.**
1. For each offset `d` from `−(n−1)` to `n−1`: compare the aligned characters with NumPy and build `P`.
2. `starts = searchsorted(P, P[1:] − k)`. The best length is `max(ends − starts)`.

```python
import os

import numpy as np


def substringDiff(k, s1, s2):
    a = np.frombuffer(s1.encode(), dtype=np.uint8)
    b = np.frombuffer(s2.encode(), dtype=np.uint8)
    n = len(a)
    best = 0
    for d in range(-(n - 1), n):
        x = a[max(0, d):n + min(0, d)]
        y = b[max(0, -d):n - max(0, d)]
        mis = (x != y).astype(np.int32)
        p = np.concatenate(([0], np.cumsum(mis)))
        starts = np.searchsorted(p, p[1:] - k, side='left')
        ends = np.arange(1, len(p))
        best = max(best, int((ends - starts).max()))
    return best


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        k, s1, s2 = input().split()
        fptr.write(str(substringDiff(int(k), s1, s2)) + '\n')
    fptr.close()
```

**Watch out.** Substrings may start at different positions in the two strings, so all `2n − 1` diagonals count, not just the main one. With `k ≥ L` every window is valid, and the formula handles that automatically.

```stdin
3
2 tabriz torino
0 abacba abcaba
3 helloworld yellomarin
```

```stdout
4
3
8
```

### Xor and Sum

**Problem.** Compute `Σ_{i=0}^{314159} (a XOR (b << i))` modulo 10⁹+7, with `a` and `b` up to 10⁵ bits.

**Idea.** Work bit by bit. Bit `p` of `b << i` equals bit `p − i` of `b`. So over all shifts, bit `p` is set `ones(p)` times, where `ones(p)` counts the 1-bits of `b` in positions `[p − 314159, p]` (a prefix-sum window). XOR with `a`'s bit `p` gives `ones(p)` if that bit is 0, and `314160 − ones(p)` if it is 1. Weight each count by `2^p`.

**Steps.**
1. Store the bits of `b` from the least significant end, with prefix sums.
2. For `p` from 0 to `len(b) + 314159`, compute the count and add `count·2^p mod MOD`.

```python
import os

MOD = 10 ** 9 + 7
SHIFTS = 314159


def xorAndSum(a, b):
    ab = list(map(int, reversed(a)))
    bb = list(map(int, reversed(b)))
    pre = [0]
    for x in bb:
        pre.append(pre[-1] + x)
    total, power = 0, 1
    top = max(len(ab), len(bb) + SHIFTS)
    for p in range(top):
        hi = min(p, len(bb) - 1)
        lo = max(0, p - SHIFTS)
        ones = pre[hi + 1] - pre[lo] if lo <= hi else 0
        bit = ab[p] if p < len(ab) else 0
        cnt = (SHIFTS + 1 - ones) if bit else ones
        total = (total + cnt * power) % MOD
        power = power * 2 % MOD
    return total


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    a = input().strip()
    b = input().strip()
    fptr.write(str(xorAndSum(a, b)) + '\n')
    fptr.close()
```

**Watch out.** Above `a`'s top bit, its bit is 0 and the count is just `ones`. The loop runs about 4·10⁵ times, whereas building 314160 huge shifted integers would be far too slow.

```stdin
10
1010
```

```stdout
489429555
```

### Lego Blocks

**Problem.** Build an `n × m` wall from 1×1…1×4 blocks, with no vertical seam running through the whole height. Count the walls modulo 10⁹+7.

**Idea.** One row of width `w` can be filled in `f(w)` ways (tetranacci: `f(w) = f(w−1) + … + f(w−4)`). Rows are independent, so `T(w) = f(w)^n` counts all walls. The *solid* walls are the rest: subtract every wall whose **first** full seam is at `j`, which is a solid left part of width `j` times anything on the right: `S(m) = T(m) − Σ_{j<m} S(j)·T(m−j)`.

**Steps.**
1. Compute `f` and `T` up to `m`.
2. Compute `S` with the recurrence and return `S(m)`.

```python
import os

MOD = 10 ** 9 + 7


def legoBlocks(n, m):
    f = [1] + [0] * m
    for w in range(1, m + 1):
        f[w] = sum(f[w - b] for b in range(1, 5) if w - b >= 0) % MOD
    t = [pow(x, n, MOD) for x in f]
    s = [0] * (m + 1)
    for w in range(1, m + 1):
        s[w] = (t[w] - sum(s[j] * t[w - j] for j in range(1, w))) % MOD
    return s[m]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n, m = map(int, input().split())
        fptr.write(str(legoBlocks(n, m)) + '\n')
    fptr.close()
```

**Watch out.** Subtract by the *first* seam position, so that each non-solid wall is counted exactly once. Counting "walls with a seam at `j`" for every `j` would over-subtract walls with several seams.

```stdin
4
2 2
3 2
2 3
4 4
```

```stdout
3
7
9
3375
```

### Brick Tiling

**Problem.** Count the tilings of a grid (up to 20 × 8, with blocked cells) by L-shaped bricks of 4 cells in any orientation, modulo 10⁹+7.

**Idea.** Row-by-row DP. An L brick spans at most 3 rows, so the state is the set of filled cells in the current row and the next one, which is about 2¹⁶ states, mostly unused. To fill a row, repeatedly take its first empty cell and try each of the 8 orientations anchored there, meaning shapes whose first cell in row-major order is that cell. That makes every tiling appear exactly once. When the row is full, shift the window down by one row.

**Steps.**
1. Pre-fill blocked cells into the masks. The 8 orientations are listed as offsets from their first cell.
2. For each row, run a DFS over placements, carrying `(cur, nxt, nn)` masks. When `cur` is full, record the state `(nxt, nn | blocked[r+2])`.
3. The answer is the count of the all-empty state after the last row.

```python
import os

MOD = 10 ** 9 + 7
# 8 orientations of the L tetromino, as (dr, dc) offsets from the first cell in row-major order
SHAPES = [
    [(0, 0), (1, 0), (2, 0), (2, 1)],
    [(0, 0), (1, 0), (2, 0), (2, -1)],
    [(0, 0), (0, 1), (1, 0), (2, 0)],
    [(0, 0), (0, 1), (1, 1), (2, 1)],
    [(0, 0), (0, 1), (0, 2), (1, 0)],
    [(0, 0), (0, 1), (0, 2), (1, 2)],
    [(0, 0), (1, 0), (1, 1), (1, 2)],
    [(0, 0), (1, -2), (1, -1), (1, 0)],
]


def brickTiling(grid):
    n, m = len(grid), len(grid[0])
    full = (1 << m) - 1
    blocked = [sum(1 << c for c in range(m) if grid[r][c] == '#') for r in range(n)] + [full, full]
    states = {(blocked[0], blocked[1]): 1}
    for r in range(n):
        nxt_states = {}

        def dfs(rows, ways):
            cur = rows[0]
            if cur == full:
                key = (rows[1], rows[2])
                nxt_states[key] = (nxt_states.get(key, 0) + ways) % MOD
                return
            c = (~cur & (cur + 1)).bit_length() - 1      # first empty column
            for shape in SHAPES:
                new = list(rows)
                good = True
                for dr, dc in shape:
                    cc = c + dc
                    if not (0 <= cc < m) or r + dr >= n or new[dr] >> cc & 1:
                        good = False
                        break
                    new[dr] |= 1 << cc
                if good:
                    dfs(new, ways)

        for (cur, nxt), ways in states.items():
            dfs([cur, nxt, blocked[r + 2]], ways)
        states = nxt_states
    return states.get((full, full), 0)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n, m = map(int, input().split())
        grid = [input().strip() for _ in range(n)]
        fptr.write(str(brickTiling(grid)) + '\n')
    fptr.close()
```

**Watch out.** Each shape must start at the anchor cell, its first cell in row-major order. Otherwise the same tiling is counted once per cell of the brick. A fully blocked grid has exactly one (empty) tiling.

```stdin
3
2 4
....
....
3 3
...
.#.
...
2 2
##
##
```

```stdout
2
4
1
```

### Alien Languages

**Problem.** For letters `1..n`, a "small" letter `i` (`2i ≤ n`) can't end a word and can only be followed by a letter `j ≥ 2i`; "big" letters are unrestricted. Count the words of length `m`, modulo 10⁸+7.

**Idea.** Any valid word cuts uniquely into *blocks*: a chain of small letters, each at least doubling, ending in a big letter. A chain at least doubles at every step, so its length is at most about `log₂ n + 1`. Count the chains `cnt[k]` of each length `k` with suffix sums: chains starting at `i` of length `k+1` = Σ over `j ≥ 2i` of chains of length `k` starting at `j`. Words then follow `W[m] = Σ_k cnt[k]·W[m − k]`.

**Steps.**
1. `f = [1 if i is big]`. Repeatedly let `cnt[k] = Σ f`, then `f'[i] = suffix_sum(f)[2i]` for small `i`, until `f` is all zero.
2. Run the linear recurrence up to `m`.

```python
import os

MOD = 100000007


def alienLanguages(n, m):
    f = [0] * (n + 2)
    for i in range(n // 2 + 1, n + 1):
        f[i] = 1
    cnt = []
    while any(f):
        cnt.append(sum(f) % MOD)
        suf = [0] * (n + 2)
        for i in range(n, 0, -1):
            suf[i] = (suf[i + 1] + f[i]) % MOD
        f = [0] * (n + 2)
        for i in range(1, n // 2 + 1):
            f[i] = suf[2 * i]
    w = [1] + [0] * m
    for length in range(1, m + 1):
        w[length] = sum(cnt[k] * w[length - k - 1] for k in range(min(len(cnt), length))) % MOD
    return w[m]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n, m = map(int, input().split())
        fptr.write(str(alienLanguages(n, m)) + '\n')
    fptr.close()
```

**Watch out.** The modulus is 10⁸+7, not 10⁹+7. Because chains double, `cnt` has fewer than 18 entries, so the word recurrence is about `18·m` steps.

```stdin
3
1 3
2 3
3 2
```

```stdout
1
3
6
```

### Stock Maximize

**Problem.** Each day you may buy one share, sell any number, or do nothing. Maximise the profit given all future prices.

**Idea.** Every share should be sold at the highest price still to come. Scan from the end, tracking the running maximum, and add `max − price` for each day (buy if positive).

**Steps.**
1. Go right to left: `best = max(best, p)` and `profit += best − p`.

```python
import os


def stockmax(prices):
    best = profit = 0
    for p in reversed(prices):
        best = max(best, p)
        profit += best - p
    return profit


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n = int(input().strip())
        prices = list(map(int, input().split()))
        fptr.write(str(stockmax(prices)) + '\n')
    fptr.close()
```

**Watch out.** Scanning forward needs "future max" anyway; the backward pass gets it for free.

```stdin
3
3
5 3 2
3
1 2 100
4
1 3 1 2
```

```stdout
0
197
3
```
