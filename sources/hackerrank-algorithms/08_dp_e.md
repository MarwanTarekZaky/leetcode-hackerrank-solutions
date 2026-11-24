## Dynamic Programming

### Hexagonal Grid

**Problem.** A 2-row hexagonal grid (`a_i` adjacent to `a_{i+1}`, `b_i`, and `b_i` adjacent to `a_{i+1}`, `b_{i+1}`) has some black cells. Can the free cells be tiled with dominoes?

**Idea.** There are at most 20 cells, numbered in the order `a_1, b_1, a_2, b_2, …`. Use memoised backtracking on the bitmask of covered cells. Always cover the *first* uncovered free cell, pairing it with one of its later neighbours; that fixes an order and avoids duplicate work.
- `a_i` pairs with `b_i` or `a_{i+1}`.
- `b_i` pairs with `a_{i+1}` or `b_{i+1}`.

**Steps.**
1. Mark black cells as already covered.
2. `ok(mask)`: if all cells are covered, return true. Otherwise take the first free cell and try its later free neighbours.

```python
import os
from functools import lru_cache


def hexagonalGrid(a, b):
    n = len(a)
    full = (1 << (2 * n)) - 1
    start = 0
    for i in range(n):
        if a[i] == '1':
            start |= 1 << (2 * i)
        if b[i] == '1':
            start |= 1 << (2 * i + 1)

    @lru_cache(maxsize=None)
    def ok(mask):
        if mask == full:
            return True
        cell = (~mask & (mask + 1)).bit_length() - 1
        i, row = divmod(cell, 2)
        partners = [2 * i + 1, 2 * i + 2] if row == 0 else [2 * i + 2, 2 * i + 3]
        for p in partners:
            if p < 2 * n and not mask >> p & 1 and ok(mask | 1 << cell | 1 << p):
                return True
        return False

    return 'YES' if ok(start) else 'NO'


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n = int(input().strip())
        a = input().strip()
        b = input().strip()
        fptr.write(hexagonalGrid(a, b) + '\n')
    fptr.close()
```

**Watch out.** The `a_i`–`b_{i-1}` link is the diagonal `b_{i−1} → a_i`, so it appears as a partner of `b`, not of `a`. Order the cells column by column so that "first free cell" works.

```stdin
6
6
010000
000010
2
00
00
2
00
10
2
00
01
2
00
11
2
10
00
```

```stdout
YES
YES
NO
NO
YES
NO
```

### Queens on Board

**Problem.** Count the non-empty sets of non-attacking queens on an `N × M` board (`M ≤ 5`) with blocked squares that stop attacks, modulo 10⁹+7.

**Idea.** Row-by-row DP. The state is three bitmasks of the attacks entering the current row: vertical, down-left diagonal and down-right diagonal. A blocked cell absorbs any attack reaching it. In each row, choose a subset of free cells that is not attacked and has no two queens on an unblocked stretch of the same row. Pass the attacks on: vertical stays, the diagonals shift by one.

**Steps.**
1. For each row, precompute the valid subsets with respect to the row's blocks.
2. For each state, mask the incoming attacks with the free cells, then try every subset that avoids them.
3. Sum all final states and subtract 1 for the empty placement.

```python
import os

MOD = 10 ** 9 + 7


def queensBoard(board):
    m = len(board[0])
    full = (1 << m) - 1
    states = {(0, 0, 0): 1}
    for row in board:
        free = sum(1 << c for c in range(m) if row[c] == '.')
        subsets = []
        for s in range(1 << m):
            if s & ~free:
                continue
            ok, seen = True, False
            for c in range(m):
                if not free >> c & 1:
                    seen = False
                elif s >> c & 1:
                    if seen:
                        ok = False
                        break
                    seen = True
            if ok:
                subsets.append(s)
        nxt = {}
        for (v, dl, dr), ways in states.items():
            v, dl, dr = v & free, dl & free, dr & free
            attacked = v | dl | dr
            for s in subsets:
                if s & attacked:
                    continue
                key = (v | s, (dl | s) >> 1, ((dr | s) << 1) & full)
                nxt[key] = (nxt.get(key, 0) + ways) % MOD
        states = nxt
    return (sum(states.values()) - 1) % MOD


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n, m = map(int, input().split())
        board = [input().strip() for _ in range(n)]
        fptr.write(str(queensBoard(board)) + '\n')
    fptr.close()
```

**Watch out.** Attacks must be masked by the current row's free cells *before* checking. That is how a `#` stops a line of attack. The empty placement is excluded ("one or more queens").

```stdin
4
3 3
...
...
...
3 3
.#.
.#.
...
2 4
.#..
....
1 1
#
```

```stdout
17
18
14
0
```

### Shashank and the Palindromic Strings

**Problem.** Pick a non-empty subsequence from each string such that their concatenation is a palindrome. Count the ways (by positions), modulo 10⁹+7.

**Idea.** Join the strings into one array of characters with segment ids. A palindromic subsequence is a nest of matching pairs (plus possibly one middle character). It must touch every segment, so between consecutive chosen positions no whole segment may be skipped.
- **Interval DP.** Let `g(i, j)` count the palindromic choices whose outermost characters are exactly `i` and `j`, with nothing skipped in between. Then `g(i, j) = [s_i = s_j]·(base + Σ g(i', j'))`, where the next pair `(i', j')` stays within one segment of `i` on the left and of `j` on the right.
- **Fast sums.** Keep `T(x, y)` = the sum of `g` over all intervals inside `[x, y]`. Each rectangle of `(i', j')` values is then an O(1) inclusion–exclusion.

**Steps.**
1. Fill `g` and `T` by increasing interval length.
2. The answer sums `g(i, j)` over `i` in the first segment and `j` in the last.

```python
import os

MOD = 10 ** 9 + 7


def palindromicStrings(a):
    s, seg = [], []
    for k, w in enumerate(a):
        s.extend(w)
        seg.extend([k] * len(w))
    n = len(s)
    nseg = len(a)
    first = [0] * nseg
    last = [0] * nseg
    pos = 0
    for k, w in enumerate(a):
        first[k], last[k] = pos, pos + len(w) - 1
        pos += len(w)
    g = [[0] * n for _ in range(n)]
    T = [[0] * (n + 1) for _ in range(n + 1)]       # T[x][y] for x <= y, 0 otherwise

    def tsum(x, y):
        return T[x][y] if 0 <= x <= y < n else 0

    for length in range(1, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j]:
                if i == j:
                    val = 1
                else:
                    val = 1 if seg[j] - seg[i] <= 1 else 0
                    x1 = i + 1
                    x2 = min(j - 1, last[min(seg[i] + 1, nseg - 1)])
                    y1 = max(i + 1, first[max(seg[j] - 1, 0)])
                    y2 = j - 1
                    if x1 <= x2 and y1 <= y2:
                        val += (tsum(x1, y2) - tsum(x2 + 1, y2) - tsum(x1, y1 - 1) + tsum(x2 + 1, y1 - 1))
                    val %= MOD
                g[i][j] = val
            T[i][j] = (g[i][j] + tsum(i + 1, j) + tsum(i, j - 1) - tsum(i + 1, j - 1)) % MOD
    total = 0
    for i in range(first[0], last[0] + 1):
        for j in range(first[-1], last[-1] + 1):
            if i <= j:
                total += g[i][j]
    return total % MOD


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        n = int(input().strip())
        a = [input().strip() for _ in range(n)]
        fptr.write(str(palindromicStrings(a)) + '\n')
    fptr.close()
```

**Watch out.**
- **What "touching every segment" means.** It is a constraint between *consecutive* chosen positions: the next pair may advance by at most one segment on each side.
- **The base term.** "Nothing inside" is valid only if the outer pair already spans at most two adjacent segments.
- **Speed.** About `L²/2 = 5·10⁵` states for `L = 1000`.

```stdin
3
3
aa
b
aa
3
a
b
c
2
abc
abc
```

```stdout
5
0
9
```

### Points in a Plane

**Problem.** Remove all `N ≤ 16` points in as few turns as possible, each turn removing a collinear subset. Count the ways to do it in that many turns, where turns are ordered.

**Idea.** Bitmask DP.
- **Minimum turns.** `best[mask]` comes from always removing the lowest point together with its whole line inside the mask. Removing more points never hurts, so full lines give the minimum.
- **Counting.** Count *unordered* partitions into `best` collinear blocks. The block containing the lowest point `p` may be `{p}` alone or `p` plus any non-empty subset of one line through `p`, as long as the remaining mask still needs exactly `best − 1` turns. Then multiply by `T!` for the order of the turns.

**Steps.**
1. Precompute, for each pair, the bitmask of all points on their line.
2. Fill `best[]` bottom-up, then count top-down with memoisation, keeping only optimal transitions.

```python
import os
from functools import lru_cache
from math import factorial

MOD = 10 ** 9 + 7


def pointsInPlane(coordinates):
    n = len(coordinates)
    pts = coordinates
    line = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                (x1, y1), (x2, y2) = pts[i], pts[j]
                line[i][j] = sum(1 << k for k in range(n)
                                 if (x2 - x1) * (pts[k][1] - y1) == (y2 - y1) * (pts[k][0] - x1))
    full = (1 << n) - 1
    best = [0] * (full + 1)
    for mask in range(1, full + 1):
        p = (mask & -mask).bit_length() - 1
        rest = mask & ~(1 << p)
        b = best[rest] + 1
        q_mask = rest
        while q_mask:
            q = (q_mask & -q_mask).bit_length() - 1
            q_mask &= q_mask - 1
            b = min(b, best[mask & ~line[p][q]] + 1)
        best[mask] = b

    @lru_cache(maxsize=None)
    def ways(mask):
        if mask == 0:
            return 1
        p = (mask & -mask).bit_length() - 1
        rest = mask & ~(1 << p)
        need = best[mask] - 1
        total = ways(rest) if best[rest] == need else 0
        done_lines = set()
        q_mask = rest
        while q_mask:
            q = (q_mask & -q_mask).bit_length() - 1
            q_mask &= q_mask - 1
            on_line = line[p][q] & rest
            if on_line in done_lines:
                continue
            done_lines.add(on_line)
            sub = on_line
            while sub:                       # every non-empty subset of this line (with p)
                if best[mask & ~sub & ~(1 << p)] == need:
                    total += ways(mask & ~sub & ~(1 << p))
                sub = (sub - 1) & on_line
        return total % MOD

    t = best[full]
    return [t, ways(full) * factorial(t) % MOD]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n = int(input().strip())
        coordinates = [list(map(int, input().split())) for _ in range(n)]
        fptr.write(' '.join(map(str, pointsInPlane(coordinates))) + '\n')
    fptr.close()
```

**Watch out.** Each line through `p` must be handled once, even though every point on it generates it again, hence `done_lines`. Partial lines matter for counting: a point on two lines can be removed in either turn.

```stdin
2
3
0 0
0 1
1 0
4
3 4
3 5
3 6
5 5
```

```stdout
2 6
2 8
```

### Turn Off the Lights

**Problem.** Pressing button `i` toggles every bulb within distance `k`. All bulbs start on. Find the cheapest set of presses that turns them all off.

**Idea.** Some press must cover bulb 0, so the first press `s` lies in `[0, k]`. Then bulb `s + k + 1` can only be switched by a press at exactly `s + 2k + 1`, and so on: the presses are forced, `s, s + (2k+1), s + 2(2k+1), …`. Each bulb is toggled exactly once. A start `s` is valid if its last press reaches bulb `n − 1`. Try every `s`.

**Steps.**
1. For `s` in `0..min(k, n−1)`: sum `c` at `s, s + 2k + 1, …`. Keep it if `last + k ≥ n − 1`.
2. Return the minimum.

```python
import os


def turnOffTheLights(k, c):
    n = len(c)
    step = 2 * k + 1
    best = None
    for s in range(min(k, n - 1) + 1):
        presses = range(s, n, step)
        if presses[-1] + k >= n - 1:
            cost = sum(c[p] for p in presses)
            best = cost if best is None else min(best, cost)
    return best


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    c = list(map(int, input().split()))
    fptr.write(str(turnOffTheLights(k, c)) + '\n')
    fptr.close()
```

**Watch out.** Pressing overlapping buttons would toggle some bulbs twice and turn them back on, so the presses must tile the line exactly. That is why the pattern is forced.

```stdin
3 1
1 1 1
```

```stdout
1
```

### Animal Transport

**Problem.** Visit zoos `1..m` in order, carrying animals from source to destination. Elephants and dogs, dogs and cats, cats and mice, and mice and elephants can't ride together. For each `x`, report the smallest zoo by which `x` animals can be delivered.

**Idea.** The conflicts form a 4-cycle E–D–C–M, so the truck always carries either only `{E, C}` or only `{D, M}`. The trip splits into segments, each serving one group.
- **The DP.** `dp[z]` = the most animals delivered by zoo `z`. Then `dp[z] = max(dp[z−1], max over y, group g of dp[y] + #g-animals with y ≤ s < d ≤ z)`.
- **Speed.** Keep one segment tree per group, holding `dp[y] + count(y)`. When animals with destination `z` appear, add 1 on `[1, s]`; a max query then gives the best `y`.

**Steps.**
1. For `z = 1..m`: range-add the animals arriving at `z` (only `s < d` animals count), query both trees on `[1, z−1]`, set `dp[z]`, and write `dp[z]` at position `z` in both trees.
2. `dp` is non-decreasing, so for each `x` the answer is the first `z` with `dp[z] ≥ x`, or -1.

```python
import os


class MaxTree:
    """Range add, range max over positions 1..n."""

    def __init__(self, n):
        self.size = 1
        while self.size < n + 1:
            self.size *= 2
        self.mx = [-10 ** 9] * (2 * self.size)
        self.lz = [0] * (2 * self.size)

    def _apply(self, node, v):
        self.mx[node] += v
        self.lz[node] += v

    def _push(self, node):
        if self.lz[node]:
            self._apply(2 * node, self.lz[node])
            self._apply(2 * node + 1, self.lz[node])
            self.lz[node] = 0

    def add(self, l, r, v, node=1, lo=0, hi=None):
        if hi is None:
            hi = self.size - 1
        if r < lo or hi < l:
            return
        if l <= lo and hi <= r:
            self._apply(node, v)
            return
        self._push(node)
        mid = (lo + hi) // 2
        self.add(l, r, v, 2 * node, lo, mid)
        self.add(l, r, v, 2 * node + 1, mid + 1, hi)
        self.mx[node] = max(self.mx[2 * node], self.mx[2 * node + 1])

    def query(self, l, r, node=1, lo=0, hi=None):
        if hi is None:
            hi = self.size - 1
        if r < lo or hi < l:
            return -10 ** 9
        if l <= lo and hi <= r:
            return self.mx[node]
        self._push(node)
        mid = (lo + hi) // 2
        return max(self.query(l, r, 2 * node, lo, mid), self.query(l, r, 2 * node + 1, mid + 1, hi))

    def set(self, pos, v, node=1, lo=0, hi=None):
        if hi is None:
            hi = self.size - 1
        if lo == hi:
            self.mx[node] = v
            self.lz[node] = 0
            return
        self._push(node)
        mid = (lo + hi) // 2
        if pos <= mid:
            self.set(pos, v, 2 * node, lo, mid)
        else:
            self.set(pos, v, 2 * node + 1, mid + 1, hi)
        self.mx[node] = max(self.mx[2 * node], self.mx[2 * node + 1])


def minimumZooNumbers(m, n, t, s, d):
    group = {'E': 0, 'C': 0, 'D': 1, 'M': 1}
    by_dest = [[] for _ in range(m + 1)]
    for ti, si, di in zip(t, s, d):
        if si < di:
            by_dest[di].append((group[ti], si))
    trees = [MaxTree(m), MaxTree(m)]
    dp = [0] * (m + 1)
    for tr in trees:
        tr.set(1, 0)
    for z in range(2, m + 1):
        for g, si in by_dest[z]:
            trees[g].add(1, si, 1)
        dp[z] = max(dp[z - 1], trees[0].query(1, z - 1), trees[1].query(1, z - 1))
        for tr in trees:
            tr.set(z, dp[z])
    out, z = [], 1
    for x in range(1, n + 1):
        while z <= m and dp[z] < x:
            z += 1
        out.append(z if z <= m else -1)
    return out


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    cases = int(input().strip())
    for _ in range(cases):
        m, n = map(int, input().split())
        t = input().split()
        s = list(map(int, input().split()))
        d = list(map(int, input().split()))
        fptr.write(' '.join(map(str, minimumZooNumbers(m, n, t, s, d))) + '\n')
    fptr.close()
```

**Watch out.**
- **Backward animals.** An animal with `s > d` can never be delivered, because zoos are visited in increasing order.
- **Shared boundary zoo.** At a zoo where one group's segment ends and the next begins, the old group is unloaded before the new one is loaded. That is why a segment may start at `y = dp`'s own zoo.

```stdin
2
10 3
E D C
4 1 4
7 5 8
10 6
E D C M E D
1 1 1 2 9 7
2 2 2 4 10 10
```

```stdout
5 8 -1
2 2 4 10 -1 -1
```

### The Indian Job

**Problem.** Each robber needs `A[i]` continuous minutes in the vault, at most two people may be inside at once, and everything must finish within `G` minutes. Is it possible?

**Idea.** At most two people at a time means two "lanes", and each robber's stay goes in one lane. So the robbers must split into two groups whose totals are both ≤ `G`. That is a subset sum: some subset sum `x` must satisfy `total − G ≤ x ≤ G`. A Python-int bitset gives all reachable sums.

**Steps.**
1. `bits` = the reachable subset sums (shift-or for each `A[i]`).
2. Answer `YES` if any sum in `[max(0, total − G), G]` is reachable.

```python
import sys


def indianJob(g, arr):
    total = sum(arr)
    if total > 2 * g:
        return 'NO'
    bits = 1
    for x in arr:
        bits |= bits << x
    lo = max(0, total - g)
    window = (bits >> lo) & ((1 << (g - lo + 1)) - 1) if g >= lo else 0
    return 'YES' if window else 'NO'


def main():
    data = sys.stdin.read().split()
    t = int(data[0])
    pos = 1
    out = []
    for _ in range(t):
        n, g = int(data[pos]), int(data[pos + 1])
        arr = list(map(int, data[pos + 2:pos + 2 + n]))
        pos += 2 + n
        out.append(indianJob(g, arr))
    print('\n'.join(out))


main()
```

**Watch out.** HackerRank's Python starter for this one is broken (`indianJob = g(arr)`), so the program parses the input itself. Touching endpoints are allowed, which is what makes a lane simply a sum.

```stdin
2
3 4
2 4 2
3 2
2 4 2
```

```stdout
YES
NO
```

### Requirement

**Problem.** Assign each of `n < 14` variables a digit 0–9 so that the given constraints `x ≤ y` hold. Count the assignments modulo 1007.

**Idea.** Look at the sets `M_v` = the variables with value ≤ `v`. They form a chain `∅ ⊆ M_0 ⊆ … ⊆ M_9 = all`. Each `M_v` must be *closed*: if `y` is in it, so is every `x` with `x ≤ y`. Counting assignments means counting such chains. Each level is a subset-sum (zeta) transform over masks, followed by zeroing the non-closed masks: `dp_v[M] = Σ_{M' ⊆ M} dp_{v−1}[M']`.

**Steps.**
1. Precompute `closed[mask]` from the predecessor masks.
2. Start from `dp = [1 at ∅]`. Ten times: zeta transform, then zero the non-closed masks.
3. Return `dp[full]`.

```python
import os

import numpy as np


def requirement(n, req):
    size = 1 << n
    preds = [0] * n
    for x, y in req:
        preds[y] |= 1 << x
    closed = np.array([all(not (mask >> y & 1) or (preds[y] & ~mask) == 0 for y in range(n))
                       for mask in range(size)])
    idx = np.arange(size)
    dp = np.zeros(size, dtype=np.int64)
    dp[0] = 1
    for _ in range(10):
        for b in range(n):
            has = (idx >> b) & 1 == 1
            dp[has] = (dp[has] + dp[idx[has] ^ (1 << b)]) % 1007
        dp[~closed] = 0
    return int(dp[size - 1])


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m = map(int, input().split())
    req = [list(map(int, input().split())) for _ in range(m)]
    fptr.write(str(requirement(n, req)) + '\n')
    fptr.close()
```

**Watch out.** Cyclic constraints (`x ≤ y` and `y ≤ x`) simply force equal values, and closure handles them automatically. Enumerating 10¹³ assignments is impossible, whereas the zeta transform costs `10·n·2ⁿ`.

```stdin
6 7
1 3
0 1
2 4
0 4
2 5
3 4
0 2
```

```stdout
1000
```

### A Super Hero

**Problem.** At each level, kill one enemy with power `P`. The bullets taken from the enemy you killed at the previous level can be used only at this level; starting bullets last forever. Find the minimum number of starting bullets.

**Idea.** At level `i`, after killing enemy `k` at level `i−1`, killing enemy `j` costs `max(0, P_j − B_k)` starting bullets. So `dp_i[j] = min_k(dp[k] + max(0, P_j − B_k))`. Values are at most 1000, so bucket the previous enemies by `B`:
- enemies with `B ≥ P_j` cost `dp[k]`, so take a suffix minimum;
- the others cost `dp[k] − B_k + P_j`, so take a prefix minimum of `dp[k] − B_k`.

That makes each level O(M + 1000).

**Steps.**
1. `dp_0[j] = P_0[j]`.
2. For each next level, build `byB[b] = min dp over enemies with B = b` and its prefix and suffix minima, then compute `dp` for every enemy.
3. Return `min(dp)`.

```python
import os

import numpy as np

MAXV = 1001


def superHero(power, bullets):
    dp = np.array(power[0], dtype=np.int64)
    big = 10 ** 15
    for i in range(1, len(power)):
        prev_b = np.array(bullets[i - 1], dtype=np.int64)
        by_b = np.full(MAXV + 1, big, dtype=np.int64)
        np.minimum.at(by_b, prev_b, dp)
        suffix = np.minimum.accumulate(by_b[::-1])[::-1]                 # min dp with B >= p
        minus = np.where(by_b < big, by_b - np.arange(MAXV + 1), big)
        prefix = np.concatenate(([big], np.minimum.accumulate(minus)[:-1]))  # min dp-B with B < p
        p = np.array(power[i], dtype=np.int64)
        dp = np.minimum(suffix[p], prefix[p] + p)
    return int(dp.min())


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n, m = map(int, input().split())
        power = [list(map(int, input().split())) for _ in range(n)]
        bullets = [list(map(int, input().split())) for _ in range(n)]
        fptr.write(str(superHero(power, bullets)) + '\n')
    fptr.close()
```

**Watch out.** The O(M²) transition is 2.5·10¹¹ steps at the limit, so the value bucketing is essential. Leftover bullets from the previous enemy are lost, which is exactly why the cost is `max(0, …)`.

```stdin
2
3 3
3 2 1
1 2 3
3 2 1
1 2 3
3 2 1
1 2 3
3 3
3 2 5
8 9 1
4 7 6
1 1 1
1 1 1
1 1 1
```

```stdout
1
5
```

### Clues on a Binary Path

**Problem.** Count the distinct binary strings of length `d` that some walk of `d` edges from house 1 produces (each edge is labelled 0 or 1).

**Idea.** Run the subset construction on the fly. The state after reading a prefix is the **set** of houses where some walk with that label sequence can end. Merge equal sets and count the prefixes mapping to each. Every string with a non-empty reachable set is realisable, so after `d` steps sum the counts. Sets are Python-int bitmasks, and per-house neighbour masks for each label make the steps cheap.

**Steps.**
1. `nb[c][u]` = the mask of houses reachable from `u` by a `c`-edge.
2. Start with `{1}` and repeat `d` times: every state branches on 0 and 1 to the union of its members' masks. Drop empty sets and merge equal ones.

```python
import os


def cluesOnBinaryPath(n, d, roads):
    nb = [[0] * (n + 1) for _ in range(2)]
    for u, v, c in roads:
        nb[c][u] |= 1 << v
        nb[c][v] |= 1 << u
    states = {1 << 1: 1}
    cache = {}

    def step(mask, c):
        key = (mask, c)
        if key not in cache:
            out, m = 0, mask
            while m:
                low = m & -m
                out |= nb[c][low.bit_length() - 1]
                m ^= low
            cache[key] = out
        return cache[key]

    for _ in range(d):
        nxt = {}
        for mask, cnt in states.items():
            for c in (0, 1):
                new = step(mask, c)
                if new:
                    nxt[new] = nxt.get(new, 0) + cnt
        states = nxt
    return sum(states.values())


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m, d = map(int, input().split())
    roads = [list(map(int, input().split())) for _ in range(m)]
    fptr.write(str(cluesOnBinaryPath(n, d, roads)) + '\n')
    fptr.close()
```

**Watch out.** Counting walks would count the same label string many times. Grouping prefixes by their reachable *set* is what turns "distinct strings" into a simple sum. Self-loops and parallel edges just set bits.

```stdin
3 2 3
1 2 0
1 3 1
```

```stdout
4
```

### Road Maintenance

**Problem.** Count the sets of exactly `M ≤ 5` edge-disjoint paths (each with at least one edge) in a tree, modulo 10⁹+7.

**Idea.** Tree DP with two states per node: is the edge to the parent used by an open path (`up = 1`) or not, and how many paths `j ≤ M` are already complete inside the subtree.
- **Merging children.** Keep a table over `(j, k)`, where `k` is the number of child edges carrying an open path into `v`. A used child edge contributes one more open end.
- **Resolving the ends at `v`.** The `k` open ends can pair up through `v` (`(2p−1)!!` ways for `p` pairs), end at `v`, or have one continue upward. Alternatively, a brand-new path can start at `v` and go up. Since `j ≤ 5`, `k` never exceeds 11.

**Steps.**
1. Process children before parents and merge them with NumPy row shifts.
2. For each `(j, k)`, enumerate `u ∈ {0, 1}` (one end continues up) and the number of pairs `p`; the rest end at `v`. Also add the "new path starting at `v`" option.
3. The answer is `up = 0` at the root with `j = M`.

```python
import os
from collections import deque
from math import comb

import numpy as np

MOD = 10 ** 9 + 7


def roadMaintenance(n, m, edges):
    adj = [[] for _ in range(n + 1)]
    for a, b in edges:
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
    K = 2 * m + 2
    dfact = [1] * (K + 1)                 # (2p-1)!!
    for p in range(1, K + 1):
        dfact[p] = dfact[p - 1] * (2 * p - 1) % MOD
    down = [None] * (n + 1)               # down[v] = (no_up[j], up[j]) arrays of length m+1
    tables = {}
    for v in reversed(order):
        table = tables.pop(v, None)
        if table is None:
            table = np.zeros((m + 1, K + 1), dtype=np.int64)
            table[0, 0] = 1
        no_up = np.zeros(m + 1, dtype=np.int64)
        up = np.zeros(m + 1, dtype=np.int64)
        for j in range(m + 1):
            for k in range(K + 1):
                ways = int(table[j, k])
                if not ways:
                    continue
                for u in (0, 1):
                    if u > k:
                        continue
                    rest = k - u
                    for p in range(rest // 2 + 1):
                        done = j + p + (rest - 2 * p)
                        if done > m:
                            continue
                        w = ways * comb(k, u) % MOD * comb(rest, 2 * p) % MOD * dfact[p] % MOD
                        if u:
                            up[done] = (up[done] + w) % MOD
                        else:
                            no_up[done] = (no_up[done] + w) % MOD
                            up[done] = (up[done] + w) % MOD     # new path starts at v going up
        down[v] = (no_up, up)
        p_ = parent[v]
        if p_:
            pt = tables.get(p_)
            if pt is None:
                pt = np.zeros((m + 1, K + 1), dtype=np.int64)
                pt[0, 0] = 1
            new = np.zeros_like(pt)
            for jj in range(m + 1):
                a, b = int(no_up[jj]), int(up[jj])
                if a:
                    new[jj:, :] = (new[jj:, :] + pt[:m + 1 - jj, :] * a) % MOD
                if b:
                    new[jj:, 1:] = (new[jj:, 1:] + pt[:m + 1 - jj, :-1] * b) % MOD
            tables[p_] = new
    return int(down[1][0][m])


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m = map(int, input().split())
    edges = [list(map(int, input().split())) for _ in range(n - 1)]
    fptr.write(str(roadMaintenance(n, m, edges)) + '\n')
    fptr.close()
```

**Watch out.**
- **Counting the ends.** An open end that stops at `v` still completes a path of at least one edge, so it counts. The "new path from `v` upward" option exists only when no child's path continues up.
- **Keeping it small.** Capping `j` at `M` keeps every table tiny (6 × 12).

```stdin
4 2
1 2
2 3
2 4
```

```stdout
6
```

### Billboards

**Problem.** Remove billboards so that no more than `k` consecutive ones remain, maximising the revenue left standing.

**Idea.** Minimise the revenue *removed* instead. Every window of `k + 1` consecutive billboards must contain a removed one. Let `dp[i]` be the cheapest removal set whose last removal is billboard `i`; the previous removal lies within `k + 1` positions. A sliding-window minimum (monotonic deque) makes it O(n). Add virtual removals of cost 0 at both ends.

**Steps.**
1. `dp[-1] = 0`. For `i = 0..n` (where `n` is the virtual end): `dp[i] = cost[i] + min(dp[i−k−1 .. i−1])`.
2. The answer is `total − dp[n]`.

```python
import os
from collections import deque


def billboards(k, revenue):
    n = len(revenue)
    cost = revenue + [0]                  # virtual billboard n with cost 0
    dp = [0] * (n + 1)
    window = deque([(-1, 0)])             # (index, dp) with increasing dp
    for i in range(n + 1):
        while window[0][0] < i - k - 1:
            window.popleft()
        dp[i] = cost[i] + window[0][1]
        while window and window[-1][1] >= dp[i]:
            window.pop()
        window.append((i, dp[i]))
    return sum(revenue) - dp[n]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    revenue = [int(input().strip()) for _ in range(n)]
    fptr.write(str(billboards(k, revenue)) + '\n')
    fptr.close()
```

**Watch out.** A direct DP over "number of consecutive billboards kept" costs O(n·k), up to 10¹⁰. The removal view with a monotonic deque is linear.

```stdin
6 2
1
2
3
1
6
10
```

```stdout
21
```
