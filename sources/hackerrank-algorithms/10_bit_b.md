## Bit Manipulation

### What's Next?

**Problem.** A binary number is given in run-length form: even indices count runs of 1s and odd indices runs of 0s, starting with 1s. Print the run-length form of the next larger number with the same number of 1s.

**Idea.** The classic "next number with the same popcount" step:
1. Find the rightmost `01` pair, which is the start of the last block of 1s that has a 0 to its left.
2. Turn it into `10`.
3. Move the other 1s of that block to the very end.

In run form, write the number as `P 0^z 1^c 0^w` (with `w = 0` if it ends in 1s). Then the answer is `P 0^{z−1} 1 0^{w+1} 1^{c−1}`. If there is no zero block before the last 1s, treat `z` as a virtual leading zero. Rebuild the runs, drop the empty ones, merge neighbours of the same bit and drop any leading zeros.

**Steps.**
1. Split off the trailing zeros `w`, the last ones block `c`, its zeros `z` and the prefix `P`.
2. Build the new run list and normalise it.

```python
import sys


def whats_next(arr):
    runs = [(1 - i % 2, v) for i, v in enumerate(arr)]       # (bit, length)
    w = 0
    if runs[-1][0] == 0:
        w = runs.pop()[1]
    c = runs.pop()[1]
    z = runs.pop()[1] if runs else 1                         # virtual leading zero
    new = runs + [(0, z - 1), (1, 1), (0, w + 1), (1, c - 1)]
    merged = []
    for bit, v in new:
        if v == 0:
            continue
        if merged and merged[-1][0] == bit:
            merged[-1] = (bit, merged[-1][1] + v)
        else:
            merged.append((bit, v))
    while merged and merged[0][0] == 0:
        merged.pop(0)
    return [v for _, v in merged]


def main():
    data = sys.stdin.read().split()
    t = int(data[0])
    pos = 1
    out = []
    for _ in range(t):
        n = int(data[pos])
        arr = list(map(int, data[pos + 1:pos + 1 + n]))
        pos += 1 + n
        c = whats_next(arr)
        out.append(str(len(c)))
        out.append(' '.join(map(str, c)))
    print('\n'.join(out))


main()
```

**Watch out.** The counts reach 10¹⁸, so the number cannot be expanded; only the last few runs change. When `c = 1` the final `1^{c−1}` block is empty, and when `z = 1` the zero block vanishes and the new 1 joins the prefix's last ones block. Merging handles both.

```stdin
1
5
4 1 3 2 4
```

```stdout
7
4 1 3 1 1 1 3
```

### String Transmission

**Problem.** Count the binary strings within Hamming distance `K` of the received string `s` (length `N ≤ 1000`) that are **not periodic**. Answer modulo 10⁹+7.

**Idea.** **Möbius inversion over the period.** Let `f(d)` be the number of strings within distance `K` of the form `t^{N/d}` (with `|t| = d`, where `d | N`). A string whose smallest period is `e` is counted in `f(d)` exactly when `e | d`. So the non-periodic count is `Σ_{d|N} μ(N/d)·f(d)`.

**Computing `f(d)`.** Position `j` of `t` controls the class `j, j+d, j+2d, …`. Choosing bit 0 there costs the number of ones in the class, and choosing 1 costs the number of zeros. A knapsack over the classes counts the ways with total cost `≤ K`, using one NumPy shift-add per class.

**Steps.**
1. For each divisor `d` of `N` with `μ(N/d) ≠ 0`, run the class knapsack and sum the counts up to `K`.
2. Combine them with the Möbius signs.

```python
import sys

import numpy as np

MOD = 10 ** 9 + 7


def mobius(m):
    res, p = 1, 2
    while p * p <= m:
        if m % p == 0:
            m //= p
            if m % p == 0:
                return 0
            res = -res
        p += 1
    return -res if m > 1 else res


def count_period(s, d, K):
    n = len(s)
    ways = np.zeros(K + 1, dtype=np.int64)
    ways[0] = 1
    for j in range(d):
        ones = sum(s[j::d])
        zeros = n // d - ones
        new = np.zeros(K + 1, dtype=np.int64)
        for cost in (ones, zeros):                   # bit 0 costs `ones`, bit 1 costs `zeros`
            if cost <= K:
                new[cost:] += ways[:K + 1 - cost]
        ways = new % MOD
    return int(ways.sum() % MOD)


def main():
    data = sys.stdin.read().split()
    t = int(data[0])
    pos = 1
    out = []
    for _ in range(t):
        n, k = int(data[pos]), int(data[pos + 1])
        s = [int(ch) for ch in data[pos + 2]]
        pos += 3
        total = 0
        for d in range(1, n + 1):
            if n % d == 0:
                mu = mobius(n // d)
                if mu:
                    total += mu * count_period(s, d, k)
        out.append(total % MOD)
    print('\n'.join(map(str, out)))


main()
```

**Watch out.** A length-1 string counts as non-periodic (it cannot be split into a smaller repeated piece), which the formula gives naturally with `d = N = 1`. The sample lines carry trailing spaces, so read tokens. `f(N)` alone is the plain count of strings within distance `K`.

```stdin
3
5 0
00000
3 1
001
3 3
101
```

```stdout
0
3
6
```

### A or B

**Problem.** Change at most `K` bits in total of `A` and `B` (hexadecimal, up to 2·10⁵ bits) so that `A' | B' = C`. Among the solutions, minimise `A'`, then `B'`. Print `-1` if impossible.

**Idea.**
- **Forced changes.** Where `C` has a 0, both bits must become 0. Where `C` has a 1 and both bits are 0, set `B`'s bit, which keeps `A` small. If these alone cost more than `K`, print `-1`.
- **Spend the rest on `A`.** Go from the highest bit down. Where `C = 1` and `A' = 1`:
  - if `B' = 1`, clearing `A`'s bit costs 1;
  - if `B' = 0`, moving the bit to `B` costs 2.

  Take every reduction that still fits the budget; a higher bit always matters more than all the lower ones.

Python's big integers make the forced part a few whole-number operations.

**Steps.**
1. Forced cost = `popcount(A & ~C) + popcount(B & ~C) + popcount(C & ~A & ~B)`.
2. `A' = A & C` and `B' = (B & C) | (C & ~A & ~B)`, then the greedy pass over the set bits of `A'`.

```python
import sys


def main():
    data = sys.stdin.read().split()
    q = int(data[0])
    pos = 1
    out = []
    for _ in range(q):
        k = int(data[pos])
        A, B, C = (int(data[pos + i], 16) for i in (1, 2, 3))
        pos += 4
        width = max(A.bit_length(), B.bit_length(), C.bit_length())
        mask = (1 << width) - 1
        notC = mask ^ C
        need = C & ~A & ~B & mask
        cost = bin(A & notC).count('1') + bin(B & notC).count('1') + bin(need).count('1')
        if cost > k:
            out.append('-1')
            continue
        left = k - cost
        A2 = A & C
        B2 = (B & C) | need
        bits = bin(A2)[2:]
        L = len(bits)
        for i, ch in enumerate(bits):
            if left == 0:
                break
            if ch == '1':
                bit = 1 << (L - 1 - i)
                if B2 & bit:
                    A2 ^= bit
                    left -= 1
                elif left >= 2:
                    A2 ^= bit
                    B2 |= bit
                    left -= 2
        out.append(format(A2, 'X'))
        out.append(format(B2, 'X'))
    print('\n'.join(out))


main()
```

**Watch out.** The output must be uppercase hexadecimal, and 0 prints as `0`. A bit that needs 2 changes is skipped when only 1 is left, but the scan continues because a lower bit may still be cleared for 1.

```stdin
3
8
2B
9F
58
5
B9
40
5A
2
91
BE
A8
```

```stdout
8
58
18
42
-1
```

### Manipulative Numbers

**Problem.** Find the largest `K` such that the numbers can be arranged in a **circle** with every neighbouring XOR `≥ 2^K`, or `-1`.

**Idea.** `x ⊕ y ≥ 2^K` exactly when `x >> K ≠ y >> K`. So group the numbers by `x >> K`; neighbours must come from different groups. A circular arrangement with no equal neighbours exists exactly when no group holds more than half the numbers. Try `K` from 30 downwards.

**Steps.**
1. For `K = 30 … 0`: if the largest group of `x >> K` has size `≤ n/2`, print `K`.
2. If none works, print `-1`.

```python
import sys
from collections import Counter


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    a = list(map(int, data[1:1 + n]))
    for k in range(30, -1, -1):
        if 2 * max(Counter(x >> k for x in a).values()) <= n:
            print(k)
            return
    print(-1)


main()
```

**Watch out.** The arrangement is a cycle, so the last and first elements are neighbours too. That is why the bound is `n/2` and not `(n+1)/2`. A value appearing more than `n/2` times makes every `K` fail, so the answer is `-1`.

```stdin
3
13 3 10
```

```stdout
2
```

### Stone Game

**Problem.** Bob may lower any piles (each new size between 0 and the original), keeping at least one pile unchanged, so that the Nim XOR becomes 0. Count the ways modulo 10⁹+7.

**Idea.** Let `cnt(b)` = number of tuples with `0 ≤ q_i ≤ b_i` and XOR 0. The answer is `cnt(p) − cnt(p − 1)`: all tuples, minus those where every pile changed.

**`cnt(b)` by bits from the top.** At bit `k`, a number whose bound has bit `k` set may either:
- **stay tight:** take bit 1 here, leaving `b_i mod 2^k + 1` choices below; or
- **drop:** take bit 0 here, making its lower `k` bits completely free.

If at least one number drops, the first dropped number can absorb any XOR of the lower bits. So the count is the product of the others' choices, where tight numbers give `b_i mod 2^k + 1` and later drops give `2^k`. A small DP over the numbers tracks (parity of tight bits, any dropped yet). If nobody drops, the bit-`k` parity must be even and we continue to bit `k−1` with all numbers still tight.

**Steps.**
1. `cnt(b)`: loop the bits from 30 down, adding the "someone drops" totals from the DP.
2. Print `cnt(p) − cnt(p−1)`.

```python
import sys

MOD = 10 ** 9 + 7


def cnt(b):
    total = 0
    for k in range(30, -1, -1):
        low = [(x & ((1 << k) - 1)) + 1 for x in b]
        # dp[parity][dropped]
        dp = [[1, 0], [0, 0]]
        for x, lw in zip(b, low):
            nd = [[0, 0], [0, 0]]
            for par in (0, 1):
                for dr in (0, 1):
                    w = dp[par][dr]
                    if not w:
                        continue
                    if x >> k & 1:
                        nd[par ^ 1][dr] = (nd[par ^ 1][dr] + w * lw) % MOD          # stay tight
                        f = (1 << k) % MOD if dr else 1                             # first drop absorbs
                        nd[par][1] = (nd[par][1] + w * f) % MOD
                    else:
                        nd[par][dr] = (nd[par][dr] + w * lw) % MOD
            dp = nd
        total = (total + dp[0][1]) % MOD
        if sum(x >> k & 1 for x in b) % 2:                                          # all tight: parity
            return total
    return (total + 1) % MOD                                                        # everything tight to the end


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    p = list(map(int, data[1:1 + n]))
    print((cnt(p) - cnt([x - 1 for x in p])) % MOD)


main()
```

**Watch out.**
- **Why the absorber is not multiplied.** The absorber's lower bits are forced by the others, so it contributes a factor 1 instead of `2^k`.
- **Ending.** If the loop survives every bit with all numbers tight, the tuple `q = b` itself has XOR 0 and counts once.

Checked against brute force over all tuples.

```stdin
3
1 2 3
```

```stdout
4
```

### 2's complement

**Problem.** Count the 1s in the 32-bit two's-complement forms of all integers in `[a, b]`.

**Idea.** A negative `x` is stored as the unsigned number `2³² + x`, so every range turns into unsigned ranges. Let `F(u)` be the number of 1 bits over `0..u`. Bit `i` repeats with period `2^{i+1}`, each period holding `2^i` ones; add the partial last period.

**Steps.**
1. `a ≥ 0`: `F(b) − F(a−1)`.
2. `b < 0`: `F(2³²+b) − F(2³²+a−1)`.
3. Mixed signs: `F(b) + F(2³²−1) − F(2³²+a−1)`.

```python
import sys

FULL = 1 << 32


def F(u):
    if u < 0:
        return 0
    total = 0
    for i in range(33):
        period = 1 << (i + 1)
        total += (u + 1) // period * (1 << i) + max(0, (u + 1) % period - (1 << i))
    return total


def twos(a, b):
    if a >= 0:
        return F(b) - F(a - 1)
    if b < 0:
        return F(FULL + b) - F(FULL + a - 1)
    return F(b) + F(FULL - 1) - F(FULL + a - 1)


def main():
    data = sys.stdin.read().split()
    t = int(data[0])
    out = [twos(int(data[1 + 2 * i]), int(data[2 + 2 * i])) for i in range(t)]
    print('\n'.join(map(str, out)))


main()
```

**Watch out.** `-1` is all ones (32 of them) and `-2³¹` is a single 1, which the mapping gets right without special cases. The function name in the template is misspelled (`twosCompliment`), which does not matter for a full program.

```stdin
3
-2 0
-3 4
-1 4
```

```stdout
63
99
37
```

### Changing Bits

**Problem.** Two `n`-bit numbers `a, b` are updated bit by bit. Answer `get_c idx` with bit `idx` of `a + b`, for up to 5·10⁵ commands.

**Idea.** `c[idx] = a[idx] ⊕ b[idx] ⊕ carry`, and the carry into `idx` is decided by the nearest lower position where `a` and `b` agree. If both bits are 1 there, a carry is generated; if both are 0, it is killed. Positions where they differ just pass the carry along, and if no position agrees, the carry is 0.

So keep the set of positions where the bits agree, and answer "largest member below `idx`". It is stored as 512-bit Python integers (one per block) plus a bitmask of the non-empty blocks, so a lookup is two `bit_length` calls.

**Steps.**
1. Store `a` and `b` as bit lists with index 0 as the least significant bit; mark the agreeing positions.
2. `set_*`: update the bit and its membership. `get_c`: find the predecessor and combine.

```python
import sys

SH = 9
SIZE = 1 << SH


def main():
    data = sys.stdin.buffer.read().split()
    n, q = int(data[0]), int(data[1])
    a = [int(ch) for ch in reversed(data[2].decode())]
    b = [int(ch) for ch in reversed(data[3].decode())]
    blocks = [0] * ((n >> SH) + 1)
    for i in range(n):
        if a[i] == b[i]:
            blocks[i >> SH] |= 1 << (i & (SIZE - 1))
    summary = 0
    for j, v in enumerate(blocks):
        if v:
            summary |= 1 << j

    def update(i):
        nonlocal summary
        j = i >> SH
        bit = 1 << (i & (SIZE - 1))
        if a[i] == b[i]:
            blocks[j] |= bit
        else:
            blocks[j] &= ~bit
        if blocks[j]:
            summary |= 1 << j
        else:
            summary &= ~(1 << j)

    def pred(idx):                                   # largest agreeing position < idx, or -1
        if idx > n:
            idx = n
        j = idx >> SH
        if j < len(blocks):
            m = blocks[j] & ((1 << (idx & (SIZE - 1))) - 1)
            if m:
                return (j << SH) + m.bit_length() - 1
        lower = summary & ((1 << j) - 1)
        if not lower:
            return -1
        jj = lower.bit_length() - 1
        return (jj << SH) + blocks[jj].bit_length() - 1

    out = []
    pos = 4
    for _ in range(q):
        cmd = data[pos]
        if cmd == b'get_c':
            idx = int(data[pos + 1])
            pos += 2
            if idx > n:                              # a + b has at most n + 1 bits
                out.append('0')
                continue
            p = pred(idx)
            carry = a[p] if p >= 0 else 0
            here = a[idx] ^ b[idx] if idx < n else 0
            out.append('1' if here ^ carry else '0')
        else:
            idx, x = int(data[pos + 1]), int(data[pos + 2])
            pos += 3
            if cmd == b'set_a':
                a[idx] = x
            else:
                b[idx] = x
            update(idx)
    print(''.join(out))


main()
```

**Watch out.** `get_c n` is the final carry, found by the same predecessor rule. `get_c n+1` is always 0, because `a + b` has at most `n + 1` bits. A Fenwick tree or a sorted list would also work, but at 5·10⁵ commands the per-call overhead matters in Python.

```stdin
5 5
00000
11111
set_a 0 1
get_c 5
get_c 1
set_b 2 0
get_c 5
```

```stdout
100
```

### XOR key

**Problem.** For each query `(a, l, r)`, find the maximum `a ⊕ x_j` over `l ≤ j ≤ r`. The values are at most 2¹⁵ and there are up to 5·10⁴ queries.

**Idea.** Greedy from the top bit: at each bit, prefer the value prefix that disagrees with `a`, provided some `x_j` with that prefix sits inside `[l, r]`. For every bit level, keep a map from each value prefix `x >> level` to the sorted list of indices having it. "Does this prefix occur in `[l, r]`?" is then one `bisect`.

**Steps.**
1. Build `pos[level][prefix]` = increasing index lists, for 16 levels.
2. Per query, walk 16 levels with the greedy, then print `a ⊕ value`.

```python
import sys
from bisect import bisect_left

BITS = 16


def main():
    data = sys.stdin.buffer.read().split()
    t = int(data[0])
    p = 1
    out = []
    for _ in range(t):
        n, q = int(data[p]), int(data[p + 1])
        x = list(map(int, data[p + 2:p + 2 + n]))
        p += 2 + n
        pos = [dict() for _ in range(BITS + 1)]
        for idx, v in enumerate(x, 1):
            for lev in range(BITS + 1):
                pos[lev].setdefault(v >> lev, []).append(idx)
        for _ in range(q):
            a, l, r = int(data[p]), int(data[p + 1]), int(data[p + 2])
            p += 3
            pref = 0
            for lev in range(BITS, -1, -1):
                want = (pref << 1) | (1 - (a >> lev & 1))
                lst = pos[lev].get(want)
                if lst is not None:
                    i = bisect_left(lst, l)
                    if i < len(lst) and lst[i] <= r:
                        pref = want
                        continue
                pref = (pref << 1) | (a >> lev & 1)
            out.append(a ^ pref)
    print('\n'.join(map(str, out)))


main()
```

**Watch out.** Values can equal 2¹⁵ exactly, so 17 bit levels (0..16) are needed, not 15. The fallback prefix always exists in the range, because the previous prefix did.

```stdin
1
15 8
1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
10 6 10
1023 7 7
33 5 8
182 5 10
181 1 13
5 10 15
99 8 9
33 10 14
```

```stdout
13
1016
41
191
191
15
107
47
```

### Maximizing the Function

**Problem.** For a 0/1 array, `g(x, y)` counts the subarrays of `[x, y]` with XOR 1. Each query may flip at most `k` bits; print the maximum `g`.

**Idea.** Use the prefix parities `P_{x−1}, P_x, …, P_y` (`L + 1` values, where `L = y − x + 1`). A subarray has XOR 1 exactly when its two end prefixes differ, so `g = c₀·c₁`, where `c₀` and `c₁` count the 0 and 1 parities.
- **`k = 0`.** Read `c₁` from prefix sums of the parities.
- **`k ≥ 1`.** Flipping one bit toggles a suffix of the parity list, and moving that cut by one changes `c₁` by ±1. That walk always passes through the balanced split, so the answer is `⌊(L+1)/2⌋·⌈(L+1)/2⌉`, the largest possible product.

This was verified by brute force.

**Steps.**
1. Prefix parities and their running sums (NumPy), vectorised over all queries.
2. Answer with `c₀·c₁` for `k = 0` and the balanced product otherwise.

```python
import sys

import numpy as np


def main():
    data = np.array(sys.stdin.buffer.read().split(), dtype=np.int64)
    n, q = int(data[0]), int(data[1])
    a = data[2:2 + n]
    qs = data[2 + n:2 + n + 3 * q].reshape(q, 3)
    par = np.zeros(n + 1, dtype=np.int64)
    par[1:] = np.cumsum(a) & 1                       # P_0 .. P_n (P_0 = empty prefix)
    ones = np.zeros(n + 2, dtype=np.int64)
    ones[1:] = np.cumsum(par)                        # ones[i] = count of 1s in par[0..i-1]
    x, y, k = qs[:, 0], qs[:, 1], qs[:, 2]
    m = y - x + 2                                    # parities par[x] .. par[y+1]
    c1 = ones[y + 2] - ones[x]
    res = np.where(k > 0, (m // 2) * ((m + 1) // 2), c1 * (m - c1))
    sys.stdout.write('\n'.join(map(str, res.tolist())) + '\n')


main()
```

**Watch out.** With up to 5·10⁵ queries, reading the input in one NumPy call and answering vectorised is what keeps Python fast enough. Only "`k ≥ 1`" matters; extra flips never beat the balanced split.

```stdin
3 2
0 0 1
0 2 1
0 1 0
```

```stdout
4
0
```

### XOR Subsequences

**Problem.** Over all contiguous subarrays, find the XOR value that occurs most often (the smallest one on ties) and its frequency. Values are below 2¹⁶.

**Idea.** A subarray's XOR is `P_i ⊕ P_j` for two prefix values. Let `c[u]` count the prefix values. The number of ordered prefix pairs with XOR `w` is the XOR-convolution `Σ_u c[u]·c[u ⊕ w]`, computed with a Walsh–Hadamard transform of size 65536 in NumPy. Then:
- for `w ≠ 0`, halve it (unordered pairs);
- for `w = 0`, subtract the `n + 1` self-pairs, then halve.

**Steps.**
1. Count the prefix XORs (including the empty prefix 0).
2. Transform, square, transform back, divide by 65536.
3. Fix the pair counting and take the first maximum.

```python
import sys

import numpy as np


def wht(v):
    h = 1
    n = len(v)
    while h < n:
        v = v.reshape(-1, 2, h)
        a, b = v[:, 0, :].copy(), v[:, 1, :].copy()
        v[:, 0, :], v[:, 1, :] = a + b, a - b
        v = v.reshape(n)
        h *= 2
    return v


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    a = np.array(data[1:1 + n], dtype=np.int64)
    pre = np.zeros(n + 1, dtype=np.int64)
    pre[1:] = np.bitwise_xor.accumulate(a)
    c = np.bincount(pre, minlength=1 << 16).astype(np.int64)
    f = wht(c.copy())
    pairs = wht(f * f) // (1 << 16)
    pairs[0] -= n + 1
    pairs //= 2
    best = int(np.argmax(pairs))
    print(best, int(pairs[best]))


main()
```

**Watch out.** The transformed values reach about `10¹⁰` after squaring, and the inverse sums 65536 of them, so they stay inside `int64`. Each array value is on its own line in the input.

```stdin
4
2
1
1
3
```

```stdout
1 3
```

### Iterate It

**Problem.** Repeatedly replace the array with all differences `|x − y|` of distinct pairs, and count the rounds until it is empty (or `-1` if it never empties).

**Idea.** Only the **set** of values matters. The maximum strictly decreases each round, so the loop always ends and `-1` never happens.
- **Scaling.** Divide by the gcd `g`; the round count does not change.
- **The full set.** Once the set is `{1, 2, …, M}`, it shrinks by exactly one value per round, so `M` more rounds remain.
- **Otherwise.** Simulate one round. The set of differences is the support of the autocorrelation of the indicator vector, computed with an FFT, or with a direct NumPy table when the set is small.

In practice the set becomes full after very few rounds.

**Steps.**
1. Loop: divide by the gcd. If the set is `{1..M}`, add `M` and stop. Otherwise compute the difference set and count one round.

```python
import sys
from functools import reduce
from math import gcd

import numpy as np


def diffs(vals):
    if len(vals) <= 2000:
        d = np.abs(np.subtract.outer(vals, vals)).ravel()
        return np.unique(d[d > 0])
    M = int(vals.max())
    size = 1
    while size < 2 * (M + 1):
        size *= 2
    ind = np.zeros(size)
    ind[vals] = 1.0
    f = np.fft.rfft(ind, size)
    corr = np.fft.irfft(f * np.conj(f), size)[1:M + 1]
    return np.flatnonzero(corr > 0.5) + 1


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    vals = np.unique(np.array(data[1:1 + n], dtype=np.int64))
    rounds = 0
    while len(vals):
        g = reduce(gcd, vals.tolist())
        vals = vals // g
        M = int(vals[-1])
        if len(vals) == M:                  # {1, 2, ..., M}
            rounds += M
            break
        vals = diffs(vals)
        rounds += 1
    print(rounds)


main()
```

**Watch out.** A single value gives one round (the next array is empty). The FFT correlation counts pairs as floats, so a difference is present when its count is above 0.5. Exact counts are not needed. Checked against the literal simulation on random small inputs.

```stdin
3
1 3 4
```

```stdout
4
```

### Hamming Distance

**Problem.** A string of `a`/`b` (length `N ≤ 5·10⁴`) receives up to 7.5·10⁴ commands: assign a range, swap two fragments, reverse a range, print a substring, and Hamming distance between two equal-length substrings.

**Idea.** Store the string as a **bitset in one Python integer** (bit `i` = character `i`, with `b` = 1). Every command becomes a few shifts and masks that run in C over about 800 machine words:
- **Hamming distance:** popcount of the XOR of the two extracted slices.
- **Assign and swap:** cut the integer into pieces and reassemble.
- **Reverse:** there is no fast bit reversal, so also keep the **reversed string** as a second bitset. Reversing `[l, r]` swaps that slice with the matching slice of the reversed copy. Every other command updates both copies.

**Steps.**
1. `get(x, l, len)` and `put(x, l, len, v)` helpers on 0-based slices.
2. Apply each command to `S` (and mirror it on `R`); print `W` slices via `format(…, 'b')`.

```python
import sys


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    s = data[1].decode()
    m = int(data[2])
    S = int(s[::-1].replace('a', '0').replace('b', '1'), 2)        # bit i = char i
    R = int(s.replace('a', '0').replace('b', '1'), 2)              # reversed string
    full = (1 << n) - 1

    def get(x, l, ln):
        return (x >> l) & ((1 << ln) - 1)

    def put(x, l, ln, v):
        mask = ((1 << ln) - 1) << l
        return (x & ~mask & full) | (v << l)

    def rev_pos(l, r):                       # 0-based [l, r] in S -> start in R
        return n - 1 - r

    out = []
    pos = 3
    table = str.maketrans('01', 'ab')
    for _ in range(m):
        op = data[pos]
        if op == b'C':
            l, r, ch = int(data[pos + 1]) - 1, int(data[pos + 2]) - 1, data[pos + 3]
            pos += 4
            ln = r - l + 1
            v = (1 << ln) - 1 if ch == b'b' else 0
            S = put(S, l, ln, v)
            R = put(R, rev_pos(l, r), ln, v)
        elif op == b'S':
            l1, r1, l2, r2 = (int(data[pos + i]) - 1 for i in range(1, 5))
            pos += 5
            ln = r2 - l1 + 1
            a_len, mid_len, b_len = r1 - l1 + 1, l2 - r1 - 1, r2 - l2 + 1
            seg = get(S, l1, ln)
            A = seg & ((1 << a_len) - 1)
            Mid = (seg >> a_len) & ((1 << mid_len) - 1)
            B = seg >> (a_len + mid_len)
            S = put(S, l1, ln, B | (Mid << b_len) | (A << (b_len + mid_len)))
            rs = rev_pos(l1, r2)                 # in R the same block reads reversed
            seg = get(R, rs, ln)
            Br = seg & ((1 << b_len) - 1)
            Mr = (seg >> b_len) & ((1 << mid_len) - 1)
            Ar = seg >> (b_len + mid_len)
            R = put(R, rs, ln, Ar | (Mr << a_len) | (Br << (a_len + mid_len)))
        elif op == b'R':
            l, r = int(data[pos + 1]) - 1, int(data[pos + 2]) - 1
            pos += 3
            ln = r - l + 1
            rs = rev_pos(l, r)
            x, y = get(S, l, ln), get(R, rs, ln)
            S = put(S, l, ln, y)
            R = put(R, rs, ln, x)
        elif op == b'W':
            l, r = int(data[pos + 1]) - 1, int(data[pos + 2]) - 1
            pos += 3
            ln = r - l + 1
            out.append(format(get(S, l, ln), f'0{ln}b')[::-1].translate(table))
        else:
            l1, l2, ln = int(data[pos + 1]) - 1, int(data[pos + 2]) - 1, int(data[pos + 3])
            pos += 4
            out.append(str(bin(get(S, l1, ln) ^ get(S, l2, ln)).count('1')))
    print('\n'.join(out))


main()
```

**Watch out.**
- **Slice positions.** In the reversed copy, the slice for `[l, r]` starts at `n−1−r`, and its pieces appear in mirrored order. That is why the swap rebuilds `R` with the roles of the two fragments exchanged.
- **Testing.** The whole thing is checked against a plain list implementation on random command sequences.

```stdin
10
aabbbabbab
6
R 1 5
W 3 8
C 4 4 a
H 2 1 9
S 5 9 10 10
H 1 2 9
```

```stdout
baaabb
4
5
```

### Mixing proteins

**Problem.** Each second, every protein in a ring becomes `table[p_i][p_{i+1}]`. Print the ring after `K ≤ 10⁹` seconds, with `N ≤ 10⁶`.

**Idea.** Map `A, B, C, D` to `0, 1, 2, 3`: the table is exactly XOR. So one second is `s ← s ⊕ shift(s, 1)`, the same map as in *XOR Matrix*. Over GF(2), `2^p` seconds equal `s ⊕ shift(s, 2^p)`. Apply the set bits of `K` with NumPy `roll`.

**Steps.**
1. Convert the letters to a NumPy array of 0..3.
2. For each set bit `p` of `K`: `s ^= roll(s, −(2^p mod N))`. Convert back.

```python
import sys

import numpy as np


def main():
    data = sys.stdin.buffer.read().split()
    n, k = int(data[0]), int(data[1])
    s = np.frombuffer(data[2], dtype=np.uint8) - ord('A')
    p = 0
    while k:
        if k & 1:
            s = s ^ np.roll(s, -((1 << p) % n))
        k >>= 1
        p += 1
    print((s + ord('A')).astype(np.uint8).tobytes().decode())


main()
```

**Watch out.** Spotting that the table is XOR is the whole problem; a direct simulation is 10⁹ × 10⁶. A shift of `2^p mod N = 0` turns the ring into all `A`, which is the correct result (`x ⊕ x = 0`).

```stdin
5 15
AAAAD
```

```stdout
DDDDA
```
