## Dynamic Programming

### The Coin Change Problem

**Problem.** Count the ways to make change for `n` from an unlimited supply of the given coin values (order doesn't matter).

**Idea.** The classic unbounded-knapsack count. Process the coins one at a time and let `ways[v]` be the number of ways to make `v` with the coins seen so far. Adding coin `c` gives `ways[v] += ways[v − c]`, scanning `v` upward so the same coin can be reused. Coins are the outer loop, so each combination is counted once, never as several orderings.

**Steps.**
1. `ways[0] = 1`. For each coin `c`, for `v` from `c` to `n`: `ways[v] += ways[v − c]`.

```python
import os


def getWays(n, c):
    ways = [1] + [0] * n
    for coin in c:
        for v in range(coin, n + 1):
            ways[v] += ways[v - coin]
    return ways[n]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m = map(int, input().split())
    c = list(map(int, input().split()))
    fptr.write(str(getWays(n, c)) + '\n')
    fptr.close()
```

**Watch out.** Swapping the loops (amount outer, coin inner) counts orderings: `1+2` and `2+1` become different. The counts overflow 32 bits.

```stdin
4 3
1 2 3
```

```stdout
4
```

### Equal

**Problem.** In one operation, add 1, 2 or 5 to every colleague except one. Find the minimum number of operations to make all values equal.

**Idea.** Giving to everyone except one person is the same, relatively, as *taking* from that one person. So count the 1/2/5 subtractions needed to bring every value down to a common target. The target is at most the minimum. Checking `min, min−1, …, min−4` is enough, because going lower than that never helps with steps of 1, 2 and 5.

**Steps.**
1. `ops(d) = d // 5 + (d % 5) // 2 + (d % 5) % 2`.
2. Return `min over base in [min − 4, min]` of `Σ ops(a − base)`.

```python
import os


def equal(arr):
    lo = min(arr)

    def ops(d):
        return d // 5 + (d % 5) // 2 + (d % 5) % 2

    return min(sum(ops(a - base) for a in arr) for base in range(lo - 4, lo + 1))


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n = int(input().strip())
        arr = list(map(int, input().split()))
        fptr.write(str(equal(arr)) + '\n')
    fptr.close()
```

**Watch out.** Targeting only the minimum misses cases like `[1, 5, 5]`, where lowering everyone to `min − 2` is cheaper.

```stdin
1
4
2 2 3 7
```

```stdout
2
```

### Sherlock and Cost

**Problem.** Choose each `A[i]` in `[1, B[i]]` to maximise `Σ |A[i] − A[i−1]|`.

**Idea.** In an optimal solution every `A[i]` is an extreme value: 1 or `B[i]`. So keep two running bests: the best total with `A[i] = 1` (`lo`) and with `A[i] = B[i]` (`hi`).

**Steps.**
1. `new_lo = max(lo, hi + B[i−1] − 1)`.
2. `new_hi = max(lo + B[i] − 1, hi + |B[i] − B[i−1]|)`.
3. Return `max(lo, hi)`.

```python
import os


def cost(B):
    lo = hi = 0
    for i in range(1, len(B)):
        lo, hi = max(lo, hi + B[i - 1] - 1), max(lo + B[i] - 1, hi + abs(B[i] - B[i - 1]))
    return max(lo, hi)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n = int(input().strip())
        B = list(map(int, input().split()))
        fptr.write(str(cost(B)) + '\n')
    fptr.close()
```

**Watch out.** The tuple assignment updates `lo` and `hi` together; updating `lo` first would feed the new value into `hi`.

```stdin
1
5
10 1 10 1 10
```

```stdout
36
```

### Construct the Array

**Problem.** Count arrays of length `n` over `1..k` that start with 1, end with `x`, and have no two equal neighbours (modulo 10⁹+7).

**Idea.** Every non-1 value is symmetric. So track only two numbers: arrays ending in 1 (`one`) and arrays ending in one *specific* other value (`other`). To end in 1, the previous value must be one of the `k − 1` others. To end in a given non-1 value `v`, the previous value is 1 or one of the `k − 2` other non-`v` values.

**Steps.**
1. Start with `one = 1`, `other = 0`. Repeat `n − 1` times: `one, other = (k−1)·other, one + (k−2)·other`.
2. Return `one` if `x == 1`, else `other`.

```python
import os

MOD = 10 ** 9 + 7


def countArray(n, k, x):
    one, other = 1, 0
    for _ in range(n - 1):
        one, other = (k - 1) * other % MOD, (one + (k - 2) * other) % MOD
    return one if x == 1 else other


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k, x = map(int, input().split())
    fptr.write(str(countArray(n, k, x)) + '\n')
    fptr.close()
```

**Watch out.** `other` counts arrays ending in *one particular* value, not in any non-1 value. That is exactly why the answer for any `x ≠ 1` is `other` itself.

```stdin
4 3 2
```

```stdout
3
```

### Kingdom Division

**Problem.** Colour every city of a tree with one of two siblings so that every city has at least one neighbour of its own colour. Count the colourings modulo 10⁹+7.

**Idea.** Tree DP, fixing the colour of the current node.
- `s[v]`: colourings of `v`'s subtree in which every node, including `v`, is already happy.
- `u[v]`: colourings in which everything below `v` is happy but `v` itself still needs its parent to share its colour.

A child with the same colour as `v` may be in either state, because `v` makes it happy. A child with the other colour must already be happy. So `all = Π (2·s_c + u_c)`, `u[v] = Π s_c` (every child differs) and `s[v] = all − u[v]`. The root can't rely on a parent, so the answer is `2·s[root]` (two choices of the root's colour).

**Steps.**
1. Root at 1 and process children before parents.
2. A leaf has `s = 0`, `u = 1`. Combine the children as above, modulo `MOD`.

```python
import os
from collections import deque

MOD = 10 ** 9 + 7


def kingdomDivision(n, roads):
    adj = [[] for _ in range(n + 1)]
    for a, b in roads:
        adj[a].append(b)
        adj[b].append(a)
    parent = [0] * (n + 1)
    order, seen = [], [False] * (n + 1)
    seen[1] = True
    queue = deque([1])
    while queue:
        v = queue.popleft()
        order.append(v)
        for w in adj[v]:
            if not seen[w]:
                seen[w] = True
                parent[w] = v
                queue.append(w)
    s, u = [0] * (n + 1), [0] * (n + 1)
    total, diff = [1] * (n + 1), [1] * (n + 1)
    for v in reversed(order):
        u[v] = diff[v]
        s[v] = (total[v] - diff[v]) % MOD
        p = parent[v]
        if p:
            total[p] = total[p] * (2 * s[v] + u[v]) % MOD
            diff[p] = diff[p] * s[v] % MOD
    return 2 * s[1] % MOD


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    roads = [list(map(int, input().split())) for _ in range(n - 1)]
    fptr.write(str(kingdomDivision(n, roads)) + '\n')
    fptr.close()
```

**Watch out.** A leaf can only be happy through its parent, which is why `s[leaf] = 0`. Use an iterative order, because a path of 10⁵ cities would overflow recursion.

```stdin
5
1 2
1 3
3 4
3 5
```

```stdout
4
```

### Sam and substrings

**Problem.** Sum the numeric values of all substrings of a digit string, modulo 10⁹+7.

**Idea.** Let `cur` be the sum of all substrings that *end* at position `i`. Every substring ending at `i − 1` extends by one digit, which multiplies it by 10 and adds `d`. Plus there are `i + 1` substrings ending at `i`, and each contributes `d` in its last place. So `cur = 10·cur + d·(i + 1)`, and the answer is the sum of all `cur`.

**Steps.**
1. Scan the digits and update `cur` and `total` modulo `MOD`.

```python
import os

MOD = 10 ** 9 + 7


def substrings(n):
    cur = total = 0
    for i, ch in enumerate(n):
        cur = (cur * 10 + int(ch) * (i + 1)) % MOD
        total = (total + cur) % MOD
    return total


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = input().strip()
    fptr.write(str(substrings(n)) + '\n')
    fptr.close()
```

**Watch out.** The string is up to 2·10⁵ digits, so enumerating substrings (O(n²) of them, each a big number) is hopeless; the recurrence is O(n).

```stdin
16
```

```stdout
23
```

### Fibonacci Modified

**Problem.** `t(i+2) = t(i) + t(i+1)²`. Print the `n`-th term exactly.

**Idea.** Just iterate. The numbers explode (a 20th term has thousands of digits), but Python integers are arbitrary precision.

**Steps.**
1. Repeat `a, b = b, a + b*b` `n − 2` times and return `b`.

```python
import os


def fibonacciModified(t1, t2, n):
    a, b = t1, t2
    for _ in range(n - 2):
        a, b = b, a + b * b
    return b


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t1, t2, n = map(int, input().split())
    fptr.write(str(fibonacciModified(t1, t2, n)) + '\n')
    fptr.close()
```

**Watch out.** In C++ or Java this needs a big-integer class. Python 3.11+ limits `str()` of huge integers (4300 digits by default), so raise the limit with `sys.set_int_max_str_digits(0)` if your terms get that long.

```stdin
0 1 5
```

```stdout
5
```

### Abbreviation

**Problem.** You may capitalise some lowercase letters of `a` and delete the remaining lowercase letters. Can `a` become `b`?

**Idea.** `dp[i][j]` = whether the first `i` characters of `a` can produce the first `j` of `b`. Character `a[i]`:
- **matches** `b[j]` if it is equal or uppercases to it, so move both pointers;
- if it is **lowercase**, it may also be deleted, so move only `i`.

Uppercase letters can never be deleted.

**Steps.**
1. Keep one row per prefix of `a` (as a list of booleans over `j`).
2. Return `dp[len(a)][len(b)]`.

```python
import os


def abbreviation(a, b):
    n, m = len(a), len(b)
    dp = [False] * (m + 1)
    dp[0] = True
    for i in range(n):
        ch = a[i]
        new = [False] * (m + 1)
        for j in range(m + 1):
            if not dp[j]:
                continue
            if j < m and ch.upper() == b[j]:
                new[j + 1] = True
            if ch.islower():
                new[j] = True
        dp = new
    return 'YES' if dp[m] else 'NO'


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        a = input()
        b = input()
        fptr.write(abbreviation(a, b) + '\n')
    fptr.close()
```

**Watch out.** Greedy matching fails on inputs like `a = "AbcDE"`, `b = "ABDE"`: whether to use or skip `b` depends on what comes later.

```stdin
1
daBcd
ABC
```

```stdout
YES
```

### Prime XOR

**Problem.** The values lie in `[3500, 4500]`. Count the distinct multisets drawn from the array whose XOR is prime, modulo 10⁹+7.

**Idea.**
- **Even and odd counts.** A value that occurs `c` times can be used 0..`c` times. Only the parity matters for the XOR: there are `c // 2 + 1` even choices and `(c + 1) // 2` odd ones.
- **The DP.** XORs of 13-bit values stay below 8192. So run a DP over the at most 1001 distinct values, with 8192 XOR states each, vectorised with NumPy: `new = dp·even + dp[i ^ v]·odd`.

**Steps.**
1. Count each value, then fold every distinct value into the DP.
2. Sieve the primes below 8192 and sum `dp` over them.

```python
import os

import numpy as np

MOD = 10 ** 9 + 7
SIZE = 8192
IDX = np.arange(SIZE)
SIEVE = np.ones(SIZE, dtype=bool)
SIEVE[:2] = False
for _p in range(2, int(SIZE ** 0.5) + 1):
    if SIEVE[_p]:
        SIEVE[_p * _p::_p] = False


def primeXor(a):
    counts = np.bincount(a, minlength=4501)
    dp = np.zeros(SIZE, dtype=np.int64)
    dp[0] = 1
    for v in range(3500, 4501):
        c = int(counts[v])
        if c:
            dp = (dp * (c // 2 + 1) + dp[IDX ^ v] * ((c + 1) // 2)) % MOD
    return int(dp[SIEVE].sum() % MOD)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        n = int(input().strip())
        a = list(map(int, input().split()))
        fptr.write(str(primeXor(a)) + '\n')
    fptr.close()
```

**Watch out.** "Unique multisets" means only how many copies of each value are used matters, not which array positions they come from. Hence the `c // 2 + 1` and `(c + 1) // 2` counts rather than powers of 2.

```stdin
1
3
3511 3671 4153
```

```stdout
4
```

### Decibinary Numbers

**Problem.** Decibinary numbers use digits 0–9 with binary place values. List them by decimal value, breaking ties by the digit string read as a decimal number. Print the `x`-th one (`x ≤ 10¹⁶`).

**Idea.**
- **Count by value.** `cnt[p][w]` = the number of ways to write value `w` using `p` digit positions. It satisfies `cnt[p+1][w] = Σ_d cnt[p][w − d·2^p]`.
- **Find the value.** The prefix sums of `cnt[20][w]` over `w` reach 10¹⁶ around `w ≈ 3·10⁵`. So a binary search finds the decimal value `v` and the rank `r` of the answer among the representations of `v`.
- **Build the digits.** Equal values are ordered as decimal strings, which is lexicographic from the most significant position. So choose digits from the top: for each digit `d = 0..9`, skip the `cnt[p][v − d·2^p]` representations that start with `d` while `r` exceeds them.

**Steps.**
1. Build `cnt` with NumPy shifted adds until the cumulative total passes 10¹⁶.
2. For each query, `bisect` the prefix sums, then pick digits greedily from position 19 down to 0.

```python
import os
from bisect import bisect_left

import numpy as np

P = 20
MAXV = 300000
cnt = [np.zeros(MAXV, dtype=np.int64) for _ in range(P + 1)]
cnt[0][0] = 1
for p in range(P):
    step = 1 << p
    cur = np.zeros(MAXV, dtype=np.int64)
    for d in range(10):
        shift = d * step
        if shift >= MAXV:
            break
        cur[shift:] += cnt[p][:MAXV - shift]
    cnt[p + 1] = cur
prefix = np.cumsum(cnt[P]).tolist()


def decibinaryNumbers(x):
    v = bisect_left(prefix, x)
    r = x - (prefix[v - 1] if v else 0) - 1      # 0-based rank among values equal to v
    digits = []
    rest = v
    for p in range(P - 1, -1, -1):
        for d in range(10):
            w = rest - d * (1 << p)
            if w < 0:
                break
            ways = int(cnt[p][w])
            if r < ways:
                digits.append(d)
                rest = w
                break
            r -= ways
    s = ''.join(map(str, digits)).lstrip('0')
    return s or '0'


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        x = int(input().strip())
        fptr.write(decibinaryNumbers(x) + '\n')
    fptr.close()
```

**Watch out.** `cnt[p][w]` already allows leading zeros, so numbers with fewer digits are counted naturally. Without the counting table, enumerating 10¹⁶ numbers is impossible. The table (21 × 3·10⁵ `int64` values) is built once and stays in NumPy; converting it to Python lists would cost hundreds of MB.

```stdin
5
1
2
3
4
10
```

```stdout
0
1
2
10
100
```

### Fair Cut

**Problem.** Give exactly `k` of the `n` integers to Li and the rest to Lu, minimising `Σ |a_i − a_j|` over pairs with `i` from Li and `j` from Lu.

**Idea.** Sort the values. When the `i`-th smallest goes to Li (with `j` Li-items before it), it is larger than the `i − j` Lu-items before it, which adds `+a_i` per pair. It is smaller than the Lu-items still to come, `(n − k) − (i − j)` of them, which adds `−a_i` per pair. It is symmetric for Lu. So each element's contribution depends only on `(i, j)`, giving the DP `dp[j]` = best cost with `j` items assigned to Li so far. NumPy updates the whole `j` row per element.

**Steps.**
1. For each sorted `a_i`, with `j` ranging over the Li-count *before* it:
   - **to Li:** `a_i·((i − j) − ((n − k) − (i − j)))`;
   - **to Lu:** `a_i·(j − (k − j))`.
2. `new[j+1] = min(…, dp[j] + toLi)` and `new[j] = min(…, dp[j] + toLu)`, keeping only valid counts.

```python
import os

import numpy as np


def fairCut(k, arr):
    a = sorted(arr)
    n = len(a)
    inf = np.int64(4 * 10 ** 18)
    dp = np.full(k + 1, inf, dtype=np.int64)
    dp[0] = 0
    j = np.arange(k + 1, dtype=np.int64)
    for i, x in enumerate(a):
        lu_before = i - j
        valid = (lu_before >= 0) & (lu_before <= n - k)
        to_li = x * (lu_before - ((n - k) - lu_before))
        to_lu = x * (j - (k - j))
        new = np.full(k + 1, inf, dtype=np.int64)
        ok_lu = valid & (lu_before < n - k) & (dp < inf)
        new[ok_lu] = dp[ok_lu] + to_lu[ok_lu]
        ok_li = valid & (j < k) & (dp < inf)
        idx = np.nonzero(ok_li)[0]
        cand = dp[idx] + to_li[idx]
        new[idx + 1] = np.minimum(new[idx + 1], cand)
        dp = new
    return int(dp[k])


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    arr = list(map(int, input().split()))
    fptr.write(str(fairCut(k, arr)) + '\n')
    fptr.close()
```

**Watch out.** Each pair is counted once, from the larger element's side as `+` and the smaller element's side as `−`, so the total is the sum of absolute differences without any `abs`. A pure-Python 3000×3000 DP is about 9·10⁶ steps; the NumPy row update avoids that.

```stdin
4 2
4 3 1 2
```

```stdout
6
```

### The Maximum Subarray

**Problem.** Print the maximum non-empty contiguous subarray sum and the maximum non-empty subsequence sum.

**Idea.**
- **Subarray.** Kadane's algorithm: `best_ending_here = max(x, best_ending_here + x)`.
- **Subsequence.** Take every positive number, or the single largest number if none is positive.

**Steps.**
1. Run Kadane for the subarray.
2. The subsequence is the sum of positives, or `max(arr)` when that sum is 0 because nothing is positive.

```python
import os


def maxSubarray(arr):
    best = cur = arr[0]
    for x in arr[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    pos = sum(x for x in arr if x > 0)
    return [best, pos if any(x > 0 for x in arr) else max(arr)]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n = int(input().strip())
        arr = list(map(int, input().split()))
        fptr.write(' '.join(map(str, maxSubarray(arr))) + '\n')
    fptr.close()
```

**Watch out.** Both answers must be non-empty, so for an all-negative array they are the maximum element, not 0.

```stdin
2
4
1 2 3 4
6
2 -1 2 3 4 -5
```

```stdout
10 10
10 11
```
