## Constructive Algorithms

### Lena Sort

**Problem.** Lena's quicksort always uses the first element as the pivot and makes `size − 1` comparisons per call. For each query `(len, c)`, build an array of `len` distinct values that takes exactly `c` comparisons, or print `-1`.

**Idea.** Only the sizes of the two sides matter: a call on `m` elements costs `m − 1` plus the costs of its two parts.
- **Range of costs.** The most a call can cost is `m(m−1)/2` (a sorted array: the pivot is always the minimum). The least, `mn[m]`, comes from the most balanced splits. Every value in between is reachable; this was checked by brute force for `m ≤ 7`.
- **Building the array.** Work on the sub-problem `(size, c)`.
  - If the rest `c − (size−1)` still fits `size − 1` elements on one side (it is `≥ mn[size−1]`), make the pivot the smallest value and recurse on the right.
  - Otherwise, split off the smallest left size `a` with `mn[a] + mn[size−1−a] ≤ rest`, found by binary search. This sum shrinks as the split balances. Give the left side as many comparisons as it can take and the right side the rest.
- **Order in the array.** Place the pivot first, then the "less" values, then the "more" values. Lena's partition keeps this order.

**Steps.**
1. Precompute `mn[m]` for `m ≤ 10⁵`.
2. For each query, check `mn[len] ≤ c ≤ len(len−1)/2`, then build iteratively with an explicit stack, using values `1..len`.

```python
import sys


def main():
    data = sys.stdin.buffer.read().split()
    q = int(data[0])
    queries = [(int(data[1 + 2 * i]), int(data[2 + 2 * i])) for i in range(q)]
    N = max(l for l, _ in queries)
    mn = [0] * (N + 1)
    for m in range(2, N + 1):
        a = (m - 1) // 2
        mn[m] = m - 1 + mn[a] + mn[m - 1 - a]
    out = []
    for n, c in queries:
        if c < mn[n] or c > n * (n - 1) // 2:
            out.append('-1')
            continue
        res = []
        stack = [(n, c, 1)]                      # (size, comparisons, smallest value)
        while stack:
            size, cc, lo = stack.pop()
            if size == 0:
                continue
            if size == 1:
                res.append(lo)
                continue
            m = size - 1
            rest = cc - m
            if rest >= mn[m]:                    # pivot is the minimum
                res.append(lo)
                stack.append((m, rest, lo + 1))
                continue
            a_lo, a_hi = 1, m // 2               # smallest left size that is cheap enough
            while a_lo < a_hi:
                mid = (a_lo + a_hi) // 2
                if mn[mid] + mn[m - mid] <= rest:
                    a_hi = mid
                else:
                    a_lo = mid + 1
            a, b = a_lo, m - a_lo
            ca = min(a * (a - 1) // 2, rest - mn[b])
            res.append(lo + a)                   # a values are smaller than the pivot
            stack.append((b, rest - ca, lo + a + 1))
            stack.append((a, ca, lo))            # popped first: the "less" part comes next
        out.append(' '.join(map(str, res)))
    sys.stdout.write('\n'.join(out) + '\n')


main()
```

**Watch out.** `len` can be 10⁵ and a sorted array recurses 10⁵ deep, so the build uses a stack instead of recursion. Any array with the right count is accepted, so the hidden test checks the comparison count by simulating Lena's sort.

```stdin
5
5 6
5 100
1 0
6 15
7 11
```

```check
qs = [tuple(map(int, l.split())) for l in stdin.strip().split('\n')[1:]]
lines = output.strip().split('\n')
assert len(lines) == len(qs)
def count(arr):
    total, st = 0, [arr]
    while st:
        nums = st.pop()
        if len(nums) <= 1:
            continue
        p = nums[0]
        total += len(nums) - 1
        st.append([x for x in nums[1:] if x < p])
        st.append([x for x in nums[1:] if x >= p])
    return total
expected_none = {(5, 100)}
for (n, c), line in zip(qs, lines):
    if (n, c) in expected_none:
        assert line.strip() == '-1'
        continue
    arr = list(map(int, line.split()))
    assert len(arr) == n and len(set(arr)) == n and all(1 <= v <= 10 ** 9 for v in arr)
    assert count(arr) == c, (n, c, arr)
```

### Flipping the Matrix

**Problem.** In a `2n×2n` matrix you may reverse any row or column. Maximise the sum of the top-left `n×n` quadrant.

**Idea.** Reversals only ever move a value among its four mirror positions: `(i, j)`, `(i, 2n−1−j)`, `(2n−1−i, j)` and `(2n−1−i, 2n−1−j)`. Each of these orbits supplies exactly one cell of the quadrant, and some sequence of flips can bring any member of the orbit there without disturbing the other choices. So the answer is the sum over the orbits of their maximum.

**Steps.**
1. For every `i, j < n`, add the largest of the four mirror values.

```python
import os


def flippingMatrix(matrix):
    m = len(matrix)
    n = m // 2
    total = 0
    for i in range(n):
        for j in range(n):
            total += max(matrix[i][j], matrix[i][m - 1 - j],
                         matrix[m - 1 - i][j], matrix[m - 1 - i][m - 1 - j])
    return total


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        n = int(input().strip())
        matrix = [list(map(int, input().rstrip().split())) for _ in range(2 * n)]
        fptr.write(str(flippingMatrix(matrix)) + '\n')
    fptr.close()
```

**Watch out.** You do not need to find the actual flips; the four-cell orbits are independent. This is the classic "it looks like search but is a formula" constructive problem.

```stdin
1
2
112 42 83 119
56 125 56 49
15 78 101 43
62 98 114 108
```

```stdout
414
```

### Gaming Array

**Problem.** Players alternately remove the maximum element and everything to its right, and Bob moves first. Whoever makes the last move wins.

**Idea.** Every move removes the current maximum. The next maximum is the largest element to its left, so the moves hit exactly the **prefix maxima** (the records read left to right), from the last record back to the first. The game always lasts as many moves as there are records. Bob wins exactly when that count is odd.

**Steps.**
1. Count the elements larger than everything before them.
2. Print `BOB` if the count is odd, else `ANDY`.

```python
import os


def gamingArray(arr):
    records = 0
    best = 0
    for x in arr:
        if x > best:
            best = x
            records += 1
    return 'BOB' if records % 2 else 'ANDY'


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    g = int(input().strip())
    for _ in range(g):
        input()
        arr = list(map(int, input().rstrip().split()))
        fptr.write(gamingArray(arr) + '\n')
    fptr.close()
```

**Watch out.** No player has a choice, so there is no game tree to search. Simulating the removals directly is O(n²) in the worst case; counting records is O(n).

```stdin
2
5
5 2 6 3 4
2
3 1
```

```stdout
ANDY
BOB
```

### New Year Chaos

**Problem.** People swap only with the person directly in front of them, each at most twice. Given the final queue, print the minimum number of bribes, or `Too chaotic`.

**Idea.** Person `p` can be at most 2 places ahead of position `p`; otherwise print `Too chaotic`. Every bribe is one inversion, so the answer is the number of pairs where a larger sticker stands in front of a smaller one. Anyone who overtook `p` started behind `p` and moved at most 2 places forward, so they now stand no earlier than position `p − 2`. Only that short window needs to be checked.

**Steps.**
1. For each position `i` (0-based) holding `p`: if `p − (i+1) > 2`, it is too chaotic.
2. Count the `j` in `[max(0, p−2), i)` with `q[j] > p`.

```python
def minimumBribes(q):
    bribes = 0
    for i, p in enumerate(q):
        if p - (i + 1) > 2:
            print('Too chaotic')
            return
        for j in range(max(0, p - 2), i):
            if q[j] > p:
                bribes += 1
    print(bribes)


if __name__ == '__main__':
    t = int(input().strip())
    for _ in range(t):
        n = int(input().strip())
        q = list(map(int, input().rstrip().split()))
        minimumBribes(q)
```

**Watch out.** Counting how far each person moved *forward* misses the people who were pushed back. Counting inversions with the window start at `p − 2` (not `i − 2`) keeps it O(n) and still finds everyone who overtook `p`.

```stdin
2
5
2 1 5 3 4
5
2 5 1 3 4
```

```stdout
3
Too chaotic
```

### Bonetrousle

**Problem.** Pick `b` distinct box sizes from `1..k` with total exactly `n` (up to 10¹⁸), or print `-1`.

**Idea.** The smallest total is `1 + … + b`; the largest is `(k−b+1) + … + k`. Every total in between is reachable: start from `1..b` and slide boxes up one step at a time. Concretely, let `d = n − b(b+1)/2` and write `d = q·(k−b) + r`.
- The top `q` boxes jump the full `k − b` steps, becoming `k−q+1 … k`.
- The next box moves up by `r`.
- The rest stay put.

All values stay distinct.

**Steps.**
1. If `n` is outside `[b(b+1)/2, b(2k−b+1)/2]`, print `-1`.
2. Otherwise build the boxes as above (when `k = b`, then `d = 0`).

```python
import sys


def bonetrousle(n, k, b):
    lo = b * (b + 1) // 2
    hi = b * (2 * k - b + 1) // 2
    if n < lo or n > hi:
        return [-1]
    d = n - lo
    if k == b:
        return list(range(1, b + 1))
    q, r = divmod(d, k - b)
    boxes = list(range(1, b + 1))
    for i in range(b - q, b):                 # the top q boxes take the full shift
        boxes[i] += k - b
    if q < b:
        boxes[b - q - 1] += r
    return boxes


def main():
    data = sys.stdin.read().split()
    t = int(data[0])
    out = []
    for i in range(t):
        n, k, b = map(int, data[1 + 3 * i:4 + 3 * i])
        out.append(' '.join(map(str, bonetrousle(n, k, b))))
    print('\n'.join(out))


main()
```

**Watch out.** `n` and `k` reach 10¹⁸, so never loop over values; only over the `b ≤ 10⁵` boxes. Any valid set is accepted; the hidden test checks the sum, the range and distinctness.

```stdin
6
12 8 3
10 3 3
9 10 2
22 7 4
1000000000000000000 1000000000000000000 1
15 5 5
```

```check
qs = [tuple(map(int, l.split())) for l in stdin.strip().split('\n')[1:]]
lines = output.strip().split('\n')
assert len(lines) == len(qs)
for (n, k, b), line in zip(qs, lines):
    vals = list(map(int, line.split()))
    if b * (b + 1) // 2 <= n <= b * (2 * k - b + 1) // 2:
        assert len(vals) == b and len(set(vals)) == b, line
        assert all(1 <= v <= k for v in vals) and sum(vals) == n, line
    else:
        assert vals == [-1], line
```

### Yet Another KMP Problem

**Problem.** Given the letter counts, build the string whose KMP failure values have the smallest possible sum, and among those the lexicographically smallest.

**Idea.** Every later occurrence of the first letter has a failure value of at least 1, because it matches `S[1]`. So the sum is at least (count of the first letter) − 1, and that is always reachable. The first letter must therefore have the minimum count; take the smallest such letter `f`.
- **`f` is not the overall smallest letter, or appears once.** Write `f` and then all remaining letters in sorted order. Here `S[2]` is a letter other than `f`, so every later `f` scores exactly 1.
- **Only one distinct letter.** The string is forced.
- **`f` is also the overall smallest letter and appears at least twice.** Starting `ff` is lexicographically best. But now `S[2] = f`, so a later `ff` would score 2. Use `ff`, then alternate (next smallest other letter, `f`) until the `f`s run out, then the rest in sorted order.

This was checked by brute force over all arrangements of small inputs.

**Steps.**
1. Find `m`, the minimum positive count, and `f`, the smallest letter with that count.
2. Apply the matching case above.

```python
import os


def kmp(x):
    letters = [chr(97 + i) for i in range(26) if x[i] > 0]
    cnt = {chr(97 + i): x[i] for i in range(26)}
    if len(letters) == 1:
        return letters[0] * cnt[letters[0]]
    m = min(cnt[c] for c in letters)
    first = min(c for c in letters if cnt[c] == m)
    cnt[first] -= 1
    if first != letters[0] or m == 1:
        return first + ''.join(c * cnt[c] for c in letters)
    out = [first, first]
    cnt[first] -= 1
    others = letters[1:]
    oi = 0
    while cnt[first] > 0:                 # separate the remaining f's: never "ff" again
        while cnt[others[oi]] == 0:
            oi += 1
        out.append(others[oi])
        cnt[others[oi]] -= 1
        out.append(first)
        cnt[first] -= 1
    out.append(''.join(c * cnt[c] for c in others))
    return ''.join(out)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    x = list(map(int, input().rstrip().split()))
    fptr.write(kmp(x) + '\n')
    fptr.close()
```

**Watch out.** There are always enough other letters to separate the `f`s: `f` has the minimum count, so every other letter appears at least `m` times. The string can be 10⁶ long, so build it with joins, not repeated concatenation.

```stdin
2 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
```

```stdout
aabb
```

### Beautiful 3 Set

**Problem.** Find the largest set of triples `(x, y, z)` of non-negative integers with `x + y + z = n`, such that all the `x`s are distinct, all the `y`s are distinct and all the `z`s are distinct.

**Idea.** **Upper bound.** `K` distinct non-negative values sum to at least `0 + 1 + … + (K−1)`. So `K·n = Σx + Σy + Σz ≥ 3·K(K−1)/2`, which gives `K ≤ ⌊2n/3⌋ + 1`.

**Construction.** Use two diagonals whose `z` values have different parities. Write `n = 3q + rem`.
- **`rem = 0` or `1`.** Take `(i, q+i, 2q−2i)` for `i = 0..q` and `(q+j, j−1, 2q−2j+1)` for `j = 1..q`, then add `rem` to every `z`.
- **`rem = 2`.** Take `(i, q+2+i, 2q−2i)` for `i = 0..q` and `(q+1+j, j, 2q+1−2j)` for `j = 0..q`.

In each case the `x`s and `y`s fill disjoint ranges and the `z`s split into evens and odds. Both families have size `⌊2n/3⌋ + 1`.

**Steps.**
1. Build the family for `n mod 3`; print its size and the triples.

```python
n = int(input())
q, rem = divmod(n, 3)
if rem == 2:
    triples = ([(i, q + 2 + i, 2 * q - 2 * i) for i in range(q + 1)] +
               [(q + 1 + j, j, 2 * q + 1 - 2 * j) for j in range(q + 1)])
else:
    triples = ([(i, q + i, 2 * q - 2 * i + rem) for i in range(q + 1)] +
               [(q + j, j - 1, 2 * q - 2 * j + 1 + rem) for j in range(1, q + 1)])
print(len(triples))
print('\n'.join(f"{x} {y} {z}" for x, y, z in triples))
```

**Watch out.** Any maximum set is accepted, so the hidden test checks the size `⌊2n/3⌋ + 1` and the three distinctness rules. Brute force confirms the bound is tight for `n ≤ 8`, and the construction was verified for every `n ≤ 300`.

```stdin
299
```

```check
n = int(stdin.split()[0])
lines = output.strip().split('\n')
k = int(lines[0])
assert k == 2 * n // 3 + 1, k
trip = [tuple(map(int, l.split())) for l in lines[1:]]
assert len(trip) == k
assert all(min(t) >= 0 and sum(t) == n for t in trip)
for idx in range(3):
    assert len({t[idx] for t in trip}) == k
```

### Inverse RMQ

**Problem.** The `2n − 1` values of a min segment tree over `n` distinct leaves were shuffled. Rebuild the lexicographically smallest valid tree (in array order), or print `NO`.

**Idea.** In a min segment tree, a value that first appears at depth `d` is copied all the way down to a leaf. So it occurs exactly `k + 1 − d` times, where `n = 2^k`.
- **Count check.** There must be exactly `n` distinct values: one with count `k+1` (the root), one with count `k`, two with count `k−1`, …, and `n/2` with count 1.
- **Fill the levels top-down.** Each node's value `v` is copied into one child and the other child gets a new value `> v` from that level's pool. For the lexicographically smallest array:
  - copy `v` into the **left** child;
  - give the right child the **smallest unused value `> v`** from the pool, processing nodes left to right.

An exchange argument shows this greedy never blocks a later node that could otherwise be served.

**Steps.**
1. Count the values and verify the level sizes.
2. For each level, find "smallest unused `≥` index" in the sorted pool with `bisect` plus a union-find skip pointer.
3. Print `NO` if some node finds no larger value.

```python
import sys
from bisect import bisect_right
from collections import Counter


def solve(n, vals):
    k = n.bit_length() - 1
    cnt = Counter(vals)
    if len(cnt) != n:
        return None
    by_count = {}
    for v, c in cnt.items():
        by_count.setdefault(c, []).append(v)
    need = {k + 1: 1}
    for d in range(1, k + 1):
        need[k + 1 - d] = 1 << (d - 1)
    if any(need.get(c, 0) != len(lst) for c, lst in by_count.items()):
        return None
    tree = [0] * (2 * n - 1)
    tree[0] = by_count[k + 1][0]
    for d in range(1, k + 1):
        pool = sorted(by_count[k + 1 - d])
        nxt = list(range(len(pool) + 1))

        def find(i):
            root = i
            while nxt[root] != root:
                root = nxt[root]
            while nxt[i] != root:
                nxt[i], i = root, nxt[i]
            return root

        for p in range((1 << (d - 1)) - 1, (1 << d) - 1):
            v = tree[p]
            tree[2 * p + 1] = v
            j = find(bisect_right(pool, v))
            if j == len(pool):
                return None
            tree[2 * p + 2] = pool[j]
            nxt[j] = j + 1
    return tree


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    tree = solve(n, list(map(int, data[1:2 * n])))
    if tree is None:
        print('NO')
    else:
        print('YES')
        print(' '.join(map(str, tree)))


main()
```

**Watch out.** Having the right distinct values is not enough. The multiplicities must match the level sizes exactly (sample 2, `1 1 1`, fails). It is also not enough that the counts fit, because a node may find no larger unused value. `n = 1` is a single leaf with count 1.

```stdin
4
3 1 3 1 2 4 1
```

```stdout
YES
1 1 3 1 2 3 4
```

### Two Subarrays

**Problem.** For a subarray, `f = sum − inc`, where `inc` is the largest sum of a strictly increasing subsequence. Find the maximum `f` over all subarrays (`g`), and how many subarrays reach `g` with the shortest possible length. The values are in `[−40, 40]` and `n ≤ 2·10⁵`.

**Idea.** Every single element gives `f = 0`, so `g ≥ 0`. If `g = 0`, the answer is `0 n`.

For `g > 0`, use `inc' = max(0, best chain of positive values)`. This equals `inc` on every subarray that matters, and it is subadditive: `inc'(l..r) ≤ inc'(l..m) + inc'(m+1..r)`. So `f'` is superadditive, and that gives three ways to drop a start `l` for good, while scanning `r` left to right:
1. **Positive prefix.** If some subarray ending at `l − 1` has `f > 0`, extending it beats starting at `l`. So `l` is a candidate only if the best `f` ending at `l − 1` is `≤ 0`.
2. **Larger prefix sum.** An earlier start `l₁` always has `inc' ≥` that of a later start `l₂`. So if `P[l₁] ≥ P[l₂]`, the later and shorter `l₂` is never worse. The candidates therefore keep strictly increasing prefix sums, within `820 + 1` of the first one, since `inc' ≤ 1+…+40 = 820`.
3. **Same chain profile.** Each candidate keeps a 41-entry profile: best chain sum using values `≤ v`. Two candidates with identical profiles evolve identically, so keep only the earlier one, whose prefix sum is strictly smaller.

All candidates update together with NumPy. For each `r`, take the best `f` and the **largest** `l` reaching it, which gives the shortest length.

**Steps.**
1. At each `r`, maybe add `l = r` as a candidate (rules 1 and 2). If `a_r > 0`, update all the profiles and merge equal neighbours (rule 3).
2. Compute `f` for all candidates. Track `g`, the shortest length, and how many `r` reach it.

```python
import sys

import numpy as np


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    a = list(map(int, data[1:1 + n]))
    P = [0] * (n + 1)
    for i, x in enumerate(a):
        P[i + 1] = P[i] + x
    cap = 1024
    D = np.zeros((cap, 41), dtype=np.int64)
    Pc = np.zeros(cap, dtype=np.int64)
    Lc = np.zeros(cap, dtype=np.int64)
    k = 0
    g, best_len, cnt = 0, 1, 0
    prev_best = 0
    for r in range(n):
        if r == 0 or prev_best <= 0:                   # rule 1
            p = P[r]
            while k and Pc[k - 1] >= p:                # rule 2
                k -= 1
            if k == 0 or p < Pc[0] + 821:
                D[k] = 0
                Pc[k] = p
                Lc[k] = r
                k += 1
        x = a[r]
        if x > 0:
            new = D[:k, x - 1] + x
            np.maximum(D[:k, x:], new[:, None], out=D[:k, x:])
            if k > 1:                                  # rule 3
                same = (D[1:k] == D[:k - 1]).all(axis=1)
                if same.any():
                    keep = np.concatenate(([True], ~same))
                    k2 = int(keep.sum())
                    D[:k2], Pc[:k2], Lc[:k2] = D[:k][keep], Pc[:k][keep], Lc[:k][keep]
                    k = k2
        f = P[r + 1] - Pc[:k] - D[:k, 40]
        m = int(f.max())
        idx = k - 1 - int(np.argmax(f[::-1] == m))      # largest l reaching m
        length = r - int(Lc[idx]) + 1
        prev_best = m
        if m > g:
            g, best_len, cnt = m, length, 1
        elif m == g and m > 0:
            if length < best_len:
                best_len, cnt = length, 1
            elif length == best_len:
                cnt += 1
    print(f"{g} {cnt}" if g > 0 else f"0 {n}")


main()
```

**Watch out.**
- **Why `inc'`.** A subarray with no positive value has `f = sum − max ≤ 0`, so it never matters once `g > 0`. Using `inc' = 0` for it is what makes the domination rules valid.
- **Testing.** Checked against an O(n³) brute force. Adversarial patterns such as repeated `1..40, −819` blocks, which would keep 821 candidates without rule 3, run in about 1.5 s.

```stdin
3
2 3 1
```

```stdout
1 1
```

### Lovely Triplets

**Problem.** Build a graph with at most 100 nodes and 100 edges that has exactly `P ≤ 5000` triplets whose pairwise distances all equal `Q` (`2 ≤ Q ≤ 9`).

**Idea.** Use separate components; triplets never cross components, so their counts add up.
- **`Q = 2`.** A star with `k` leaves gives `C(k, 3)` triplets and costs `k + 1` nodes. An unbounded knapsack over `C(k, 3)` finds the cheapest sum for every `P`. The worst case needs 70 nodes.
- **`Q ≥ 3`.** Use three "arms" around a core whose attachment points are pairwise at distance `D`:
  - `D = 1` (a triangle) for odd `Q`;
  - `D = 2` (a hub with three neighbours) for even `Q`.

  Each arm is a path to a star centre with `k_i` leaves, so that leaves on different arms are at distance exactly `Q`. Leaves on the same arm are 2 apart, and every other pair is closer. A component therefore gives `k₁·k₂·k₃` triplets. It costs `base + k₁ + k₂ + k₃` nodes, where `base = 3t` for odd `Q` and `3t + 1` for even `Q`, with `t = ⌊(Q−1)/2⌋`.
- **Fitting in 100 nodes.** At most three components always suffice; the worst case is 92 nodes for `Q = 9`, checked for every `P ≤ 5000`. They are found with min-plus combinations of the one-component costs.

**Steps.**
1. Compute the cheapest component for every value, then the best split of `P` into one, two or three components.
2. Emit the components with consecutive node numbers.

```python
import sys

import numpy as np

INF = 10 ** 9


def plan(P, Q):
    c1 = np.full(P + 1, INF, dtype=np.int64)
    how = {}
    if Q == 2:
        items = []
        k = 3
        while k * (k - 1) * (k - 2) // 6 <= P:
            items.append((k * (k - 1) * (k - 2) // 6, k))
            k += 1
        best = [0] + [INF] * P
        choice = [0] * (P + 1)
        for v in range(1, P + 1):
            for w, kk in items:
                if w <= v and best[v - w] + kk + 1 < best[v]:
                    best[v] = best[v - w] + kk + 1
                    choice[v] = (w, kk)
        comps, v = [], P
        while v:
            w, kk = choice[v]
            comps.append(('star', kk))
            v -= w
        return comps
    t = (Q - 1) // 2
    base = 3 * t if Q % 2 else 3 * t + 1
    k1 = 1
    while k1 ** 3 <= P:
        k2 = k1
        while k1 * k2 * k2 <= P:
            for k3 in range(k2, P // (k1 * k2) + 1):
                v = k1 * k2 * k3
                if base + k1 + k2 + k3 < c1[v]:
                    c1[v] = base + k1 + k2 + k3
                    how[v] = ('arms', k1, k2, k3)
            k2 += 1
        k1 += 1
    if c1[P] <= 100:
        return [how[P]]
    c2 = c1.copy()
    arg2 = np.zeros(P + 1, dtype=np.int64)
    for u in range(1, P + 1):
        if c1[u] < INF:
            cand = c1[u] + c1[:P + 1 - u]
            better = cand < c2[u:]
            c2[u:][better] = cand[better]
            arg2[u:][better] = u

    def split2(v):
        u = int(arg2[v])
        return [how[v]] if u == 0 else [how[u], how[v - u]]

    if c2[P] <= 100:
        return split2(P)
    for u in range(1, P):
        if c1[u] + c2[P - u] <= 100:
            return [how[u]] + split2(P - u)
    return None


def main():
    P, Q = map(int, sys.stdin.read().split()[:2])
    edges = []
    count = [0]

    def node():
        count[0] += 1
        return count[0]

    t = (Q - 1) // 2
    for comp in plan(P, Q):
        if comp[0] == 'star':
            c = node()
            edges += [(c, node()) for _ in range(comp[1])]
            continue
        if Q % 2:
            att = [node() for _ in range(3)]
            edges += [(att[0], att[1]), (att[1], att[2]), (att[0], att[2])]
        else:
            hub = node()
            att = [node() for _ in range(3)]
            edges += [(hub, a) for a in att]
        for a, kk in zip(att, comp[1:]):
            cur = a
            for _ in range(t - 1):                      # path to the star centre
                nx = node()
                edges.append((cur, nx))
                cur = nx
            edges += [(cur, node()) for _ in range(kk)]
    print(count[0], len(edges))
    print('\n'.join(f"{u} {v}" for u, v in edges))


main()
```

**Watch out.** A single structure per graph cannot reach every `P`: primes like 4999 would need a huge arm. Splitting into components fixes that. For `Q = 2`, three stars are not always enough, but the unbounded knapsack over star sizes always is. The hidden test recounts the triplets by BFS on the printed graph.

```stdin
4999 8
```

```check
P, Q = map(int, stdin.split())
lines = output.strip().split('\n')
N, M = map(int, lines[0].split())
assert 0 <= N <= 100 and 0 <= M <= 100 and len(lines) == M + 1
adj = [[] for _ in range(N + 1)]
for line in lines[1:]:
    u, v = map(int, line.split())
    assert 1 <= u <= N and 1 <= v <= N
    adj[u].append(v)
    adj[v].append(u)
dist = []
for s in range(1, N + 1):
    d = [-1] * (N + 1)
    d[s] = 0
    qq = [s]
    for x in qq:
        for y in adj[x]:
            if d[y] < 0:
                d[y] = d[x] + 1
                qq.append(y)
    dist.append(d)
cnt = 0
for i in range(1, N + 1):
    js = [j for j in range(i + 1, N + 1) if dist[i - 1][j] == Q]
    for x in range(len(js)):
        for y in range(x + 1, len(js)):
            if dist[js[x] - 1][js[y]] == Q:
                cnt += 1
assert cnt == P, cnt
```

### Array Construction

**Problem.** Find the lexicographically smallest array of `n` non-negative integers with sum `s` and total pairwise absolute difference `k`, or print `-1`.

**Idea.** The best array is sorted ascending: reordering a multiset never helps lexicographically. Describe a sorted array by its gaps: `A_0 = d_0` and `A_j = A_{j−1} + d_j`.
- **Sum.** Gap `d_j` is added to the `n − j` elements from position `j` on, so `s = Σ_j d_j·(n − j)`.
- **Differences.** Gap `d_j` (for `j ≥ 1`) separates `j` elements from `n − j`, so `k = Σ_j d_j·j·(n − j)`.

Lexicographic order on `A` is the same as on `d`. So choose `d_0, d_1, …` greedily, each as small as possible while the rest stays feasible. Feasibility of "gaps `j..n−1` produce `(s', k')`" is an unbounded 2-D knapsack, kept as NumPy boolean tables.

**Steps.**
1. Group the queries by `n`. For each `n`, build `reach[j]` (a `201 × 2001` boolean table) from `j = n−1` down to `0`.
2. If `reach[0][s][k]` is false, print `-1`. Otherwise pick each `d_j` greedily and print the prefix sums.

```python
import sys

import numpy as np


def build_reach(n, S, K):
    reach = [None] * (n + 1)
    cur = np.zeros((S + 1, K + 1), dtype=bool)
    cur[0, 0] = True
    reach[n] = cur.copy()
    for j in range(n - 1, -1, -1):
        w, v = n - j, j * (n - j)
        if v > K:                                 # this gap must stay 0
            reach[j] = cur.copy()
            continue
        for s in range(w, S + 1):                 # increasing s: unbounded copies
            if v:
                cur[s, v:] |= cur[s - w, :K + 1 - v]
            else:
                cur[s] |= cur[s - w]
        reach[j] = cur.copy()
    return reach


def construct(n, s, k, reach):
    if not reach[0][s, k]:
        return [-1]
    out, acc = [], 0
    for j in range(n):
        w, v = n - j, j * (n - j)
        t = 0
        while not reach[j + 1][s - t * w, k - t * v]:
            t += 1
        s -= t * w
        k -= t * v
        acc += t
        out.append(acc)
    return out


def main():
    data = sys.stdin.read().split()
    q = int(data[0])
    qs = [tuple(map(int, data[1 + 3 * i:4 + 3 * i])) for i in range(q)]
    S = max(s for _, s, _ in qs)
    K = max(k for _, _, k in qs)
    ans = [None] * q
    for n in sorted({n for n, _, _ in qs}):
        reach = build_reach(n, S, K)
        for i, (nn, s, k) in enumerate(qs):
            if nn == n:
                ans[i] = ' '.join(map(str, construct(n, s, k, reach)))
    print('\n'.join(ans))


main()
```

**Watch out.** The greedy loop for `d_j` always ends, because `reach[0][s][k]` guarantees that some choice works at every step. The sample input has leading spaces, so the program reads whitespace-separated tokens. Checked against a brute force over all sorted arrays.

```stdin
 1
 3 3 4
```

```stdout
0 1 2
```
