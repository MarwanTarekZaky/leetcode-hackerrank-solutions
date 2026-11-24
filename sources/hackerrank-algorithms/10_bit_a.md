## Bit Manipulation

### Lonely Integer

**Problem.** Every value appears twice except one. Find it.

**Idea.** `x ⊕ x = 0` and XOR is order-free, so XOR-ing everything cancels the pairs and leaves the lonely value.

**Steps.**
1. XOR all the numbers.

```python
import os
from functools import reduce
from operator import xor


def lonelyinteger(a):
    return reduce(xor, a, 0)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    a = list(map(int, input().rstrip().split()))
    fptr.write(str(lonelyinteger(a)) + '\n')
    fptr.close()
```

**Watch out.** This uses O(1) extra memory, unlike counting with a dictionary. It only works because every other value appears an *even* number of times.

```stdin
5
0 0 1 2 1
```

```stdout
2
```

### Maximizing XOR

**Problem.** Find the maximum `a ⊕ b` over `l ≤ a ≤ b ≤ r`.

**Idea.** Above the highest bit where `l` and `r` differ, every number in the range has the same bits, so the XOR is 0 there. At that bit, and below it, we can pick `a = prefix 0 111…` and `b = prefix 1 000…`, both inside `[l, r]`. So every lower bit can be made 1, and the answer is `2^{bitlen(l ⊕ r)} − 1`.

**Steps.**
1. Print `(1 << (l ^ r).bit_length()) − 1`.

```python
import os


def maximizingXor(l, r):
    return (1 << (l ^ r).bit_length()) - 1


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    l = int(input().strip())
    r = int(input().strip())
    fptr.write(str(maximizingXor(l, r)) + '\n')
    fptr.close()
```

**Watch out.** If `l = r`, the formula gives `2⁰ − 1 = 0`, which is correct. The double loop also works for the small limits, but the formula explains *why*.

```stdin
10
15
```

```stdout
7
```

### Counter game

**Problem.** Starting from `n`, a move halves `n` if it is a power of two, and otherwise subtracts the largest power of two below it. Louise moves first; whoever brings the counter to 1 wins.

**Idea.** Look at `n − 1` in binary.
- Halving a power of two removes one trailing zero of `n − 1`: `2^k − 1` becomes `2^{k−1} − 1`, which loses one set bit.
- Subtracting the top power removes the top set bit of `n − 1`.

So every move removes exactly one set bit of `n − 1`, and the game lasts `popcount(n − 1)` moves. Louise wins when that number is odd.

**Steps.**
1. Print `Louise` if `bin(n − 1).count('1')` is odd, else `Richard`.

```python
import os


def counterGame(n):
    return 'Louise' if bin(n - 1).count('1') % 2 else 'Richard'


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n = int(input().strip())
        fptr.write(counterGame(n) + '\n')
    fptr.close()
```

**Watch out.** `n = 1` means no move is possible, so Richard wins (popcount 0). `n` goes up to 2⁶⁴ − 1, which is no problem for Python integers.

```stdin
1
6
```

```stdout
Richard
```

### Xor-sequence

**Problem.** `A_0 = 0` and `A_x = A_{x−1} ⊕ x`. Answer up to 10⁵ queries `A_l ⊕ … ⊕ A_r` with `r ≤ 10¹⁵`.

**Idea.**
- **The sequence.** `A_x = 0 ⊕ 1 ⊕ … ⊕ x` follows the period-4 pattern `x, 1, x+1, 0`.
- **Its prefix XOR.** `G(x) = A_0 ⊕ … ⊕ A_x` has period 8:
  - `x mod 8 ∈ {0, 1}` → `x`;
  - `{2, 3}` → `2`;
  - `{4, 5}` → `x + 2`;
  - `{6, 7}` → `0`.

  This was checked against a direct computation.
- **A segment.** `G(r) ⊕ G(l − 1)`.

**Steps.**
1. Implement `G` with the table; answer each query in O(1).

```python
import sys


def G(x):
    m = x % 8
    if m in (0, 1):
        return x
    if m in (2, 3):
        return 2
    if m in (4, 5):
        return x + 2
    return 0


def main():
    data = sys.stdin.read().split()
    q = int(data[0])
    out = []
    for i in range(q):
        l, r = int(data[1 + 2 * i]), int(data[2 + 2 * i])
        out.append(G(r) ^ G(l - 1))
    print('\n'.join(map(str, out)))


main()
```

**Watch out.** `l ≥ 1`, so `G(l − 1)` never sees a negative index. With 10⁵ queries, read the whole input at once.

```stdin
3
2 4
2 8
5 9
```

```stdout
7
9
15
```

### Sum vs XOR

**Problem.** Count the `x` in `[0, n]` with `n + x = n ⊕ x`.

**Idea.** Addition equals XOR exactly when there are no carries, which means `x` has no set bit where `n` has one. Each zero bit of `n` below its top bit can be freely 0 or 1, and such an `x` is automatically `≤ n`. So the answer is `2^{(number of zero bits of n)}`, and `n = 0` gives 1.

**Steps.**
1. Count the zeros in `bin(n)` (excluding `0b`) and print `2` to that power, with `n = 0` handled separately.

```python
import os


def sumXor(n):
    if n == 0:
        return 1
    return 1 << bin(n)[2:].count('0')


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    fptr.write(str(sumXor(n)) + '\n')
    fptr.close()
```

**Watch out.** `bin(0)` is `'0b0'`, which would count one zero and answer 2, but only `x = 0` exists. Hence the special case.

```stdin
5
```

```stdout
2
```

### The Great XOR

**Problem.** Count the `a` with `0 < a < x` and `a ⊕ x > x`.

**Idea.** `a ⊕ x > x` exactly when the highest set bit of `a` sits where `x` has a 0, and `a < x` keeps that bit below `x`'s top bit. For each such zero bit `i`, there are `2^i` valid `a`. Adding them up gives all the zero bits of `x` below its top bit: `(2^{bitlen(x)} − 1) − x`.

**Steps.**
1. Print `((1 << x.bit_length()) − 1) ^ x`.

```python
import os


def theGreatXor(x):
    return ((1 << x.bit_length()) - 1) ^ x


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        x = int(input().strip())
        fptr.write(str(theGreatXor(x)) + '\n')
    fptr.close()
```

**Watch out.** `x` can be 10¹⁰, so no loop over `a`. The mask with the top bit's position flips exactly the zero bits.

```stdin
2
2
10
```

```stdout
1
5
```

### Flipping bits

**Problem.** Flip all 32 bits of an unsigned integer.

**Idea.** XOR with `2³² − 1` (all ones) flips every bit.

**Steps.**
1. Print `n ^ 0xFFFFFFFF`.

```python
import os


def flippingBits(n):
    return n ^ 0xFFFFFFFF


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        fptr.write(str(flippingBits(int(input().strip()))) + '\n')
    fptr.close()
```

**Watch out.** Python's `~n` gives `−n − 1` (infinite-width two's complement), not the 32-bit unsigned result. The mask fixes the width.

```stdin
3
2147483647
1
0
```

```stdout
2147483648
4294967294
4294967295
```

### Yet Another Minimax Problem

**Problem.** Arrange the numbers to minimise the largest XOR of neighbours.

**Idea.** If all the numbers are equal, the answer is 0. Otherwise take the highest bit where they disagree, and split them into group 0 and group 1 by that bit.
- Somewhere the arrangement must cross from one group to the other, and that XOR has the bit set.
- Neighbours inside a group XOR to below that bit.

So the best we can do is cross exactly once: list group 0, then group 1, joined by the pair with the **smallest cross XOR**. The answer is that minimum.

**Steps.**
1. Find the top differing bit and split.
2. For each value in the smaller group, take the minimum XOR against the whole other group at once with NumPy.

```python
import sys

import numpy as np


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    a = np.array(data[1:1 + n], dtype=np.int64)
    diff = np.bitwise_or.reduce(a ^ a[0])
    if diff == 0:
        print(0)
        return
    bit = 1 << (int(diff).bit_length() - 1)
    g0, g1 = a[(a & bit) == 0], a[(a & bit) != 0]
    if len(g0) > len(g1):
        g0, g1 = g1, g0
    print(min(int((g1 ^ int(x)).min()) for x in g0))


main()
```

**Watch out.** OR-ing `a_i ⊕ a_0` over all `i` finds the bits where some values disagree; its highest bit is the split bit. With `n ≤ 3000`, the pair search is at most 9·10⁶ XORs, done in NumPy.

```stdin
4
1 2 3 4
```

```stdout
5
```

### Sansa and XOR

**Problem.** XOR together the XORs of all contiguous subarrays.

**Idea.** Element `i` (0-based) lies in `(i+1)(n−i)` subarrays, and it survives the XOR only if that count is odd.
- If `n` is even, one of the two factors is always even, so everything cancels and the answer is 0.
- If `n` is odd, the count is odd exactly for the even indices.

**Steps.**
1. If `n` is even, print 0. Otherwise XOR `arr[0], arr[2], arr[4], …`.

```python
import os
from functools import reduce
from operator import xor


def sansaXor(arr):
    if len(arr) % 2 == 0:
        return 0
    return reduce(xor, arr[::2], 0)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n = int(input().strip())
        arr = list(map(int, input().rstrip().split()))
        fptr.write(str(sansaXor(arr)) + '\n')
    fptr.close()
```

**Watch out.** Listing all subarrays is O(n²) and too slow for `n = 10⁵`. Only the parity of each element's count matters.

```stdin
2
3
1 2 3
4
4 5 7 5
```

```stdout
2
0
```

### AND Product

**Problem.** Compute `a & (a+1) & … & b` for `b` up to 2³².

**Idea.** Any bit below the highest bit where `a` and `b` differ flips somewhere in the range, so it ends up 0. The result is the common binary prefix of `a` and `b`, padded with zeros.

**Steps.**
1. Shift both right until they are equal, then shift back.

```python
import os


def andProduct(a, b):
    shift = 0
    while a != b:
        a >>= 1
        b >>= 1
        shift += 1
    return a << shift


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    for _ in range(n):
        a, b = map(int, input().split())
        fptr.write(str(andProduct(a, b)) + '\n')
    fptr.close()
```

**Watch out.** Looping from `a` to `b` can take 4·10⁹ steps. The prefix loop takes at most 32.

```stdin
3
12 15
2 3
8 13
```

```stdout
12
2
8
```

### Winning Lottery Ticket

**Problem.** Count the pairs of tickets whose digits, together, include all of `0`–`9`.

**Idea.** Only the set of digits on each ticket matters, which is a 10-bit mask; there are 1024 of them. Count the tickets per mask. A pair of masks wins when `m₁ | m₂ = 1023`:
- different masks contribute `c[m₁]·c[m₂]`;
- the full mask with itself contributes `C(c, 2)`.

A 1024×1024 NumPy table does it at once.

**Steps.**
1. Build `c[mask]` from `set(ticket)`.
2. `total = (Σ_{m₁≠m₂, m₁|m₂ full} c c) / 2 + C(c[1023], 2)`.

```python
import sys

import numpy as np


def main():
    lines = sys.stdin.read().split()
    n = int(lines[0])
    cnt = np.zeros(1024, dtype=np.int64)
    for t in lines[1:1 + n]:
        mask = 0
        for ch in set(t):
            mask |= 1 << (ord(ch) - 48)
        cnt[mask] += 1
    masks = np.arange(1024)
    full = (masks[:, None] | masks[None, :]) == 1023
    np.fill_diagonal(full, False)
    pairs = int((np.outer(cnt, cnt) * full).sum()) // 2
    c = int(cnt[1023])
    print(pairs + c * (c - 1) // 2)


main()
```

**Watch out.** Ticket lines in the sample have trailing spaces; splitting on whitespace removes them. A ticket of 10⁶ characters is only scanned once (`set(t)`).

```stdin
5
129300455
5559948277
012334556
56789
123456879
```

```stdout
5
```

### Xoring Ninja

**Problem.** Sum the XOR of every non-empty subset, modulo 10⁹+7.

**Idea.** Look at one bit. If no element has it, it contributes nothing. If some element has it, exactly half of the `2^n` subsets have an odd number of elements with that bit: pair each subset with itself toggled at one such element. So bit `b` contributes `2^b · 2^{n−1}` exactly when it appears in the OR of all elements, and the answer is `OR · 2^{n−1}`.

**Steps.**
1. Print `(OR of the array) · 2^{n−1} mod p`.

```python
import os
from functools import reduce
from operator import or_

MOD = 10 ** 9 + 7


def xoringNinja(arr):
    return reduce(or_, arr, 0) * pow(2, len(arr) - 1, MOD) % MOD


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        input()
        arr = list(map(int, input().rstrip().split()))
        fptr.write(str(xoringNinja(arr)) + '\n')
    fptr.close()
```

**Watch out.** The empty subset has XOR 0, so including or excluding it changes nothing. Enumerating subsets is 2ⁿ, which is hopeless for `n = 10⁵`.

```stdin
1
3
1 2 3
```

```stdout
12
```

### Cipher

**Problem.** A bit string `b` of length `n` was written `k` times, shifted by `0..k−1`, and the columns were XOR-ed into `s` (length `n + k − 1`). Recover `b`.

**Idea.** `s[i]` is the XOR of `b[i−k+1 … i]`, the bits that exist. So `s[i] ⊕ s[i−1] = b[i] ⊕ b[i−k]`, and therefore `b[i] = s[i] ⊕ s[i−1] ⊕ b[i−k]`. Here `b[i−k]` counts as 0 when `i < k`, and `b[0] = s[0]`.

**Steps.**
1. Decode left to right with the recurrence; output the first `n` bits.

```python
import os


def cipher(k, s):
    n = len(s) - k + 1
    bits = list(map(int, s))
    b = [0] * n
    for i in range(n):
        v = bits[i] ^ (bits[i - 1] if i else 0) ^ (b[i - k] if i >= k else 0)
        b[i] = v
    return ''.join(map(str, b))


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    s = input().strip()
    fptr.write(cipher(k, s) + '\n')
    fptr.close()
```

**Watch out.** Keeping a running XOR of the last `k−1` decoded bits also works, but the two-term recurrence avoids window bookkeeping. `k = 1` gives `b = s`.

```stdin
7 4
1110100110
```

```stdout
1001010
```

### XOR Matrix

**Problem.** Each new row is `row[j] ⊕ row[(j+1) mod n]`. Given the first row, print row `m − 1` for `m` up to 10¹⁸.

**Idea.** One step maps `row` to `row ⊕ shift(row, 1)`. Over GF(2), applying it `2^p` times gives `row ⊕ shift(row, 2^p)`, because the middle binomial coefficients of `(1 + x)^{2^p}` are even. So write `m − 1` in binary and apply each power-of-two jump with a NumPy `roll`.

**Steps.**
1. For each set bit `p` of `m − 1`: `row ^= np.roll(row, −(2^p mod n))`.

```python
import sys

import numpy as np


def main():
    data = sys.stdin.read().split()
    n, m = int(data[0]), int(data[1])
    row = np.array(data[2:2 + n], dtype=np.int64)
    steps = m - 1
    p = 0
    while steps:
        if steps & 1:
            row = row ^ np.roll(row, -((1 << p) % n))
        steps >>= 1
        p += 1
    print(' '.join(map(str, row.tolist())))


main()
```

**Watch out.** The template writes `result` but stores `last_row`, so it crashes. This program reads and writes on its own. A shift of `2^p mod n` can be 0, which correctly makes the row XOR with itself (all zeros).

```stdin
4 2
6 7 1 3
```

```stdout
1 6 2 5
```
