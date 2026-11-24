## Dynamic Programming

### Bricks Game

**Problem.** Two players alternately take 1–3 bricks from the top of a stack, scoring the numbers on them. Both play optimally. What is your score if you move first?

**Idea.** `best[i]` = the most the player to move can collect from bricks `i..n−1`. Whatever you don't take, your opponent will optimise against you. So taking `t` bricks gives `sum(i..i+t−1) + (suffix[i+t] − best[i+t])`, and `best[i]` is the maximum over `t = 1..3`.

**Steps.**
1. Build suffix sums. Fill `best` from the bottom of the stack up.
2. Return `best[0]`.

```python
import os


def bricksGame(arr):
    n = len(arr)
    suffix = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        suffix[i] = suffix[i + 1] + arr[i]
    best = [0] * (n + 4)
    for i in range(n - 1, -1, -1):
        best[i] = max(suffix[i] - best[i + t] if i + t <= n else suffix[i] for t in (1, 2, 3))
    return best[0]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n = int(input().strip())
        arr = list(map(int, input().split()))
        fptr.write(str(bricksGame(arr)) + '\n')
    fptr.close()
```

**Watch out.** "Take `t` bricks, then the opponent's best" simplifies to `suffix[i] − best[i+t]`: everything from `i` on, minus what the opponent gets. Greedily taking the largest sum now is wrong, as the first sample shows.

```stdin
2
5
999 1 1 1 0
5
0 1 1 1 999
```

```stdout
1001
999
```

### The Longest Increasing Subsequence

**Problem.** Find the length of the longest strictly increasing subsequence (n up to 10⁶).

**Idea.** Patience sorting: `tails[L]` is the smallest possible last value of an increasing subsequence of length `L + 1`. Each new value replaces the first tail that is ≥ it (`bisect_left`) or extends the list. The final length of `tails` is the answer, in O(n log n).

**Steps.**
1. For each `x`, `i = bisect_left(tails, x)`. Append if `i == len(tails)`, else set `tails[i] = x`.

```python
import os
from bisect import bisect_left


def longestIncreasingSubsequence(arr):
    tails = []
    for x in arr:
        i = bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    arr = [int(input().strip()) for _ in range(n)]
    fptr.write(str(longestIncreasingSubsequence(arr)) + '\n')
    fptr.close()
```

**Watch out.** `bisect_left` enforces *strict* increase; `bisect_right` would allow equal values. `tails` is not an actual subsequence, only its length is meaningful.

```stdin
5
2
7
4
3
8
```

```stdout
3
```

### Coin on the Table

**Problem.** A coin follows the arrow letters from the top-left cell. Change as few letters as possible so that the coin reaches `*` within `k` steps.

**Idea.** Use a time-expanded shortest path. `cost[t][cell]` = the fewest changes needed to have the coin on `cell` at time `t`. Moving in the direction the cell already shows is free; any other direction costs 1. A shortest path never benefits from a loop, so it visits each cell at most once and "one direction per cell" is automatic. Each time step is four NumPy shifted minimums.

**Steps.**
1. `cost[0][start] = 0`. For `t < k`: for each direction, shift `cost` from the cells that point there (free) or from any non-star cell (+1), and take the minimum.
2. The answer is the minimum of `cost[t][star]` over `t ≤ k`, or -1.

```python
import os

import numpy as np


def coinOnTheTable(m, k, board):
    n = len(board)
    inf = 10 ** 9
    letters = np.array([list(row) for row in board])
    star = tuple(np.argwhere(letters == '*')[0])
    cost = np.full((n, m), inf, dtype=np.int64)
    cost[0, 0] = 0
    best = cost[star]
    moves = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}
    for _ in range(k):
        src = cost.copy()
        src[star] = inf            # the coin never leaves '*'
        new = np.full((n, m), inf, dtype=np.int64)
        for ch, (dr, dc) in moves.items():
            step = src + (letters != ch)
            r0, r1 = max(0, -dr), n - max(0, dr)
            c0, c1 = max(0, -dc), m - max(0, dc)
            target = new[r0 + dr:r1 + dr, c0 + dc:c1 + dc]
            np.minimum(target, step[r0:r1, c0:c1], out=target)
        cost = new
        best = min(best, cost[star])
    return int(best) if best < inf else -1


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m, k = map(int, input().split())
    board = [input().strip() for _ in range(n)]
    fptr.write(str(coinOnTheTable(m, k, board)) + '\n')
    fptr.close()
```

**Watch out.** The `*` cell is absorbing: the coin stays there, so its cost must not spread further. If the coin starts on `*`, the answer is 0. Arrows pointing off the board just lose the coin, so those moves are dropped by the slicing.

```stdin
2 2 3
RD
*L
```

```stdout
0
```

### The Longest Common Subsequence

**Problem.** Print one longest common subsequence of two integer arrays (any valid one is accepted).

**Idea.** Use the classic LCS table, `dp[i][j]` for prefixes, then walk back from `dp[n][m]`: on a match take the element diagonally, otherwise move toward the larger neighbour.

**Steps.**
1. Fill the table. Backtrack and collect the elements, then reverse them.

```python
import os


def longestCommonSubsequence(a, b):
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n):
        for j in range(m):
            dp[i + 1][j + 1] = dp[i][j] + 1 if a[i] == b[j] else max(dp[i][j + 1], dp[i + 1][j])
    out, i, j = [], n, m
    while i and j:
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return out[::-1]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m = map(int, input().split())
    a = list(map(int, input().split()))
    b = list(map(int, input().split()))
    fptr.write(' '.join(map(str, longestCommonSubsequence(a, b))) + '\n')
    fptr.close()
```

**Watch out.** Several LCSs can exist (the sample also has `3 4 1`), so the hidden test checks length and validity rather than exact text.

```stdin
5 6
1 2 3 4 1
3 4 1 2 1 3
```

```check
a = [1, 2, 3, 4, 1]
b = [3, 4, 1, 2, 1, 3]
got = list(map(int, output.split()))

def is_sub(x, y):
    it = iter(y)
    return all(v in it for v in x)

assert len(got) == 3 and is_sub(got, a) and is_sub(got, b), got
```

### Play with words

**Problem.** Pick two non-overlapping palindromic subsequences, the first entirely left of the second, and maximise the product of their lengths.

**Idea.** All the pieces come from the longest-palindromic-subsequence table `lps[i][j]`. The answer is `max over k of lps[0][k] · lps[k+1][n−1]`, so only row 0 and the last column are needed. Fill the table **diagonal by diagonal** (by interval length) with NumPy, saving those two edges as they appear.

**Steps.**
1. Keep diagonals `len−2` and `len−1`. Each new diagonal is `prev2[i+1] + 2` where `s[i] = s[i+len−1]`, else `max(prev1[i], prev1[i+1])`.
2. Record `pre[len−1] = diag[0]` and `suf[n−len] = diag[last]`, then maximise `pre[k]·suf[k+1]`.

```python
import os

import numpy as np


def playWithWords(s):
    n = len(s)
    a = np.frombuffer(s.encode(), dtype=np.uint8)
    pre = np.zeros(n, dtype=np.int64)      # lps[0][k]
    suf = np.zeros(n, dtype=np.int64)      # lps[k][n-1]
    prev2 = np.zeros(n + 1, dtype=np.int64)          # length 0 diagonal (empty)
    prev1 = np.ones(n, dtype=np.int64)               # length 1 diagonal
    pre[0], suf[n - 1] = 1, 1
    for length in range(2, n + 1):
        cnt = n - length + 1
        same = a[:cnt] == a[length - 1:]
        inner = prev2[1:cnt + 1] + 2 if length > 2 else np.full(cnt, 2, dtype=np.int64)
        cur = np.where(same, inner, np.maximum(prev1[:cnt], prev1[1:cnt + 1]))
        pre[length - 1] = cur[0]
        suf[n - length] = cur[-1]
        prev2, prev1 = prev1, cur
    return int((pre[:-1] * suf[1:]).max())


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    s = input().strip()
    fptr.write(str(playWithWords(s)) + '\n')
    fptr.close()
```

**Watch out.** A pure-Python O(n²) loop is 9·10⁶ steps for n = 3000, slow in CPython. Diagonals vectorise cleanly because each one depends only on the previous two.

```stdin
eeegeeksforskeeggeeks
```

```stdout
50
```

### Black and White Tree

**Problem.** Add edges to make the bipartite graph connected and still properly 2-coloured, with `|#black − #white|` as small as possible. Print `D` and the added edges (any valid answer).

**Idea.**
- **The difference `D`.** Each component has a fixed 2-colouring, up to swapping, with an imbalance `d_i`. Choosing the swaps means splitting the `d_i` into a `+` and a `−` group as evenly as possible: a subset-sum over the `d_i`. Group equal values, split the counts into powers of two, and run the 0/1 subset sum with Python-int bitsets. Keep each step's bitset so the chosen subset can be reconstructed.
- **The edges.** Once the colours are fixed, use one white hub `w0` and one black hub `b0`. Connect each other component to `w0` through one of its black nodes, or to `b0` through a white node. Link the hubs too if they lie in different components.

**Steps.**
1. BFS-colour each component and record its node lists and imbalance.
2. Subset-sum towards `T/2`, reconstruct the chosen groups, and orient each component (larger side white if chosen).
3. Emit the hub edges.

```python
import sys
from collections import Counter, deque


def main():
    data = sys.stdin.buffer.read().split()
    n, m = int(data[0]), int(data[1])
    adj = [[] for _ in range(n + 1)]
    for i in range(m):
        u, v = int(data[2 + 2 * i]), int(data[3 + 2 * i])
        adj[u].append(v)
        adj[v].append(u)
    color = [-1] * (n + 1)
    comps = []
    for s in range(1, n + 1):
        if color[s] >= 0:
            continue
        color[s] = 0
        sides = ([s], [])
        queue = deque([s])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if color[v] < 0:
                    color[v] = 1 - color[u]
                    sides[color[v]].append(v)
                    queue.append(v)
        big, small = (sides[0], sides[1]) if len(sides[0]) >= len(sides[1]) else (sides[1], sides[0])
        comps.append((big, small))
    diffs = [len(b) - len(s) for b, s in comps]
    total = sum(diffs)
    items = []                                   # (weight, value d, how many copies)
    for d, c in Counter(x for x in diffs if x).items():
        k = 1
        while c > 0:
            take = min(k, c)
            items.append((d * take, d, take))
            c -= take
            k *= 2
    reach, history = 1, []
    for w, _, _ in items:
        history.append(reach)
        reach |= reach << w
    target = total // 2
    while not (reach >> target) & 1:
        target -= 1
    D = total - 2 * target
    use = Counter()
    s = target
    for (w, d, take), before in zip(reversed(items), reversed(history)):
        if not (before >> s) & 1:
            s -= w
            use[d] += take
    white_side = []                              # per component: which list is white
    for big, small in comps:
        d = len(big) - len(small)
        if d and use[d] > 0:
            use[d] -= 1
            white_side.append((big, small))      # larger side white
        else:
            white_side.append((small, big))      # larger side black
    edges = []
    if len(comps) > 1:
        w_comp = next(i for i, (w, b) in enumerate(white_side) if w)
        w0 = white_side[w_comp][0][0]
        if white_side[w_comp][1]:
            b_comp, b0 = w_comp, white_side[w_comp][1][0]
        else:
            b_comp = next(i for i, (w, b) in enumerate(white_side) if b)
            b0 = white_side[b_comp][1][0]
            edges.append((w0, b0))
        for i, (whites, blacks) in enumerate(white_side):
            if i in (w_comp, b_comp):
                continue
            edges.append((w0, blacks[0]) if blacks else (b0, whites[0]))
    out = [f"{D} {len(edges)}"] + [f"{u} {v}" for u, v in edges]
    print('\n'.join(out))


main()
```

**Watch out.**
- **Bitset size.** The subset-sum bitsets have about `N` bits each. Binary splitting keeps the number of items near `√N·log N`, so storing them for reconstruction is affordable.
- **Unconnectable pieces.** Two single-colour components of the same colour can't be joined directly, which is why the hubs exist.
- **Many answers.** The hidden test re-checks connectivity, bipartiteness and the optimal `D`.

```stdin
8 6
1 2
3 4
3 5
3 6
3 7
3 8
```

```check
lines = output.strip().split('\n')
D, K = map(int, lines[0].split())
assert D == 4, D
n = 8
edges = [(1, 2), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8)] + [tuple(map(int, l.split())) for l in lines[1:1 + K]]
adj = {v: [] for v in range(1, n + 1)}
for u, v in edges:
    adj[u].append(v)
    adj[v].append(u)
col = {1: 0}
stack = [1]
while stack:
    u = stack.pop()
    for v in adj[u]:
        if v not in col:
            col[v] = 1 - col[u]
            stack.append(v)
        assert col[v] != col[u], 'not bipartite'
assert len(col) == n, 'not connected'
assert abs(sum(col.values()) * 2 - n) == D
```

### Counting Special Sub-Cubes

**Problem.** For each `k`, count the `k×k×k` sub-cubes whose maximum value equals exactly `k`.

**Idea.** The maximum over a `k`-cube is the maximum of the eight `(k−1)`-cubes at its corners, because together they cover it. So `M_k = max of 8 shifted copies of M_{k−1}`, computed with NumPy. For each `k`, count the cells where `M_k == k`.

**Steps.**
1. `M_1` is the cube itself. Repeatedly take the 8-corner maximum, shrinking each dimension by 1.
2. Record `count(M_k == k)` for each `k`.

```python
import os

import numpy as np


def specialSubCubes(cube):
    n = round(len(cube) ** (1 / 3))
    cur = np.array(cube, dtype=np.int32).reshape(n, n, n)
    out = [int((cur == 1).sum())]
    for k in range(2, n + 1):
        cur = np.maximum.reduce([cur[dx:dx + n - k + 1, dy:dy + n - k + 1, dz:dz + n - k + 1]
                                 for dx in (0, 1) for dy in (0, 1) for dz in (0, 1)])
        out.append(int((cur == k).sum()))
    return out


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        n = int(input().strip())
        cube = list(map(int, input().split()))
        fptr.write(' '.join(map(str, specialSubCubes(cube))) + '\n')
    fptr.close()
```

**Watch out.** `n³` reaches 125 000, and recomputing each cube's maximum from scratch is O(n⁷). The corner trick reuses the previous level, so all `k` together cost O(n⁴). Use `round` for the cube root, because floating-point roots of perfect cubes can land just below the integer.

```stdin
2
2
2 1 1 1 1 1 1 1
2
1 1 1 1 2 1 1 2
```

```stdout
7 1
6 1
```

### Interval Selection

**Problem.** Choose as many intervals as possible such that no point is covered by three of them.

**Idea.** Greedy by right endpoint, tracking two numbers: `last`, the largest end among the chosen intervals, and `dbl`, the rightmost point already covered twice. A new interval `[a, b]` (with `b ≥` every chosen end) creates a triple overlap exactly when it reaches back over `dbl`, so accept it iff `a > dbl`. If it also overlaps the interval ending at `last` (`a ≤ last`), the doubly-covered region now extends to `last`.

**Steps.**
1. Sort by end. For each interval: if `a > dbl`, count it. Then set `dbl = last` if `a ≤ last`, and `last = b`.

```python
import os


def intervalSelection(intervals):
    dbl = last = 0
    count = 0
    for a, b in sorted(intervals, key=lambda iv: iv[1]):
        if a > dbl:
            count += 1
            if a <= last:
                dbl = last
            last = b
    return count


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    s = int(input().strip())
    for _ in range(s):
        n = int(input().strip())
        intervals = [list(map(int, input().split())) for _ in range(n)]
        fptr.write(str(intervalSelection(intervals)) + '\n')
    fptr.close()
```

**Watch out.**
- **Inclusive ends.** Intervals are closed, so `[1, 3]` and `[3, 6]` share the point 3.
- **The common mistake.** Tracking only "the last two ends" rejects intervals that start after the second-to-last end but don't actually form a triple. Tracking the doubly-covered point avoids that.

```stdin
4
3
1 2
2 3
2 4
3
1 5
1 5
1 5
4
1 10
1 3
4 6
7 10
4
1 10
1 3
3 6
7 10
```

```stdout
2
2
4
3
```

### String Reduction

**Problem.** Repeatedly replace two adjacent different letters (from `a`, `b`, `c`) with the third letter. Find the shortest possible final length.

**Idea.** Each operation changes every letter count by one, so the parities of the three counts all flip together. That gives the classic answer:
- if only one letter appears, nothing can be done (length `n`);
- else, if the three counts have the same parity, the best is 2;
- otherwise it is 1.

**Steps.**
1. Count the letters and apply the rule.

```python
import os


def stringReduction(s):
    counts = [s.count(c) for c in 'abc']
    if sum(1 for c in counts if c) == 1:
        return len(s)
    return 2 if len({c % 2 for c in counts}) == 1 else 1


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        fptr.write(str(stringReduction(input().strip())) + '\n')
    fptr.close()
```

**Watch out.** A DP over substrings also works and is the "intended" DP, but the parity invariant gives the answer in O(n). It was verified against exhaustive search on small strings.

```stdin
3
cab
bcab
ccccc
```

```stdout
2
1
5
```

### Far Vertices

**Problem.** Mark as few tree vertices as possible so that the unmarked ones are all within distance `K` of each other.

**Idea.** Keep the largest possible set of diameter ≤ `K`. In a tree such a set fits around a centre:
- **`K` even.** The centre is a vertex `c`; take every vertex within `K/2` of it.
- **`K` odd.** The centre is an edge `(u, v)`; take every vertex within `(K−1)/2` of `u` or of `v`.

Try every possible centre (n ≤ 100).

**Steps.**
1. All-pairs distances by BFS.
2. Find the largest kept set over the centres; the answer is `n − best`.

```python
import os
from collections import deque


def farVertices(n, k, edges):
    adj = [[] for _ in range(n + 1)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    dist = [[0] * (n + 1) for _ in range(n + 1)]
    for s in range(1, n + 1):
        d = [-1] * (n + 1)
        d[s] = 0
        queue = deque([s])
        while queue:
            x = queue.popleft()
            for y in adj[x]:
                if d[y] < 0:
                    d[y] = d[x] + 1
                    queue.append(y)
        dist[s] = d
    best = 1
    if k % 2 == 0:
        for c in range(1, n + 1):
            best = max(best, sum(1 for w in range(1, n + 1) if dist[c][w] <= k // 2))
    else:
        r = (k - 1) // 2
        for u, v in edges:
            best = max(best, sum(1 for w in range(1, n + 1) if min(dist[u][w], dist[v][w]) <= r))
    return n - best


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    edges = [list(map(int, input().split())) for _ in range(n - 1)]
    fptr.write(str(farVertices(n, k, edges)) + '\n')
    fptr.close()
```

**Watch out.** For odd `K`, centring on a vertex with radius `(K−1)/2` is too small, and radius `(K+1)/2` is too big; the edge centre is what's needed. Any two vertices kept around the centre are within `K`, because their paths pass through it.

```stdin
5 1
1 2
1 3
1 4
1 5
```

```stdout
3
```

### Counting Road Networks

**Problem.** Count the connected simple labelled graphs on `n` vertices, modulo 663224321, for `n` up to 10⁵.

**Idea.** Use exponential generating functions. All graphs have EGF `G(x) = Σ 2^C(n,2)·xⁿ/n!`. Every graph is a set of connected components, so the connected EGF is `C = ln G`. A power-series logarithm is `∫ G'/G`, which needs a power-series inverse: Newton iteration `B ← B(2 − G·B)`, which doubles the precision each round. The products use an exact FFT multiplication (3-way 10-bit split), which works for any modulus below 2³⁰.

**Steps.**
1. Compute `g_n = 2^(n(n−1)/2 mod (p−1)) / n!` modulo `p`.
2. Compute `C = ∫ (G' · G⁻¹)`; the answer for `n` is `n!·C[n]`.

```python
import sys

import numpy as np

MOD = 663224321


def mul(a, b, limit):
    """(a*b) mod MOD truncated to `limit` terms; exact via 3-way 10-bit split FFT."""
    a, b = a[:limit], b[:limit]
    need = min(len(a) + len(b) - 1, limit)
    size = 1
    while size < len(a) + len(b) - 1:
        size *= 2
    pa = [np.fft.rfft((a >> (10 * i)) & 1023, size) for i in range(3)]
    pb = [np.fft.rfft((b >> (10 * i)) & 1023, size) for i in range(3)]
    res = np.zeros(need, dtype=np.int64)
    for s in range(5):
        acc = sum(pa[i] * pb[s - i] for i in range(3) if 0 <= s - i < 3)
        part = np.rint(np.fft.irfft(acc, size)[:need]).astype(np.int64) % MOD
        res = (res + part * pow(2, 10 * s, MOD)) % MOD
    return res


def inverse(g, n):
    b = np.array([pow(int(g[0]), MOD - 2, MOD)], dtype=np.int64)
    length = 1
    while length < n:
        length *= 2
        gb = mul(g, b, length)
        two_minus = (-gb) % MOD
        two_minus[0] = (two_minus[0] + 2) % MOD
        b = mul(b, two_minus, length)
    return b[:n]


def main():
    data = sys.stdin.read().split()
    q = int(data[0])
    ns = list(map(int, data[1:1 + q]))
    top = max(ns) + 1
    fact = [1] * (top + 1)
    for i in range(1, top + 1):
        fact[i] = fact[i - 1] * i % MOD
    inv_fact = [pow(f, MOD - 2, MOD) for f in fact]
    g = np.array([pow(2, (i * (i - 1) // 2) % (MOD - 1), MOD) * inv_fact[i] % MOD for i in range(top)],
                 dtype=np.int64)
    deriv = np.array([(i + 1) * int(g[i + 1]) % MOD for i in range(top - 1)] + [0], dtype=np.int64)
    quotient = mul(deriv, inverse(g, top), top)          # C' = G'/G
    out = []
    for n in ns:
        c_n = int(quotient[n - 1]) * pow(n, MOD - 2, MOD) % MOD   # integrate
        out.append(c_n * fact[n] % MOD)
    print('\n'.join(map(str, out)))


main()
```

**Watch out.** The O(n²) recurrence (subtracting the graphs whose vertex 1 lies in a smaller component) is 10¹⁰ steps at n = 10⁵. Reduce the exponent `C(n,2)` modulo `p − 1` (Fermat) before `pow` to keep it small.

```stdin
3
1
3
10
```

```stdout
1
4
201986643
```

### Superman Celebrates Diwali

**Problem.** Superman drops from the top of `N` buildings of height `H`. He may step down one floor within a building, or jump to any other building, losing `I` floors. Maximise the people collected on the floors he visits.

**Idea.** Floor-by-floor DP from the top. `best[h][b]` = the most people collected arriving at floor `h` of building `b`. He arrives either from floor `h+1` of the same building or by a jump from *any* building at floor `h+I`, so only the per-floor maximum `top[h+I]` matters. Each floor is one vectorised update over all buildings.

**Steps.**
1. `cnt[b][h]` = people per floor. Going from `h = H` down to 1: `best[h] = cnt[:, h] + max(best[h+1], top[h+I])`, where `top[h] = max(best[h])`.
2. Return `max(top)`.

```python
import sys

import numpy as np


def main():
    data = sys.stdin.read().split()
    n, height, drop = int(data[0]), int(data[1]), int(data[2])
    cnt = np.zeros((height + 2, n), dtype=np.int64)
    pos = 3
    for b in range(n):
        u = int(data[pos]); pos += 1
        for f in data[pos:pos + u]:
            cnt[int(f), b] += 1
        pos += u
    best = np.zeros((height + 2, n), dtype=np.int64)
    top = np.zeros(height + 2 + drop, dtype=np.int64)
    for h in range(height, 0, -1):
        from_jump = top[h + drop] if h + drop <= height else 0
        best[h] = cnt[h] + np.maximum(best[h + 1], from_jump)
        top[h] = best[h].max()
    print(int(top[1:height + 1].max()))


main()
```

**Watch out.** A jump to the *same* building is never useful, so `top` may safely include it. Several people can share a floor, so the counts are accumulated with `+=`, not set.

```stdin
4 15 2
5 1 1 1 4 10
8 9 5 7 7 3 9 8 8
5 9 5 6 4 3
0
```

```stdout
12
```
