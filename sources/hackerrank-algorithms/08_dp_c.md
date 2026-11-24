## Dynamic Programming

### Two Robots

**Problem.** Execute `N` queries (go to `a`, carry a candy to `b`) in order using two robots, minimising the total distance. A robot's first move to its first `a` is free.

**Idea.** After query `i`, one robot is certainly at `b_i`, so the state is just the other robot's position `p` (0 meaning "not used yet"). Let `dp[p]` be the best cost so far for state `p`. For the next query `(a, b)`:
- **The same robot continues.** Every state pays `|b_prev − a| + |a − b|` and keeps `p`.
- **The other robot takes it.** It pays `|p − a| + |a − b|` (or just `|a − b|` if `p = 0`). Afterwards the roles swap, so the new state is `b_prev`.

Both options are vectorised over all `p` with NumPy.

**Steps.**
1. The first query sets `dp[0] = |a − b|`.
2. For each later query, `new = dp + |b_prev − a| + |a − b|`, and `new[b_prev] = min(new[b_prev], min(dp + cost_other))`.
3. Return `min(dp)`.

```python
import os

import numpy as np


def twoRobots(m, queries):
    inf = 10 ** 15
    pos = np.arange(m + 1)
    dp = np.full(m + 1, inf, dtype=np.int64)
    a, b = queries[0]
    dp[0] = abs(a - b)
    prev = b
    for a, b in queries[1:]:
        travel = abs(a - b)
        same = dp + abs(prev - a) + travel
        other_cost = np.where(pos == 0, 0, np.abs(pos - a)) + travel
        best_other = int((dp + other_cost).min())
        same[prev] = min(int(same[prev]), best_other)
        dp = np.minimum(same, inf)
        prev = b
    return int(dp.min())


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        m, n = map(int, input().split())
        queries = [list(map(int, input().split())) for _ in range(n)]
        fptr.write(str(twoRobots(m, queries)) + '\n')
    fptr.close()
```

**Watch out.** HackerRank's Python starter reads `T` but then handles only one test case; loop over all of them. A robot that hasn't moved yet appears at its first `a` for free, which is the `p = 0` case.

```stdin
3
5 4
1 5
3 2
4 1
2 4
4 2
1 2
4 3
10 3
2 4
5 4
9 8
```

```stdout
11
2
5
```

### Cut Tree

**Problem.** Count the connected subtrees `T'` (including the empty one) with at most `K` edges leaving `T'`.

**Idea.** Root the tree. Let `f[v][j]` be the number of connected sets whose top node is `v` and that have `j` cut edges going down to `v`'s children's sides. Merge each child in turn: either exclude the child, which adds 1 cut edge, or include it with any of its own sets (a convolution on `j`). A set topped at a non-root node also cuts its parent edge, so it needs `j + 1 ≤ K`; for the root it is `j ≤ K`. Add 1 for the empty subtree.

**Steps.**
1. Process nodes children-first and keep `f[v]` as a list indexed by `j` (capped at `K + 1`).
2. Sum the valid counts over all `v` and add 1.

```python
import os


def cutTree(n, k, edges):
    adj = [[] for _ in range(n + 1)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    parent = [0] * (n + 1)
    order, seen = [1], [False] * (n + 1)
    seen[1] = True
    for v in order:
        for w in adj[v]:
            if not seen[w]:
                seen[w] = True
                parent[w] = v
                order.append(w)
    cap = k + 1
    f = [None] * (n + 1)
    total = 1                               # the empty subtree
    for v in reversed(order):
        cur = [1] + [0] * cap
        for c in adj[v]:
            if c == parent[v]:
                continue
            new = [0] * (cap + 1)
            for j, ways in enumerate(cur):
                if not ways:
                    continue
                new[min(j + 1, cap)] += ways                # cut the edge to c
                for jj, w2 in enumerate(f[c]):
                    if w2:
                        new[min(j + jj, cap)] += ways * w2  # include c's set
            cur = new
        f[v] = cur
        extra = 0 if v == 1 else 1
        total += sum(cur[j] for j in range(cap + 1) if j + extra <= k)
    return total


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    edges = [list(map(int, input().split())) for _ in range(n - 1)]
    fptr.write(str(cutTree(n, k, edges)) + '\n')
    fptr.close()
```

**Watch out.** The empty subtree counts; that is why the 3-node path with `K = 1` gives 6. HackerRank's starter calls `cutTree` while the stub is named `cuttree`, so name the function `cutTree`.

```stdin
3 1
2 1
2 3
```

```stdout
6
```

### Tara's Beautiful Permutations

**Problem.** Every value appears at most twice. Count the distinct arrangements with no two equal neighbours (modulo 10⁹+7).

**Idea.** Inclusion–exclusion over the `p` values that appear twice. Forcing a chosen set of `i` pairs to be adjacent glues each pair into one block, leaving `(n − i)!/2^(p − i)` distinct arrangements (the remaining pairs are identical twins). So the answer is `Σ (−1)^i·C(p, i)·(n − i)!/2^(p − i)`.

**Steps.**
1. Count `p` (values occurring twice) and precompute factorials and inverse powers of 2.
2. Evaluate the alternating sum modulo `MOD`.

```python
import os
from collections import Counter

MOD = 10 ** 9 + 7
FACT = [1] * 2001
for _i in range(1, 2001):
    FACT[_i] = FACT[_i - 1] * _i % MOD
INV2 = pow(2, MOD - 2, MOD)


def beautifulPermutations(arr):
    n = len(arr)
    p = sum(1 for c in Counter(arr).values() if c == 2)
    total, comb = 0, 1
    for i in range(p + 1):
        term = comb * FACT[n - i] % MOD * pow(INV2, p - i, MOD) % MOD
        total = (total + (-term if i % 2 else term)) % MOD
        comb = comb * (p - i) % MOD * pow(i + 1, MOD - 2, MOD) % MOD
    return total


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        n = int(input().strip())
        arr = list(map(int, input().split()))
        fptr.write(str(beautifulPermutations(arr)) + '\n')
    fptr.close()
```

**Watch out.** Equal values are indistinguishable, which is the reason for the division by `2^(p−i)`. A glued pair is a single block and has only one internal order.

```stdin
3
3
1 1 2
2
1 2
4
1 2 2 1
```

```stdout
1
2
2
```

### Wet Shark and Two Subsequences

**Problem.** Count the pairs of equal-length subsequences `(A, B)` with `ΣA + ΣB = r` and `ΣA − ΣB = s` (modulo 10⁹+7).

**Idea.** The two conditions fix `ΣA = (r + s)/2` and `ΣB = (r − s)/2`; if those aren't non-negative integers, the answer is 0. Count the subsequences by length and sum, `cnt[len][sum]`, as a 0/1 knapsack (NumPy shifts per element, lengths descending). The answer is `Σ_len cnt[len][sA]·cnt[len][sB]`.

**Steps.**
1. Check parity and sign, then set `sA` and `sB`.
2. Build `cnt` up to `max(sA, sB)` and combine by length.

```python
import os

import numpy as np

MOD = 10 ** 9 + 7


def twoSubsequences(x, r, s):
    if (r + s) % 2 or r < s:
        return 0
    sa, sb = (r + s) // 2, (r - s) // 2
    top = max(sa, sb)
    m = len(x)
    cnt = np.zeros((m + 1, top + 1), dtype=np.int64)
    cnt[0][0] = 1
    for v in x:
        if v > top:
            continue
        cnt[1:, v:] = (cnt[1:, v:] + cnt[:-1, :top + 1 - v]) % MOD
    return int(sum(int(cnt[l][sa]) * int(cnt[l][sb]) for l in range(1, m + 1)) % MOD)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    m, r, s = map(int, input().split())
    x = list(map(int, input().split()))
    fptr.write(str(twoSubsequences(x, r, s)) + '\n')
    fptr.close()
```

**Watch out.** The NumPy update reads the *old* rows on its right-hand side, because the whole slice is computed before assignment. That makes it a correct 0/1 update without looping lengths backwards. Empty subsequences are excluded, since `r` and `s` count non-empty pairs only through `len ≥ 1`.

```stdin
4 5 3
1 1 1 4
```

```stdout
3
```

### Nikita and the Game

**Problem.** Repeatedly split the array into two non-empty parts with equal sums, keep either part, and continue. Maximise the number of splits.

**Idea.** Plain recursion with prefix sums. A segment can split where its prefix sum reaches half its total. With non-negative values, that is a contiguous run of positions (several when zeros are involved), and taking the first one is enough. Recurse into both halves and take the better. A segment that sums to 0 can always be split down to single elements, which gives `length − 1` points.

**Steps.**
1. `P` = prefix sums. `solve(l, r)`: if the total is 0, return `r − l − 1`. If the total is odd, return 0. Otherwise find `P[i] = P[l] + total/2` with `bisect`.
2. If found, return `1 + max(solve(l, i), solve(i, r))`.

```python
import os
import sys
from bisect import bisect_left

sys.setrecursionlimit(10000)


def arraySplitting(arr):
    p = [0]
    for x in arr:
        p.append(p[-1] + x)

    def solve(l, r):
        total = p[r] - p[l]
        if r - l < 2:
            return 0
        if total == 0:
            return r - l - 1
        if total % 2:
            return 0
        target = p[l] + total // 2
        i = bisect_left(p, target, l + 1, r)
        if i < r and p[i] == target:
            return 1 + max(solve(l, i), solve(i, r))
        return 0

    return solve(0, len(arr))


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n = int(input().strip())
        arr = list(map(int, input().split()))
        fptr.write(str(arraySplitting(arr)) + '\n')
    fptr.close()
```

**Watch out.** Because of zeros, there can be several valid split points; any of them gives the same nonzero part on each side, and the all-zero rule handles the rest. The total must be even.

```stdin
3
3
3 3 3
4
2 2 2 2
7
4 1 0 1 1 0 1
```

```stdout
0
2
3
```

### Choosing White Balls

**Problem.** `k` times: a random index `x` is drawn, and you remove the `x`-th ball counting from the left or from the right (your choice). Maximise the expected number of white balls removed (`n < 30`).

**Idea.** Expectimax with memoisation on the **remaining string**. The string, not the set of removed positions, determines the future, and binary strings of length `L` are far fewer than `C(n, L)` position subsets. Store the state as a bitmask with its length. For each `x`, take the better of removing index `x − 1` or index `L − x`. The reversed string has the same value, so the key is normalised to the smaller of the two.

**Steps.**
1. `value(L, mask)`, with `r = k − (n − L)` removals left: if `r == 0`, return 0. If `r == L`, return `popcount(mask)`.
2. Otherwise average over `x` the better of the two removals, where a removal scores `whiteness + value(L − 1, new mask)`.

```python
import sys
from functools import lru_cache


def main():
    n, k = map(int, input().split())
    s = input().strip()
    mask0 = sum(1 << i for i, ch in enumerate(s) if ch == 'W')

    def rev(mask, length):
        return int(format(mask, f'0{length}b')[::-1], 2) if length else 0

    def remove(mask, j):
        return (mask & ((1 << j) - 1)) | ((mask >> (j + 1)) << j)

    sys.setrecursionlimit(10000)

    @lru_cache(maxsize=None)
    def value(length, mask):
        r = k - (n - length)
        if r == 0:
            return 0.0
        if r == length:
            return float(bin(mask).count('1'))
        total = 0.0
        for x in range(1, length + 1):
            best = 0.0
            for j in {x - 1, length - x}:
                nm = remove(mask, j)
                key = min(nm, rev(nm, length - 1))
                best = max(best, (mask >> j & 1) + value(length - 1, key))
            total += best
        return total / length

    print(f"{value(n, min(mask0, rev(mask0, n))):.10f}")


main()
```

**Watch out.** Memoising on position subsets explodes (`C(29, 14) ≈ 7.7·10⁷`). Memoising on the string itself keeps the state space small enough. For `x` in the middle of an odd-length row, both choices are the same ball, which is why a set is used.

```stdin
3 1
BWW
```

```check
assert abs(float(output.strip()) - 1.0) < 1e-6, output
```

### Mandragora Forest

**Problem.** For each mandragora, either eat it (strength +1) or battle it (gain strength × health). Maximise the total gain.

**Idea.** The order of encounters doesn't matter, because only the final strength multiplies the battle sum. It is best to eat the weakest ones and battle the rest. Try every split `e` of the sorted list: the gain is `(1 + e) × (sum of the largest n − e)`.

**Steps.**
1. Sort, then sweep `e` from 0 to `n − 1` with a running suffix sum and keep the maximum.

```python
import os


def mandragora(H):
    h = sorted(H)
    rest = sum(h)
    best = 0
    for e in range(len(h)):
        best = max(best, (1 + e) * rest)
        rest -= h[e]
    return best


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n = int(input().strip())
        H = list(map(int, input().split()))
        fptr.write(str(mandragora(H)) + '\n')
    fptr.close()
```

**Watch out.** Eating everything gives 0, so `e` stops at `n − 1`. The answer can reach about 10¹⁸, which needs 64-bit integers in other languages.

```stdin
1
3
3 2 2
```

```stdout
10
```

### Red John is Back

**Problem.** Count the tilings of a 4×`n` wall with 1×4 and 4×1 bricks (`M`), then count the primes ≤ `M`.

**Idea.** The leftmost column is either one vertical brick or the start of four stacked horizontal bricks, so `f(n) = f(n−1) + f(n−4)` with `f(0..3) = 1`. `M` is at most about 2·10⁵, so a sieve counts the primes.

**Steps.**
1. Compute `f(n)`, sieve up to `f(n)`, and return the prime count.

```python
import os


def redJohn(n):
    f = [1, 1, 1, 1]
    for i in range(4, n + 1):
        f.append(f[i - 1] + f[i - 4])
    m = f[n]
    if m < 2:
        return 0
    sieve = bytearray([1]) * (m + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(m ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
    return sum(sieve)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        fptr.write(str(redJohn(int(input().strip()))) + '\n')
    fptr.close()
```

**Watch out.** The recurrence needs `f(0) = 1` (the empty wall); with that, `n < 4` gives 1 way, and 1 is not prime.

```stdin
2
1
7
```

```stdout
0
3
```

### LCS Returns

**Problem.** Count the ways (position, character) to insert one alphanumeric character into `a` so that `LCS(a, b)` grows by one.

**Idea.** Inserting `c` between `a[:i]` and `a[i:]` helps exactly when some `b[j] = c` satisfies `pre[i][j] + suf[i][j+1] = LCS`. Here `pre[i][j] = LCS(a[:i], b[:j])` and `suf[i][j] = LCS(a[i:], b[j:])`. Count the distinct characters for each `i`.
- **Fast table rows.** A full DP table is 25·10⁶ cells, slow in Python. Instead use bit-parallel LCS (Hyyrö): each row is one big integer `V`, and `pre[i][j]` is the number of zero bits among its lowest `j` bits. NumPy `unpackbits` plus `cumsum` turns a row into an array.
- **Suffix rows** come from running the same algorithm on the reversed strings.

**Steps.**
1. Compute and store every suffix row (`int16`, using the reversed strings).
2. Sweep `i` forward, updating the prefix row, and add the number of distinct `b[j]` with `pre[j] + suf[j+1] == L`.

```python
import os

import numpy as np


def lcs_rows(a, b):
    """Rows r[i][j] = LCS(a[:i], b[:j]) for all i, via bit-parallel LCS."""
    m = len(b)
    full = (1 << m) - 1
    match = {}
    for j, ch in enumerate(b):
        match[ch] = match.get(ch, 0) | (1 << j)
    nbytes = (m + 7) // 8
    rows = np.zeros((len(a) + 1, m + 1), dtype=np.int16)
    v = full
    for i, ch in enumerate(a, 1):
        u = v & match.get(ch, 0)
        v = ((v + u) | (v - u)) & full
        bits = np.unpackbits(np.frombuffer(v.to_bytes(nbytes, 'little'), dtype=np.uint8),
                             bitorder='little')[:m]
        rows[i, 1:] = np.cumsum(1 - bits.astype(np.int16))
    return rows


def tutzkiAndLcs(a, b):
    n, m = len(a), len(b)
    pre = lcs_rows(a, b)
    rev = lcs_rows(a[::-1], b[::-1])          # rev[x][y] = LCS(a[n-x:], b[m-y:])
    total_lcs = int(pre[n][m])
    codes = np.frombuffer(b.encode(), dtype=np.uint8)
    count = 0
    for i in range(n + 1):
        p = pre[i][:m].astype(np.int32)                     # pre[i][j], j = 0..m-1
        s = rev[n - i][m - np.arange(1, m + 1)].astype(np.int32)   # suf[i][j+1]
        good = (p + s) == total_lcs
        if good.any():
            count += len(np.unique(codes[good]))
    return count


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    a = input().strip()
    b = input().strip()
    fptr.write(str(tutzkiAndLcs(a, b)) + '\n')
    fptr.close()
```

**Watch out.** The same `(position, char)` pair must be counted once even if many `j` qualify, hence `np.unique`. In the bit-parallel update `V' = (V + U) | (V − U)`, the zero bits of `V` count the LCS, and `V` must be masked back to `|b|` bits after the addition.

```stdin
aa
baaa
```

```stdout
4
```

### Grid Walking

**Problem.** Count the `m`-step walks in an `n`-dimensional box that never leave it (modulo 10⁹+7).

**Idea.** The dimensions are independent except for how the `m` steps are shared among them. For each dimension, count the 1-D walks of each length `t` that stay inside: `w_d[t]`, an O(m·D) DP. Then combine with exponential generating functions: `total = m! · [x^m] Π_d (Σ_t w_d[t]·x^t / t!)`, a series of polynomial products truncated at degree `m`.

**Steps.**
1. For each dimension, run the 1-D DP and record `w_d[t]` for `t = 0..m`.
2. Multiply the EGFs together and return `m! · coefficient_m`.

```python
import os

MOD = 10 ** 9 + 7


def gridWalking(m, x, D):
    fact = [1] * (m + 1)
    for i in range(1, m + 1):
        fact[i] = fact[i - 1] * i % MOD
    inv = [pow(f, MOD - 2, MOD) for f in fact]
    egf = [1] + [0] * m
    for pos, size in zip(x, D):
        cur = [0] * (size + 2)
        cur[pos] = 1
        walks = [1]
        for _ in range(m):
            nxt = [0] * (size + 2)
            for p in range(1, size + 1):
                nxt[p] = (cur[p - 1] + cur[p + 1]) % MOD
            cur = nxt
            walks.append(sum(cur) % MOD)
        term = [walks[t] * inv[t] % MOD for t in range(m + 1)]
        egf = [sum(egf[i] * term[s - i] for i in range(s + 1)) % MOD for s in range(m + 1)]
    return egf[m] * fact[m] % MOD


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n, m = map(int, input().split())
        x = list(map(int, input().split()))
        D = list(map(int, input().split()))
        fptr.write(str(gridWalking(m, x, D)) + '\n')
    fptr.close()
```

**Watch out.** Multiplying the per-dimension counts directly forgets that steps in different dimensions interleave. The `m!/(t₁!…t_n!)` factor is exactly what the EGF product supplies.

```stdin
1
2 3
1 1
2 3
```

```stdout
12
```

### Matrix Land

**Problem.** Start anywhere in the first row and move left, right or down. Each cell's value is collected once. Maximise the total on reaching the last row.

**Idea.** Within a row, the best route enters at column `k`, maybe detours to collect a positive stretch on the far side, walks to `j`, maybe detours beyond `j`, and descends from `j`. With prefix sums `P`:
- **Detours.** `left_ext[k] = P[k] − min_{t≤k} P[t]` is the best stretch ending just before `k`. `right_ext[j] = max_{t>j} P[t] − P[j+1]` is the best stretch starting just after `j`.
- **Entering left of `j` (`k ≤ j`).** `max_{k≤j}(dp[k] + left_ext[k] − P[k]) + P[j+1] + right_ext[j]`. This is a running maximum.
- **Entering right of `j` (`k ≥ j`).** The mirror image, using a suffix maximum.

All of these are cumulative max/min operations, so each row is a few NumPy calls.

**Steps.**
1. `dp` starts at zeros (the first row can be entered anywhere).
2. For each row, compute `P`, the two extensions and the two running maxima, then `dp = max(cand1, cand2)`.
3. Return `max(dp)`.

```python
import os

import numpy as np


def matrixLand(A):
    m = len(A[0])
    dp = np.zeros(m, dtype=np.int64)
    for row in A:
        a = np.array(row, dtype=np.int64)
        P = np.concatenate(([0], np.cumsum(a)))            # P[i] = sum a[0..i-1]
        left_ext = P[:m] - np.minimum.accumulate(P[:m])    # best stretch ending at k-1
        suffix_max = np.maximum.accumulate(P[::-1])[::-1]  # max_{t>=i} P[t]
        right_ext = suffix_max[1:] - P[1:]                 # best stretch starting at j+1
        enter_left = np.maximum.accumulate(dp + left_ext - P[:m])
        cand1 = enter_left + P[1:] + right_ext
        enter_right = np.maximum.accumulate((dp + right_ext + P[1:])[::-1])[::-1]
        cand2 = enter_right - P[:m] + left_ext
        dp = np.maximum(cand1, cand2)
    return int(dp.max())


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m = map(int, input().split())
    A = [list(map(int, input().split())) for _ in range(n)]
    fptr.write(str(matrixLand(A)) + '\n')
    fptr.close()
```

**Watch out.** You can walk sideways freely because revisited cells are worth 0. That is why a detour only adds its *positive* best stretch. With `n·m` up to 4·10⁶, per-cell Python loops are too slow, which is why each row is done in NumPy.

```stdin
4 5
1 2 3 -1 -2
-5 -8 -1 2 -150
1 2 3 -250 100
1 1 1 1 20
```

```stdout
37
```

### Knapsack

**Problem.** Using each item value any number of times, get as close as possible to `k` without exceeding it.

**Idea.** Unbounded subset sum: `reach[v]` is true if some combination sums to `v`. Scan `v` upward and mark `reach[v]` whenever `reach[v − x]` is true for some item `x`.

**Steps.**
1. `reach[0] = True`. For `v = 1..k`, check every item.
2. Return the largest reachable `v`.

```python
import os


def unboundedKnapsack(k, arr):
    reach = [True] + [False] * k
    items = set(arr)
    for v in range(1, k + 1):
        reach[v] = any(x <= v and reach[v - x] for x in items)
    return max(v for v in range(k + 1) if reach[v])


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n, k = map(int, input().split())
        arr = list(map(int, input().split()))
        fptr.write(str(unboundedKnapsack(k, arr)) + '\n')
    fptr.close()
```

**Watch out.** HackerRank's Python starter reads `T` and then only one test case; loop over all `T`. Duplicate item values add nothing, so put them in a set first.

```stdin
2
3 12
1 6 9
5 9
3 4 4 4 8
```

```stdout
12
9
```
