## Dynamic Programming

### Beautiful Strings

**Problem.** Count the distinct strings obtained by deleting exactly two characters from `S` (|S| up to 10⁶).

**Idea.** Compress `S` into runs of equal letters; say there are `r` of them. Deleting any character of a run gives the same result, so a deletion is really a choice of *run*.
- **Different runs.** Deleting from two different runs gives `C(r, 2)` candidates.
- **Same run.** Deleting two characters from one run is possible for each run of length ≥ 2.
- **Collisions.** Two candidates coincide exactly in a pattern `x y x` where the middle run `y` has length 1. There, deleting "`y` and the left `x`" equals deleting "`y` and the right `x`".

So the answer is `C(r, 2) + #(runs of length ≥ 2) − #(length-1 runs whose two neighbours have the same letter)`.

**Steps.**
1. Build the run letters and run lengths.
2. Apply the formula.

```python
import os
from itertools import groupby


def beautifulStrings(s):
    runs = [(ch, len(list(g))) for ch, g in groupby(s)]
    r = len(runs)
    total = r * (r - 1) // 2 + sum(1 for _, length in runs if length >= 2)
    for i in range(1, r - 1):
        if runs[i][1] == 1 and runs[i - 1][0] == runs[i + 1][0]:
            total -= 1
    return total


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    s = input().strip()
    fptr.write(str(beautifulStrings(s)) + '\n')
    fptr.close()
```

**Watch out.** Building all `C(n, 2)` strings is impossible for 10⁶ characters. The formula was checked against brute force on random small strings.

```stdin
abba
```

```stdout
4
```

### Covering the stains

**Problem.** Remove exactly `K` stains so that the bounding box of the rest has a strictly smaller area. Count the ways (modulo 10⁹+7).

**Idea.** The area shrinks exactly when at least one side of the box moves inward, which means the removed set contains *every* stain lying on that side. (If the box already has zero area, nothing can shrink it, so the answer is 0.) Count with inclusion–exclusion over the four sides. For a set of sides with union `U` of boundary stains, the removals that contain all of `U` number `C(N − |U|, K − |U|)`.

**Steps.**
1. Find the four boundary sets (as index sets).
2. Sum `(−1)^{|S|+1}·C(N − |U_S|, K − |U_S|)` over the 15 non-empty side subsets `S`.

```python
import os
from math import comb

MOD = 10 ** 9 + 7


def coveringStains(k, coordinates):
    n = len(coordinates)
    xs = [x for x, _ in coordinates]
    ys = [y for _, y in coordinates]
    if (max(xs) - min(xs)) * (max(ys) - min(ys)) == 0:
        return 0
    sides = [
        {i for i in range(n) if xs[i] == min(xs)},
        {i for i in range(n) if xs[i] == max(xs)},
        {i for i in range(n) if ys[i] == min(ys)},
        {i for i in range(n) if ys[i] == max(ys)},
    ]
    total = 0
    for mask in range(1, 16):
        union = set()
        for b in range(4):
            if mask >> b & 1:
                union |= sides[b]
        u = len(union)
        if u <= k:
            term = comb(n - u, k - u)
            total += term if bin(mask).count('1') % 2 else -term
    return total % MOD


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    coordinates = [list(map(int, input().split())) for _ in range(n)]
    fptr.write(str(coveringStains(k, coordinates)) + '\n')
    fptr.close()
```

**Watch out.** A corner stain belongs to two sides at once. That is why the inclusion–exclusion uses the *union* of the chosen sides, not the sum of their sizes.

```stdin
5 2
0 1
3 3
2 0
0 3
2 3
```

```stdout
8
```

### GCD Matrix

**Problem.** `M[i][j] = gcd(a_i, b_j)`. For each submatrix query, count the distinct values inside it.

**Idea.** The submatrix pairs every `a` in the row range with every `b` in the column range. Let `cntA[d]` and `cntB[d]` be how many of each are divisible by `d`. Then `cntA[d]·cntB[d]` pairs have `d | gcd`. Subtracting the counts for proper multiples, from the top down, gives the pairs with gcd *exactly* `d` (Möbius-style). A value appears iff that count is positive. Each query is O(V log V) with V = 10⁵, using NumPy slices for the multiples.

**Steps.**
1. Build frequency arrays for the two ranges and their "divisible by `d`" counts.
2. Go from `d = V` down to 1: `exact[d] = cntA·cntB − Σ exact[kd]`. Count the positive entries.

```python
import sys

import numpy as np

V = 100000


def divisible_counts(vals):
    freq = np.bincount(vals, minlength=V + 1)
    return np.array([0] + [int(freq[d::d].sum()) for d in range(1, V + 1)], dtype=np.int64)


def main():
    data = sys.stdin.buffer.read().split()
    n, m, q = int(data[0]), int(data[1]), int(data[2])
    a = np.array(data[3:3 + n], dtype=np.int64)
    b = np.array(data[3 + n:3 + n + m], dtype=np.int64)
    pos = 3 + n + m
    out = []
    for _ in range(q):
        r1, c1, r2, c2 = (int(x) for x in data[pos:pos + 4])
        pos += 4
        ca = divisible_counts(a[r1:r2 + 1])
        cb = divisible_counts(b[c1:c2 + 1])
        exact = ca * cb
        for d in range(V // 2, 0, -1):
            exact[d] -= exact[2 * d::d].sum()
        out.append(int((exact[1:] > 0).sum()))
    print('\n'.join(map(str, out)))


main()
```

**Watch out.** Enumerating up to 10¹⁰ cells per query is impossible. The divisor trick never looks at a cell. Values above `V/2` have no proper multiples ≤ V, so their counts are already exact.

```stdin
3 3 3
1 2 3
2 4 6
0 0 1 1
0 0 2 2
1 1 2 2
```

```stdout
2
3
3
```

### Fairy Chess

**Problem.** An `s`-leaper may jump to any square within Manhattan distance `s` (staying put counts), but not onto a pawn. Count its sequences of `m` moves, modulo 10⁹+7.

**Idea.** One move spreads the counts over a **diamond**. Rotating the board 45° (`u = x + y`, `v = x − y`) turns each diamond into an axis-aligned square. Then one 2-D prefix sum over the rotated grid gives every cell's diamond sum in O(1). Each of the `m` steps is a few NumPy operations, and pawn squares are zeroed after each step.

**Steps.**
1. Map each cell `(x, y)` to `(x + y, x − y + n − 1)` in a `(2n−1)²` grid.
2. For each step: scatter the counts, take a 2-D cumulative sum, read each cell's square `[u−s, u+s] × [v−s, v+s]`, then zero the pawns.

```python
import os

import numpy as np

MOD = 10 ** 9 + 7


def fairyChess(m, s, board):
    n = len(board)
    xs, ys = np.meshgrid(np.arange(n), np.arange(n), indexing='ij')
    u = (xs + ys).ravel()
    v = (xs - ys + n - 1).ravel()
    size = 2 * n - 1
    pawn = np.array([[ch == 'P' for ch in row] for row in board]).ravel()
    cur = np.array([[ch == 'L' for ch in row] for row in board], dtype=np.int64).ravel()
    lo_u = np.clip(u - s, 0, size)
    hi_u = np.clip(u + s + 1, 0, size)
    lo_v = np.clip(v - s, 0, size)
    hi_v = np.clip(v + s + 1, 0, size)
    for _ in range(m):
        grid = np.zeros((size + 1, size + 1), dtype=np.int64)
        grid[u + 1, v + 1] = cur
        pref = grid.cumsum(axis=0).cumsum(axis=1) % MOD
        cur = (pref[hi_u, hi_v] - pref[lo_u, hi_v] - pref[hi_u, lo_v] + pref[lo_u, lo_v]) % MOD
        cur[pawn] = 0
    return int(cur.sum() % MOD)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input())
    for _ in range(q):
        n, m, s = map(int, input().split())
        board = [input().strip() for _ in range(n)]
        fptr.write(str(fairyChess(m, s, board)) + '\n')
    fptr.close()
```

**Watch out.** The leaper *jumps*, so pawns in between don't block it; only the landing square matters. Staying in place is one of the moves (distance 0 ≤ `s`), which is why the first sample counts 4. Rotated cells that don't come from a board square are always 0, so the square sums stay correct.

```stdin
3
4 1 1
....
.L..
.P..
....
3 2 1
...
...
..L
4 3 2
....
...L
..P.
P...
```

```stdout
4
11
385
```

### Suffix Rotation

**Problem.** Each move picks an index larger than all earlier ones and rotates the suffix from there. Find the minimum number of moves to sort the string.

**Idea.**
- **Cyclic order is kept.** Rotations preserve the cyclic order of the unsorted suffix. So the unsorted part is always the remaining letters in their original cyclic order, starting at some "front" element.
- **Placing one letter.** Process letters from smallest to largest. Let `c` occupy `k` maximal cyclic blocks among the remaining letters.
  - **Cost.** If the front is not a `c`, every block needs one move. If the front begins a block, that block is free. If the front is in the middle of a block, that block splits into two runs, and only the first is free.
  - **Where the front lands.** It ends up just after whichever block is placed *last*, and any block that needed a move can be chosen last.
- **The DP.** Map each front element to its minimum cost. Each letter is one transition, made O(states + blocks) by keeping the best and second-best costs.

**Steps.**
1. Start with state `front = 0` and cost 0.
2. For each letter `c`, find its cyclic blocks among the letters ≥ `c` and relax the transitions. If only `c`s remain, finish.
3. Return the minimum cost.

```python
import sys


def suffix_rotation(s):
    n = len(s)
    INF = float('inf')
    states = {0: 0}
    for c in sorted(set(s)):
        Q = [i for i in range(n) if s[i] >= c]
        L = len(Q)
        isc = [s[v] == c for v in Q]
        if all(isc):
            return min(states.values())
        pos = {v: k for k, v in enumerate(Q)}
        blocks, block_of = [], [-1] * L
        k0 = next(k for k in range(L) if not isc[k])
        k = (k0 + 1) % L
        for _ in range(L):
            if isc[k]:
                if not isc[(k - 1) % L]:
                    blocks.append([k, k])
                blocks[-1][1] = k
                block_of[k] = len(blocks) - 1
            k = (k + 1) % L
        nb = len(blocks)
        afters = [Q[(blk[1] + 1) % L] for blk in blocks]
        new = {}

        def relax(front, cost):
            if cost < new.get(front, INF):
                new[front] = cost

        best_all = INF
        best1 = best2 = (INF, -1)              # (cost + k - 1, own block) for "all but own block"
        for front, cost in states.items():
            p = pos[front]
            if not isc[p]:
                best_all = min(best_all, cost + nb)
                continue
            b = block_of[p]
            split = blocks[b][0] != p
            k_lin = nb + (1 if split else 0)
            if k_lin == 1:
                relax(afters[b], cost)
            elif split:
                best_all = min(best_all, cost + k_lin - 1)
            else:
                cand = (cost + k_lin - 1, b)
                if cand < best1:
                    if cand[1] != best1[1]:
                        best2 = best1
                    best1 = cand
                elif cand[1] != best1[1] and cand < best2:
                    best2 = cand
                relax(afters[b], cost + k_lin)
        for bb in range(nb):
            if best_all < INF:
                relax(afters[bb], best_all)
            pick = best1 if best1[1] != bb else best2
            if pick[0] < INF:
                relax(afters[bb], pick[0])
        states = new
    return min(states.values())


def main():
    data = sys.stdin.read().split()
    g = int(data[0])
    print('\n'.join(str(suffix_rotation(s)) for s in data[1:1 + g]))


main()
```

**Watch out.**
- **Same-letter blocks.** Several equal letters in one cyclic block cost only one move. Choosing *which* block to place last decides the next front, and that choice is the whole DP.
- **How this was checked.** Against a BFS over all move sequences on hundreds of random short strings.

```stdin
3
abcdefghij
acab
baba
```

```stdout
0
1
2
```

### New Year Present

**Problem.** Count the 6-stick subsets that can form a square, with every stick used whole.

**Idea.** Six sticks on four sides means the side multiplicities are either `1+1+1+3` or `1+1+2+2`.
- **`1+1+1+3`.** Three sticks of the side length `L` plus three shorter sticks summing to `L`: `C(cnt[L], 3) · triples(L)`. To get the triples, sweep the sorted sticks as the third member and look up a running dictionary of pair sums of earlier sticks, only for the `L` values that occur at least 3 times.
- **`1+1+2+2`.** Two sticks of length `L` plus four shorter sticks that split into two pairs summing to `L`. We count *sets of sticks*, not pairings, so look at the four sticks' values:
  - two different value pairs `{v, L−v}` and `{v', L−v'}` split only one way: multiply the pair counts of the two types;
  - `{v, v, L−v, L−v}` splits two ways but is one set: `C(cnt[v], 2)·C(cnt[L−v], 2)`;
  - `{h, h, h, h}` with `h = L/2` is one set: `C(cnt[h], 4)`.

  Multiply the total by `C(cnt[L], 2)`.

**Steps.**
1. Count the lengths. Run the triple sweep for the `L` values that occur at least 3 times.
2. For the `L` values that occur at least 2 times, add up the three kinds of four-stick sets from the value counts.

```python
import os
from collections import Counter
from math import comb


def newYearPresent(l):
    cnt = Counter(l)
    vals = sorted(cnt)
    sticks = sorted(l)
    triple_targets = {L for L, c in cnt.items() if c >= 3}
    triples = Counter()
    pair_sums = Counter()
    for k, x in enumerate(sticks):
        for L in triple_targets:
            if L - x > 0:
                triples[L] += pair_sums[L - x]
        for j in range(k):
            pair_sums[sticks[j] + x] += 1
    total = sum(comb(cnt[L], 3) * triples[L] for L in triple_targets)
    for L, c in cnt.items():
        if c < 2:
            continue
        per_type = []                      # pairs summing to L, grouped by their value pair
        same_twice = 0                     # 4-sets {v, v, L-v, L-v} or {h, h, h, h}
        for v in vals:
            w = L - v
            if w < v:
                break
            if w == v:
                per_type.append(comb(cnt[v], 2))
                same_twice += comb(cnt[v], 4)
            elif w in cnt:
                per_type.append(cnt[v] * cnt[w])
                same_twice += comb(cnt[v], 2) * comb(cnt[w], 2)
        s = sum(per_type)
        distinct_types = (s * s - sum(p * p for p in per_type)) // 2
        total += comb(c, 2) * (distinct_types + same_twice)
    return total


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    l = list(map(int, input().split()))
    fptr.write(str(newYearPresent(l)) + '\n')
    fptr.close()
```

**Watch out.** Sticks that sum to `L` are automatically shorter than `L`, so they never overlap with the side sticks. Count each *set* of six sticks once: `{1, 1, 4, 4}` can be paired as (1a, 4a)(1b, 4b) or (1a, 4b)(1b, 4a), but it is a single choice of sticks. That is why the sample answer is 3, not 6.

```stdin
8
4 5 1 5 1 9 4 5
```

```stdout
3
```

### Travel around the world

**Problem.** Cities lie on a cycle. City `i` offers `a[i]` fuel (the tank holds at most `C`), and the road to the next city costs `b[i]`. Count the starting cities, with an empty tank, from which the full loop succeeds.

**Idea.** Refuelling is monotone: more fuel now never hurts later. That gives two steps:
- **Find one good start `p`.** Use the gas-station sweep: if a start fails at `t`, every start up to `t` fails too, so jump past `t`. Run it over two laps.
- **Test every city against `p`.** Every valid start passes `p`, and from `p` the loop is known to work with any amount of fuel. So city `i` is valid iff it can reach `p` from empty. Compute, backwards from `p`, the minimum arrival fuel `need[i] = max(0, need[i+1] + b[i] − a[i])`, which is impossible if `need[i+1] + b[i] > C`. Count the cities with `need = 0`.

**Steps.**
1. Two-lap sweep with `fuel = min(C, fuel + a) − b`, restarting after a failure. If no start survives `n` steps, the answer is 0.
2. Go backwards from `p` around the circle and count `need == 0`.

```python
import os


def travelAroundTheWorld(a, b, c):
    n = len(a)
    start, fuel, p = 0, 0, -1
    for j in range(2 * n):
        i = j % n
        fuel = min(c, fuel + a[i]) - b[i]
        if fuel < 0:
            start, fuel = j + 1, 0
            if start >= n:
                break
        elif j - start + 1 == n:
            p = start
            break
    if p < 0:
        return 0
    inf = float('inf')
    need, count = 0, 1                       # p itself is valid
    for step in range(1, n):
        i = (p - step) % n
        if need == inf or need + b[i] > c:
            need = inf
        else:
            need = max(0, need + b[i] - a[i])
        if need == 0:
            count += 1
    return count


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, c = map(int, input().split())
    a = list(map(int, input().split()))
    b = list(map(int, input().split()))
    fptr.write(str(travelAroundTheWorld(a, b, c)) + '\n')
    fptr.close()
```

**Watch out.** The tank cap breaks simple prefix-sum reasoning: fuel above `C` is lost, and a requirement above `C` is impossible no matter what. Simulating every start costs O(n²), up to 10¹⁰ steps.

```stdin
3 3
3 1 2
2 2 2
```

```stdout
2
```

### Longest Palindromic Subsequence

**Problem.** Count the insertions (position, letter) that increase the longest palindromic subsequence by at least `k`.

**Idea.** An insertion raises the LPS by at most 2, so `k ≥ 3` gives 0 and `k = 0` gives `26(n+1)`. For `k ∈ {1, 2}`, use two tables:
- `D[i][j]`, the LPS of `s[i..j]`;
- `O[a][b]`, the best "outer" palindrome pairing characters of `s[:a]` with characters of `s[b:]`.

Inserting `c` at gap `p` gives the larger of:
- `1 + O[p][p]`, with `c` as the centre;
- `2 + D[j+1][p−1] + O[j][p]`, pairing `c` with an `s[j] = c` on the left;
- `2 + D[p][j−1] + O[p][j+1]`, pairing `c` with an `s[j] = c` on the right.

Both tables fill one row at a time with a running maximum in NumPy, and each gap is scored with vector operations.

**Steps.**
1. Build `D` from the bottom row up and `O` from the top row down (`int16`).
2. For each gap, compute the best value per letter with `np.maximum.at` and count the letters with gain ≥ `k`.

```python
import os

import numpy as np


def longestPalindromicSubsequence(s, k):
    n = len(s)
    if k == 0:
        return 26 * (n + 1)
    if k > 2:
        return 0
    a = np.frombuffer(s.encode(), dtype=np.uint8) - 97
    D = np.zeros((n + 1, n + 1), dtype=np.int16)          # D[i][j], j < i means empty (0)
    for i in range(n - 1, -1, -1):
        below = D[i + 1]
        diag = np.zeros(n, dtype=np.int16)
        diag[i + 1:] = below[i:n - 1] + 2                  # D[i+1][j-1] + 2
        t = np.maximum(below[:n], np.where(a == a[i], diag, 0))
        t[:i] = 0
        t[i] = 1
        D[i, :n] = np.maximum.accumulate(t)
    O = np.zeros((n + 1, n + 1), dtype=np.int16)          # O[a][b], a <= b
    for row in range(1, n + 1):
        prev = O[row - 1]
        diag = np.zeros(n + 1, dtype=np.int16)
        diag[:n] = prev[1:n + 1] + 2
        t = np.maximum(prev, np.where(np.append(a == a[row - 1], False), diag, 0))
        O[row] = np.maximum.accumulate(t[::-1])[::-1]
    base = int(D[0, n - 1])
    idx = np.arange(n)
    count = 0
    for p in range(n + 1):
        best = np.full(26, 1 + int(O[p, p]), dtype=np.int32)
        left = idx[:p]
        if len(left):
            inner = np.where(left + 1 <= p - 1, D[np.minimum(left + 1, n), max(p - 1, 0)], 0)
            val = 2 + inner + O[left, p]
            np.maximum.at(best, a[left], val.astype(np.int32))
        right = idx[p:]
        if len(right):
            inner = np.where(right - 1 >= p, D[p, np.maximum(right - 1, 0)], 0)
            val = 2 + inner + O[p, right + 1]
            np.maximum.at(best, a[right], val.astype(np.int32))
        count += int((best - base >= k).sum())
    return count


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        n, k = map(int, input().split())
        s = input().strip()
        fptr.write(str(longestPalindromicSubsequence(s, k)) + '\n')
    fptr.close()
```

**Watch out.**
- **Why at most 2.** The inserted character can sit in at most one pair, so the gain is at most 2.
- **Building the rows.** Each table row is a running maximum of "skip" and "pair" options. That works because the values are monotone along a row.
- **Memory.** Two 3001×3001 `int16` tables take about 36 MB.

```stdin
3
1 1
a
3 2
aab
3 0
aba
```

```stdout
2
1
104
```

### Candles Counting

**Problem.** Count the strictly increasing (by height) subsequences that contain all `K ≤ 7` colours, modulo 10⁹+7.

**Idea.** `dp[i][mask]` = the number of increasing subsequences ending at candle `i` whose set of colours is exactly `mask`. To extend, sum the `dp` vectors of every earlier candle that is lower: a Fenwick tree over heights whose nodes hold whole 128-entry vectors. Then OR in the candle's own colour and add 1 for the subsequence that starts here.

**Steps.**
1. For each candle: query the prefix vector for heights below `h`, shift every mask to `mask | bit`, and add the singleton.
2. Add the result to the Fenwick tree at `h` and to the running total of `dp[full]`.

```python
import os

import numpy as np

MOD = 10 ** 9 + 7


def candlesCounting(k, candles):
    size = 1 << k
    full = size - 1
    maxh = max(h for h, _ in candles)
    tree = np.zeros((maxh + 1, size), dtype=np.int64)
    masks = np.arange(size)
    answer = 0
    for h, c in candles:
        bit = 1 << (c - 1)
        acc = np.zeros(size, dtype=np.int64)
        i = h - 1
        while i > 0:
            acc += tree[i]
            i -= i & -i
        acc %= MOD
        vec = np.zeros(size, dtype=np.int64)
        np.add.at(vec, masks | bit, acc)
        vec[bit] += 1
        vec %= MOD
        answer = (answer + int(vec[full])) % MOD
        i = h
        while i <= maxh:
            tree[i] = (tree[i] + vec) % MOD
            i += i & -i
    return answer


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    candles = [list(map(int, input().split())) for _ in range(n)]
    fptr.write(str(candlesCounting(k, candles)) + '\n')
    fptr.close()
```

**Watch out.** Querying below `h` (not including it) enforces *strictly* increasing heights. Running a separate Fenwick tree for each of the 128 colour sets would be 128 times slower; one tree of vectors does them all at once.

```stdin
4 3
1 1
3 2
2 2
4 3
```

```stdout
2
```

### Hyper Strings

**Problem.** Count the distinct strings of length ≤ `M` (including the empty one) that can be split into words from `H`, where each word has strictly increasing letters from `a`–`j`. Answer modulo 10⁹+7.

**Idea.** Every word is strictly increasing, so a split point must occur wherever the string does *not* increase. That cuts a hyper string uniquely into maximal increasing *runs*, and each run must itself split into words of `H`. There are only 1023 possible runs (non-empty subsets of 10 letters); test each with a small DP. Then count strings as sequences of good runs, where each run's first letter is ≤ the previous run's last letter, so the runs stay maximal: `f[len][last]`.

**Steps.**
1. For each subset run (letters in order), check that it can be split into `H`-words.
2. DP over the length with state = last letter (start = "no letter").

```python
import os

MOD = 10 ** 9 + 7


def hyperStrings(m, H):
    words = set(H)
    runs = []
    for mask in range(1, 1 << 10):
        r = ''.join(chr(97 + i) for i in range(10) if mask >> i & 1)
        ok = [True] + [False] * len(r)
        for i in range(1, len(r) + 1):
            ok[i] = any(ok[j] and r[j:i] in words for j in range(i))
        if ok[len(r)]:
            runs.append((len(r), ord(r[0]) - 97, ord(r[-1]) - 97))
    f = [[0] * 11 for _ in range(m + 1)]          # last letter 0..9, 10 = empty string
    f[0][10] = 1
    total = 1
    for length in range(m + 1):
        for last in range(11):
            ways = f[length][last]
            if not ways:
                continue
            for size, first, end in runs:
                if length + size <= m and (last == 10 or first <= last):
                    f[length + size][end] = (f[length + size][end] + ways) % MOD
        if length:
            total = (total + sum(f[length][:10])) % MOD
    return total


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m = map(int, input().split())
    H = [input().strip() for _ in range(n)]
    fptr.write(str(hyperStrings(m, H)) + '\n')
    fptr.close()
```

**Watch out.** Counting *concatenations* overcounts. `a` + `b` and `ab` give the same string, so count each string once through its unique run decomposition. The empty string is included, which is why the sample counts 7.

```stdin
2 3
a
ab
```

```stdout
7
```

### Swap Permutation

**Problem.** For the identity permutation of size `n`, count (1) the permutations reachable with *exactly* `k` adjacent swaps and (2) those reachable with *at most* `k` arbitrary swaps, modulo 10⁹+7.

**Idea.**
- **Exactly `k` adjacent swaps.** These reach exactly the permutations with at most `k` inversions and the same parity as `k`, since a wasted pair of swaps can cancel out. The inversion counts are Mahonian numbers, built one element at a time with sliding-window sums.
- **At most `k` arbitrary swaps.** A permutation needs `n − cycles` swaps. So sum the unsigned Stirling numbers of the first kind `c(n, j)` over `j ≥ n − k`, using `c(i, j) = c(i−1, j−1) + (i−1)·c(i−1, j)`.

**Steps.**
1. Mahonian numbers up to `k` inversions with NumPy prefix sums. Sum those with `i ≤ k` and `i ≡ k (mod 2)`.
2. Stirling rows, then sum the cycle counts `j ≥ n − k`.

```python
import os

import numpy as np

MOD = 10 ** 9 + 7


def swapPermutation(n, k):
    inv = np.zeros(k + 1, dtype=np.int64)
    inv[0] = 1
    for i in range(2, n + 1):                 # inserting element i adds 0..i-1 inversions
        pre = np.concatenate(([0], np.cumsum(inv) % MOD))
        idx = np.arange(k + 1)
        lo = np.maximum(idx - (i - 1), 0)
        inv = (pre[idx + 1] - pre[lo]) % MOD
    s1 = int(inv[k % 2::2].sum() % MOD) if n > 1 else 0
    stir = np.zeros(n + 1, dtype=np.int64)
    stir[0] = 1
    for i in range(1, n + 1):
        new = np.zeros(n + 1, dtype=np.int64)
        new[1:] = (stir[:-1] + (i - 1) * stir[1:]) % MOD
        stir = new
    s2 = int(stir[max(0, n - k):].sum() % MOD)
    return [s1, s2]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    fptr.write(' '.join(map(str, swapPermutation(n, k))) + '\n')
    fptr.close()
```

**Watch out.** "Exactly `k`" adjacent swaps can waste moves in pairs (swap and swap back), so every permutation with ≤ `k` inversions of the right parity is reachable. The exception is `n = 1`: there is no adjacent pair to swap, so exactly `k ≥ 1` swaps are impossible and `S1 = 0`.

```stdin
3 2
```

```stdout
3 6
```

### Extremum Permutations

**Problem.** Count the permutations of `1..N` where the given positions `a_i` are local minima and the positions `b_i` are local maxima.

**Idea.** Each condition only fixes the direction (`<` or `>`) of the comparisons with the two neighbours. Turn them into a sign for each adjacent pair (`up`, `down` or free), and report 0 on a contradiction. Then use the classic "relative rank" DP: `dp[i][j]` = the number of ways where the `i`-th element is the `j`-th smallest among the first `i`. An `up` step sums `dp` over smaller ranks, a `down` step over larger ranks, and a free step takes the total. Each row is one NumPy prefix sum.

**Steps.**
1. Build the sign array; contradictory constraints give 0.
2. Run the rank DP for `i = 2..N` and return the sum of the last row.

```python
import os

import numpy as np

MOD = 10 ** 9 + 7


def extremumPermutations(n, a, b):
    sign = [0] * (n + 1)                  # sign[i]: relation between p[i] and p[i+1] (1 = up, -1 = down)

    def need(i, s):
        if i < 1 or i >= n:
            return True
        if sign[i] and sign[i] != s:
            return False
        sign[i] = s
        return True

    for x in a:                           # local minimum: p[x-1] > p[x] < p[x+1]
        if not (need(x - 1, -1) and need(x, 1)):
            return 0
    for x in b:                           # local maximum: p[x-1] < p[x] > p[x+1]
        if not (need(x - 1, 1) and need(x, -1)):
            return 0
    dp = np.array([1], dtype=np.int64)   # i = 1: rank 1
    for i in range(2, n + 1):
        pre = np.concatenate(([0], np.cumsum(dp) % MOD))
        j = np.arange(1, i + 1)          # new element's rank among i elements
        if sign[i - 1] == 1:              # p[i-1] < p[i]: previous rank < j
            dp = pre[j - 1] % MOD
        elif sign[i - 1] == -1:           # p[i-1] > p[i]: previous rank >= j
            dp = (pre[i - 1] - pre[j - 1]) % MOD
        else:
            dp = np.full(i, pre[i - 1] % MOD, dtype=np.int64)
    return int(dp.sum() % MOD)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k, l = map(int, input().split())
    a = list(map(int, input().split())) if k else []
    b = list(map(int, input().split())) if l else []
    fptr.write(str(extremumPermutations(n, a, b)) + '\n')
    fptr.close()
```

**Watch out.** Inserting the `i`-th element with rank `j` shifts every earlier element of rank ≥ `j` up by one. That is why a "down" step sums the earlier ranks `j..i−1` (in the old ranking). Overlapping or adjacent constraints can contradict each other, and the sign array catches that.

```stdin
4 1 1
2
3
```

```stdout
5
```
