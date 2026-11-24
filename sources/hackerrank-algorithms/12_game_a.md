## Game Theory

### Game of Stones

**Problem.** Players remove 2, 3 or 5 stones from one pile; whoever cannot move loses. Does the first player win with `n` stones?

**Idea.** Mark positions as winning or losing: a position is winning if some move reaches a losing one. Tabulating gives a period of 7: the losing positions are exactly `n mod 7 ∈ {0, 1}`.

**Steps.**
1. Print `Second` if `n % 7` is 0 or 1, else `First`.

```python
import os


def gameOfStones(n):
    return 'Second' if n % 7 in (0, 1) else 'First'


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        fptr.write(gameOfStones(int(input().strip())) + '\n')
    fptr.close()
```

**Watch out.** A short win/lose table up to 20 shows the pattern and serves as the proof. `n = 1` is losing because no move is possible.

```stdin
8
1
2
3
4
5
6
7
10
```

```stdout
Second
First
First
First
First
First
Second
First
```

### Tower Breakers

**Problem.** There are `n` towers of height `m`. A move reduces a tower to a proper divisor of its height; whoever cannot move loses. Print the winner (1 or 2).

**Idea.** If `m = 1`, nobody can move and player 2 wins. Otherwise, with an even number of towers, player 2 mirrors every move on a partner tower and wins. With an odd number, player 1 knocks one tower down to 1 and then mirrors on the remaining even group.

**Steps.**
1. Print 2 if `m == 1` or `n` is even, else 1.

```python
import os


def towerBreakers(n, m):
    return 2 if m == 1 or n % 2 == 0 else 1


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n, m = map(int, input().split())
        fptr.write(str(towerBreakers(n, m)) + '\n')
    fptr.close()
```

**Watch out.** The mirror (copy) strategy is the whole proof; no Grundy numbers are needed when all towers are equal.

```stdin
2
2 2
1 4
```

```stdout
2
1
```

### A Chessboard Game

**Problem.** A coin on a 15×15 board moves to `(x−2, y±1)` or `(x±1, y−2)`, staying on the board. Whoever cannot move loses.

**Idea.** Every move lowers `x + y`, so compute the win/lose table by increasing `x + y`. The Grundy table also serves *Chessboard Game, Again!*. The losing cells turn out to be those with `x mod 4 ∈ {1, 2}` and `y mod 4 ∈ {1, 2}`, but computing the table avoids relying on that.

**Steps.**
1. Build the Grundy table once (memoised).
2. Print `First` if `G(x, y) ≠ 0`.

```python
import os
from functools import lru_cache

MOVES = [(-2, 1), (-2, -1), (1, -2), (-1, -2)]


@lru_cache(maxsize=None)
def grundy(x, y):
    seen = set()
    for dx, dy in MOVES:
        nx, ny = x + dx, y + dy
        if 1 <= nx <= 15 and 1 <= ny <= 15:
            seen.add(grundy(nx, ny))
    g = 0
    while g in seen:
        g += 1
    return g


def chessboardGame(x, y):
    return 'First' if grundy(x, y) else 'Second'


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        x, y = map(int, input().split())
        fptr.write(chessboardGame(x, y) + '\n')
    fptr.close()
```

**Watch out.** Two of the moves increase one coordinate, but the sum `x + y` always drops, so the recursion terminates.

```stdin
3
5 2
5 3
8 8
```

```stdout
Second
First
First
```

### Introduction to Nim Game

**Problem.** Classic Nim: remove any positive number of stones from one pile; whoever takes the last stone wins.

**Idea.** **Bouton's theorem:** the player to move loses exactly when the XOR of the pile sizes is 0.

**Steps.**
1. Print `First` if the XOR is non-zero.

```python
import os
from functools import reduce
from operator import xor


def nimGame(pile):
    return 'First' if reduce(xor, pile, 0) else 'Second'


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    g = int(input().strip())
    for _ in range(g):
        input()
        pile = list(map(int, input().rstrip().split()))
        fptr.write(nimGame(pile) + '\n')
    fptr.close()
```

**Watch out.** From XOR 0, every move makes it non-zero. From a non-zero XOR, the move that sets some pile to `pile ⊕ X` brings it back to 0. That is the entire strategy.

```stdin
2
2
1 1
3
2 1 4
```

```stdout
Second
First
```

### Misère Nim

**Problem.** Nim where whoever takes the **last** stone **loses**.

**Idea.** It plays exactly like normal Nim until all piles are size 1. So:
- if every pile is 1, the first player wins exactly when the number of piles is even;
- otherwise the usual XOR rule applies.

**Steps.**
1. All ones: `First` if `n` is even. Otherwise: `First` if the XOR is non-zero.

```python
import os
from functools import reduce
from operator import xor


def misereNim(s):
    if all(x == 1 for x in s):
        return 'First' if len(s) % 2 == 0 else 'Second'
    return 'First' if reduce(xor, s, 0) else 'Second'


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        input()
        s = list(map(int, input().rstrip().split()))
        fptr.write(misereNim(s) + '\n')
    fptr.close()
```

**Watch out.** The winner of the normal game steers so that, when only 1-piles remain, the opponent faces an odd number of them.

```stdin
2
2
1 1
3
2 1 3
```

```stdout
First
Second
```

### Nimble Game

**Problem.** Coins sit on squares `0..n−1` (square `i` has `c_i` coins). A move slides one coin to any square to its left. Whoever cannot move loses.

**Idea.** Each coin is a Nim pile of size equal to its square index (moving left is reducing the pile). Pairs of coins on the same square cancel in the XOR, so XOR the index `i` for each square with an odd number of coins.

**Steps.**
1. XOR `i` over the squares with `c_i` odd; print `First` if the result is non-zero.

```python
import os


def nimbleGame(s):
    x = 0
    for i, c in enumerate(s):
        if c % 2:
            x ^= i
    return 'First' if x else 'Second'


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        input()
        s = list(map(int, input().rstrip().split()))
        fptr.write(nimbleGame(s) + '\n')
    fptr.close()
```

**Watch out.** Coins on square 0 can never move, which matches a pile of size 0. Counts can be large; only their parity matters.

```stdin
2
5
0 2 3 0 6
4
0 0 0 0
```

```stdout
First
Second
```

### Alice and Bob's Silly Game

**Problem.** From `{1..n}`, a move picks a prime `p` still in the set and removes it with all its multiples. Whoever cannot move loses.

**Idea.** Removing a prime's multiples never removes another prime. So every prime is exactly one move, the game lasts as many moves as there are primes `≤ n`, and Alice wins when that count is odd.

**Steps.**
1. Sieve up to the largest `n`, take prefix counts of primes, and print `Alice` for an odd count.

```python
import sys


def main():
    data = list(map(int, sys.stdin.read().split()))
    g = data[0]
    ns = data[1:1 + g]
    N = max(ns)
    sieve = bytearray([1]) * (N + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(N ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(range(i * i, N + 1, i)))
    cnt = [0] * (N + 1)
    c = 0
    for i in range(N + 1):
        c += sieve[i]
        cnt[i] = c
    print('\n'.join('Alice' if cnt[n] % 2 else 'Bob' for n in ns))


main()
```

**Watch out.** `n = 1` has no primes, so Bob wins without a single move. Build the sieve once for all games.

```stdin
3
1
2
5
```

```stdout
Bob
Alice
Alice
```

### Poker Nim

**Problem.** Nim where a player may also **add** chips to a pile (at most `k` times per player). Who wins?

**Idea.** Adding chips is reversible: whatever the opponent adds, you remove on your next move. The additions are limited, so the game still ends, and the winner of plain Nim keeps winning. The answer is the Nim XOR rule.

**Steps.**
1. Print `First` if the XOR of `c` is non-zero.

```python
import os
from functools import reduce
from operator import xor


def pokerNim(k, c):
    return 'First' if reduce(xor, c, 0) else 'Second'


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n, k = map(int, input().split())
        c = list(map(int, input().rstrip().split()))
        fptr.write(pokerNim(k, c) + '\n')
    fptr.close()
```

**Watch out.** `k` does not matter at all. This "reversible move" argument shows up again in *Vertical Rooks*.

```stdin
2
2 5
1 2
3 5
2 1 3
```

```stdout
First
Second
```

### Tower Breakers, Revisited!

**Problem.** A move reduces a tower of height `X` to a proper divisor `Y` of `X`. Several towers; whoever cannot move loses.

**Idea.** A tower is equivalent to a Nim pile of size `Ω(X)`, the number of prime factors counted with multiplicity: moving to a divisor removes any positive number of them. So XOR the `Ω` values.

**Steps.**
1. Sieve the smallest prime factor up to the maximum height and compute `Ω` by repeated division.
2. Print 1 if the XOR is non-zero, else 2.

```python
import sys


def main():
    data = list(map(int, sys.stdin.read().split()))
    t = data[0]
    pos = 1
    tests = []
    for _ in range(t):
        n = data[pos]
        tests.append(data[pos + 1:pos + 1 + n])
        pos += 1 + n
    N = max(max(h) for h in tests)
    spf = list(range(N + 1))
    for i in range(2, int(N ** 0.5) + 1):
        if spf[i] == i:
            for j in range(i * i, N + 1, i):
                if spf[j] == j:
                    spf[j] = i
    omega = [0] * (N + 1)
    for x in range(2, N + 1):
        omega[x] = omega[x // spf[x]] + 1
    out = []
    for h in tests:
        x = 0
        for v in h:
            x ^= omega[v]
        out.append('1' if x else '2')
    print('\n'.join(out))


main()
```

**Watch out.** It is not the number of *divisors*: reducing 12 to 6 removes one prime factor, and reducing 12 to 1 removes three. The sample input lines carry trailing spaces; reading tokens handles that.

```stdin
2
2
1 2
3
1 2 3
```

```stdout
1
2
```

### Tower Breakers, Again!

**Problem.** A move breaks a tower of height `X` into `Y > 1` towers of equal height `Z` (`Y·Z = X`). Several towers; whoever cannot move loses.

**Idea.** Use Grundy numbers.
- **Even `Y`.** The `Y` equal towers cancel in pairs, so the result is worth 0.
- **Odd `Y`.** The result is worth `g(Z)`.

So `g(X) = mex({0 for even divisors Y > 1} ∪ {g(X/Y) for odd divisors Y > 1})`. Precompute it up to 10⁵ with a divisor sieve.

**Steps.**
1. For every `Z` and every multiple `X = Y·Z` (`Y ≥ 2`), record the option.
2. Fill `g` in increasing `X`; XOR over the towers.

```python
import sys


def main():
    data = list(map(int, sys.stdin.read().split()))
    t = data[0]
    pos = 1
    tests = []
    for _ in range(t):
        n = data[pos]
        tests.append(data[pos + 1:pos + 1 + n])
        pos += 1 + n
    N = max(max(h) for h in tests)
    divs = [[] for _ in range(N + 1)]            # divs[X] = list of Z with Y = X/Z >= 2
    for z in range(1, N // 2 + 1):
        for x in range(2 * z, N + 1, z):
            divs[x].append(z)
    g = [0] * (N + 1)
    for x in range(2, N + 1):
        seen = set()
        for z in divs[x]:
            seen.add(g[z] if (x // z) % 2 else 0)
        v = 0
        while v in seen:
            v += 1
        g[x] = v
    out = []
    for h in tests:
        s = 0
        for v in h:
            s ^= g[v]
        out.append('1' if s else '2')
    print('\n'.join(out))


main()
```

**Watch out.** The divisor lists total about `N ln N ≈ 1.2·10⁶` entries, which is fine. Height 1 has no move (`g = 0`).

```stdin
2
2
1 2
3
1 2 3
```

```stdout
1
2
```

### Zero-Move Nim

**Problem.** Nim where each non-empty pile also allows one "zero move" (removing nothing), usable once per pile by either player. Does the first player win?

**Idea.** A pile with its zero move still available has Grundy value `p + 1` for odd `p` and `p − 1` for even `p ≥ 2` (0 stays 0). Brute force shows this. The zero move links each pair `(2k−1, 2k)` and swaps their values. XOR these values.

**Steps.**
1. Map each pile to `p+1` (odd) or `p−1` (even); print `W` if the XOR is non-zero.

```python
import sys


def main():
    data = list(map(int, sys.stdin.read().split()))
    g = data[0]
    pos = 1
    out = []
    for _ in range(g):
        n = data[pos]
        p = data[pos + 1:pos + 1 + n]
        pos += 1 + n
        x = 0
        for v in p:
            x ^= v + 1 if v % 2 else v - 1
        out.append('W' if x else 'L')
    print('\n'.join(out))


main()
```

**Watch out.** After its zero move is used, a pile is plain Nim again. The formula above already accounts for that through the mex.

```stdin
2
2
1 2
2
2 2
```

```stdout
W
L
```

### Chessboard Game, Again!

**Problem.** Same moves as *A Chessboard Game*, but with `k` coins (a cell may hold several). A move moves one coin; whoever cannot move loses.

**Idea.** A sum of independent games: XOR the Grundy numbers of all the coins.

**Steps.**
1. Grundy table for 15×15 (memoised); XOR over the coins.

```python
import sys
from functools import lru_cache

MOVES = [(-2, 1), (-2, -1), (1, -2), (-1, -2)]


@lru_cache(maxsize=None)
def grundy(x, y):
    seen = set()
    for dx, dy in MOVES:
        nx, ny = x + dx, y + dy
        if 1 <= nx <= 15 and 1 <= ny <= 15:
            seen.add(grundy(nx, ny))
    g = 0
    while g in seen:
        g += 1
    return g


def main():
    data = list(map(int, sys.stdin.read().split()))
    t = data[0]
    pos = 1
    out = []
    for _ in range(t):
        k = data[pos]
        x = 0
        for i in range(k):
            x ^= grundy(data[pos + 1 + 2 * i], data[pos + 2 + 2 * i])
        pos += 1 + 2 * k
        out.append('First' if x else 'Second')
    print('\n'.join(out))


main()
```

**Watch out.** Two coins on the same cell cancel each other. The win/lose bit of each coin is not enough; you need the full Grundy value.

```stdin
2
3
5 4
5 8
8 2
6
7 1
7 2
7 3
7 4
7 4
7 4
```

```stdout
First
Second
```

### Digits Square Board

**Problem.** An `N×N` board (`N ≤ 30`) of digits. A move cuts a piece that has more than one cell and contains a non-prime digit into two pieces along a grid line. Whoever cannot move loses.

**Idea.** Every rectangle is a game.
- **Dead rectangles.** A rectangle that is 1×1 or contains only primes (2, 3, 5, 7) has Grundy value 0.
- **Live rectangles.** Otherwise the value is the mex of `g(part₁) ⊕ g(part₂)` over all cuts.

There are about `N⁴/4` rectangles. Compute them by size `(h, w)`, with NumPy across all positions at once: each cut is an XOR of two shifted arrays, OR-ed into a bitmask of seen values, and the mex is the lowest unset bit.

**Steps.**
1. 2-D prefix sums of "non-prime" cells to tell live rectangles from dead ones.
2. For `h, w` increasing, build `G[h][w]` (indexed by top-left corner) from smaller sizes.

```python
import sys

import numpy as np


def solve(board):
    n = len(board)
    nonprime = np.array([[0 if v in (2, 3, 5, 7) else 1 for v in row] for row in board], dtype=np.int64)
    pre = np.zeros((n + 1, n + 1), dtype=np.int64)
    pre[1:, 1:] = nonprime.cumsum(0).cumsum(1)
    G = {}
    for h in range(1, n + 1):
        for w in range(1, n + 1):
            rows, cols = n - h + 1, n - w + 1
            mask = np.zeros((rows, cols), dtype=np.int64)
            for a in range(1, h):                   # horizontal cut: a rows on top
                top, bot = G[(a, w)], G[(h - a, w)]
                mask |= np.left_shift(1, top[:rows, :] ^ bot[a:a + rows, :])
            for b in range(1, w):                   # vertical cut: b columns on the left
                lft, rgt = G[(h, b)], G[(h, w - b)]
                mask |= np.left_shift(1, lft[:, :cols] ^ rgt[:, b:b + cols])
            free = ~mask
            low = free & -free                      # lowest unset bit of mask
            mex = np.log2(low.astype(np.float64)).astype(np.int64)
            live = (pre[h:h + rows, w:w + cols] - pre[:rows, w:w + cols]
                    - pre[h:h + rows, :cols] + pre[:rows, :cols]) > 0
            g = np.where(live & ((h > 1) | (w > 1)), mex, 0)
            G[(h, w)] = g
    return 'First' if G[(n, n)][0, 0] else 'Second'


def main():
    data = list(map(int, sys.stdin.read().split()))
    t = data[0]
    pos = 1
    out = []
    for _ in range(t):
        n = data[pos]
        board = [data[pos + 1 + i * n:pos + 1 + (i + 1) * n] for i in range(n)]
        pos += 1 + n * n
        out.append(solve(board))
    print('\n'.join(out))


main()
```

**Watch out.** The Grundy values stay small (well below 62), so a 64-bit mask per rectangle is enough. `free & −free` isolates the lowest unset bit, and its `log2` is exact for powers of two. HackerRank gives Python 18 seconds here; the vectorised version needs only a fraction of that.

```stdin
2
3
2 7 5
2 7 5
7 7 7
2
4 3
1 2
```

```stdout
Second
First
```

### Fun Game

**Problem.** Players alternately claim unused indices. Player 1 scores `A_i` and player 2 scores `B_i` for the index they claim. Who wins, or is it a tie?

**Idea.** Taking index `i` gains your own value and also denies the opponent theirs, so its total worth is `A_i + B_i` for whoever takes it. Both players should therefore take the indices in decreasing order of `A_i + B_i`.

**Steps.**
1. Sort the indices by `A_i + B_i` descending; alternate the picks; compare the totals.

```python
import os


def funGame(a, b):
    order = sorted(range(len(a)), key=lambda i: -(a[i] + b[i]))
    p1 = sum(a[i] for i in order[0::2])
    p2 = sum(b[i] for i in order[1::2])
    return 'First' if p1 > p2 else 'Second' if p2 > p1 else 'Tie'


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        input()
        a = list(map(int, input().rstrip().split()))
        b = list(map(int, input().rstrip().split()))
        fptr.write(funGame(a, b) + '\n')
    fptr.close()
```

**Watch out.** Greedily taking your own largest value is wrong. With `A = [1, 3, 4]` and `B = [5, 3, 1]`, taking index 0 (sum 6) first is what wins the sample.

```stdin
3
3
1 3 4
5 3 1
2
1 1
1 1
2
2 2
3 3
```

```stdout
First
Tie
Second
```

### Stone Division

**Problem.** A move splits a pile into exactly `s` equal piles for some `s ∈ S` (the pile size must be divisible by `s`). `n` can be 10¹⁸ and `|S| ≤ 10`. Who wins?

**Idea.** Splitting into `s` equal piles of size `x/s`:
- if `s` is even, the copies cancel and the result is worth 0;
- if `s` is odd, it is worth `g(x/s)`.

So `g(x) = mex({0 for even s | x} ∪ {g(x/s) for odd s | x})`. Only sizes of the form `n / (product of elements of S)` are ever reached, so a memoised recursion visits few states.

**Steps.**
1. Memoised `g(x)` as above.
2. Print `First` if `g(n) ≠ 0`.

```python
import os
from functools import lru_cache


def stoneDivision(n, s):
    @lru_cache(maxsize=None)
    def g(x):
        seen = set()
        for k in s:
            if x % k == 0:
                seen.add(g(x // k) if k % 2 else 0)
        v = 0
        while v in seen:
            v += 1
        return v
    return 'First' if g(n) else 'Second'


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m = map(int, input().split())
    s = list(map(int, input().rstrip().split()))
    fptr.write(stoneDivision(n, s) + '\n')
    fptr.close()
```

**Watch out.** Splitting into `s` piles is impossible if `s > x`; the divisibility test already covers that, since `x % s ≠ 0` whenever `0 < x < s`.

```stdin
15 3
5 2 3
```

```stdout
Second
```

### Chocolate in Box

**Problem.** Nim: count the first moves after which the first player still wins.

**Idea.** A move is winning exactly when it leaves XOR 0, which means pile `i` becomes `a_i ⊕ X`. That is a legal move only if `a_i ⊕ X < a_i`, which happens exactly when `a_i` has the highest set bit of `X`. Count those piles; if `X = 0`, the answer is 0.

**Steps.**
1. `X` = XOR of all piles; count the `a_i` with `a_i ⊕ X < a_i`.

```python
import sys


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    a = list(map(int, data[1:1 + n]))
    x = 0
    for v in a:
        x ^= v
    print(sum(1 for v in a if v ^ x < v) if x else 0)


main()
```

**Watch out.** For each pile there is exactly one winning target size, so the count of winning moves equals the count of such piles. With up to 10⁶ piles, read the input in bulk.

```stdin
2
2 3
```

```stdout
1
```
