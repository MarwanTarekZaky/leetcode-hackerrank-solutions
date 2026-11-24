## Recursion

### The Power Sum

**Problem.** Count the ways to write `X` as a sum of `N`-th powers of **distinct** natural numbers.

**Idea.** Try the bases in increasing order: either use `base^N` (and move on to the next base with `X − base^N`), or skip the base. Stop when `base^N > X`. Going in increasing order makes every set counted once.

**Steps.**
1. `count(rest, base)`: if `rest == 0` it is one way; if `base^N > rest`, it is zero ways; otherwise `count(rest − base^N, base+1) + count(rest, base+1)`.

```python
import os
import sys

sys.setrecursionlimit(10000)


def powerSum(X, N):
    def count(rest, base):
        if rest == 0:
            return 1
        p = base ** N
        if p > rest:
            return 0
        return count(rest - p, base + 1) + count(rest, base + 1)
    return count(X, 1)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    X = int(input().strip())
    N = int(input().strip())
    fptr.write(str(powerSum(X, N)) + '\n')
    fptr.close()
```

**Watch out.** Distinct numbers only, so `10 = 1² + 1² + …` does not count. With `X ≤ 1000` and `N ≥ 2`, there are at most 31 bases, so plain recursion is enough.

```stdin
10
2
```

```stdout
1
```

### Crossword Puzzle

**Problem.** Fill the `-` slots of a 10×10 grid with the given words (separated by `;`) so that every crossing letter agrees.

**Idea.** Backtracking.
1. Collect the **slots**: maximal horizontal or vertical runs of `-` with length at least 2.
2. Place the words one at a time into a free slot of matching length whose cells are empty or already hold the same letter.
3. Undo only the cells you actually wrote, then try the next option.

**Steps.**
1. Find the slots as lists of cells.
2. `solve(word_index)`: try each unused slot of that length; recurse; undo on failure.

```python
import os


def crosswordPuzzle(crossword, words):
    grid = [list(row) for row in crossword]
    words = words.split(';')
    slots = []
    for r in range(10):                      # horizontal runs
        c = 0
        while c < 10:
            if grid[r][c] == '-':
                start = c
                while c < 10 and grid[r][c] == '-':
                    c += 1
                if c - start >= 2:
                    slots.append([(r, x) for x in range(start, c)])
            else:
                c += 1
    for c in range(10):                      # vertical runs
        r = 0
        while r < 10:
            if grid[r][c] == '-':
                start = r
                while r < 10 and grid[r][c] == '-':
                    r += 1
                if r - start >= 2:
                    slots.append([(y, c) for y in range(start, r)])
            else:
                r += 1
    used = [False] * len(slots)

    def solve(i):
        if i == len(words):
            return True
        w = words[i]
        for k, slot in enumerate(slots):
            if used[k] or len(slot) != len(w):
                continue
            if any(grid[r][c] not in ('-', ch) for (r, c), ch in zip(slot, w)):
                continue
            written = [(r, c) for (r, c) in slot if grid[r][c] == '-']
            for (r, c), ch in zip(slot, w):
                grid[r][c] = ch
            used[k] = True
            if solve(i + 1):
                return True
            used[k] = False
            for r, c in written:
                grid[r][c] = '-'
        return False

    solve(0)
    return [''.join(row) for row in grid]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    crossword = [input().strip() for _ in range(10)]
    words = input().strip()
    fptr.write('\n'.join(crosswordPuzzle(crossword, words)) + '\n')
    fptr.close()
```

**Watch out.** When undoing, reset only the cells this word wrote. Crossing letters placed by earlier words must stay. Runs of length 1 are not slots: they are crossings seen from the other direction.

```stdin
+-++++++++
+-++++++++
+-++++++++
+-----++++
+-+++-++++
+-+++-++++
+++++-++++
++------++
+++++-++++
+++++-++++
LONDON;DELHI;ICELAND;ANKARA
```

```stdout
+L++++++++
+O++++++++
+N++++++++
+DELHI++++
+O+++C++++
+N+++E++++
+++++L++++
++ANKARA++
+++++N++++
+++++D++++
```

### Recursive Digit Sum

**Problem.** The number `p` is `n` written `k` times in a row. Repeatedly sum its digits until one digit remains (the "super digit").

**Idea.** The super digit is the **digital root**, which only depends on the value modulo 9: `1 + (x − 1) mod 9` for `x > 0`. The digit sum of `p` is `k · digitsum(n)`, so we never build `p`.

**Steps.**
1. `s = k · sum(digits of n)`; print `1 + (s − 1) % 9`.

```python
import os


def superDigit(n, k):
    s = sum(map(int, n)) * k
    return 1 + (s - 1) % 9


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = input().split()
    fptr.write(str(superDigit(n, int(k))) + '\n')
    fptr.close()
```

**Watch out.** `n` can have 10⁵ digits and `k` up to 10⁵, so the concatenated number is far too large to build. Digits are 1–9 at least somewhere (`n ≥ 1`), so `s > 0`.

```stdin
148 3
```

```stdout
3
```

### Simplified Chess Engine

**Problem.** On a 4×4 board with Queens, Rooks, Bishops and Knights (no Kings), White moves first. Can White capture Black's Queen within `m ≤ 6` moves (both sides' moves count), no matter what Black does, without losing its own Queen first?

**Idea.** A depth-limited game search (AND–OR), memoised on (board, moves left).
- **White to move with `p` plies left.**
  - Win at once if some move captures the black Queen.
  - Otherwise, with `p ≥ 3`, look for a move such that **every** black reply both avoids capturing the white Queen and leaves a winning position with `p − 2` plies.
- **Pruning.** "Some" stops at the first success and "every" stops at the first refutation, so most of the tree is never visited.

**Steps.**
1. Build the board as 16 cells; generate moves (sliders stop at the first occupied cell, captures only of enemy pieces).
2. Run `win(board, m)` for each game and print `YES`/`NO`.

```python
import sys

KN = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]
DIAG = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
ORTH = [(1, 0), (-1, 0), (0, 1), (0, -1)]
DIRS = {'B': DIAG, 'R': ORTH, 'Q': DIAG + ORTH}


def moves(board, color):
    out = []
    for s, piece in enumerate(board):
        if piece is None or piece[0] != color:
            continue
        r, c = divmod(s, 4)
        t = piece[1]
        if t == 'N':
            for dr, dc in KN:
                rr, cc = r + dr, c + dc
                if 0 <= rr < 4 and 0 <= cc < 4:
                    d = board[rr * 4 + cc]
                    if d is None or d[0] != color:
                        out.append((s, rr * 4 + cc))
        else:
            for dr, dc in DIRS[t]:
                rr, cc = r + dr, c + dc
                while 0 <= rr < 4 and 0 <= cc < 4:
                    d = board[rr * 4 + cc]
                    if d is None:
                        out.append((s, rr * 4 + cc))
                    else:
                        if d[0] != color:
                            out.append((s, rr * 4 + cc))
                        break
                    rr += dr
                    cc += dc
    return out


def play(board, mv):
    b = list(board)
    b[mv[1]] = b[mv[0]]
    b[mv[0]] = None
    return tuple(b)


def solve(board, m):
    memo = {}

    def captures_queen(b, color):
        enemy = 'B' if color == 'W' else 'W'
        return any(b[t] == (enemy, 'Q') for _, t in moves(b, color))

    def win(b, p):
        key = (b, p)
        if key in memo:
            return memo[key]
        res = False
        wm = moves(b, 'W')
        if any(b[t] == ('B', 'Q') for _, t in wm):
            res = True
        elif p >= 3:
            for mv in wm:
                b1 = play(b, mv)
                ok = True
                for bm in moves(b1, 'B'):
                    if b1[bm[1]] == ('W', 'Q'):
                        ok = False
                        break
                    if not win(play(b1, bm), p - 2):
                        ok = False
                        break
                if ok:
                    res = True
                    break
        memo[key] = res
        return res

    return win(board, m)


def main():
    data = sys.stdin.read().split()
    g = int(data[0])
    pos = 1
    out = []
    for _ in range(g):
        w, b, m = int(data[pos]), int(data[pos + 1]), int(data[pos + 2])
        pos += 3
        board = [None] * 16
        for i in range(w + b):
            t, c, r = data[pos], data[pos + 1], data[pos + 2]
            pos += 3
            board[(int(r) - 1) * 4 + (ord(c) - 65)] = ('W' if i < w else 'B', t)
        out.append('YES' if solve(tuple(board), m) else 'NO')
    print('\n'.join(out))


main()
```

**Watch out.** `m` counts both players' moves, so White moves at plies 1, 3 and 5. A white move that lets Black capture the white Queen is a refutation, even if White could capture back next turn. The template drops the column letters into lists; this program parses the tokens itself.

```stdin
1
2 1 1
N B 2
Q B 1
Q A 4
```

```stdout
YES
```

### Password Cracker

**Problem.** Split the login attempt into a concatenation of the given passwords (reuse allowed), or print `WRONG PASSWORD`.

**Idea.** Depth-first search over the start position, trying the passwords in the given order. Remember the positions that already failed, so each position is explored at most once: O(len · passwords) work in total.

**Steps.**
1. `dfs(i)`: at the end, succeed. Otherwise, for each password that matches at `i`, try `dfs(i + len)`. Record failures.
2. Join the found pieces with spaces.

```python
import os
import sys

sys.setrecursionlimit(10000)


def passwordCracker(passwords, loginAttempt):
    n = len(loginAttempt)
    dead = set()
    path = []

    def dfs(i):
        if i == n:
            return True
        if i in dead:
            return False
        for p in passwords:
            if loginAttempt.startswith(p, i):
                path.append(p)
                if dfs(i + len(p)):
                    return True
                path.pop()
        dead.add(i)
        return False

    return ' '.join(path) if dfs(0) else 'WRONG PASSWORD'


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        input()
        passwords = input().rstrip().split()
        loginAttempt = input().strip()
        fptr.write(passwordCracker(passwords, loginAttempt) + '\n')
    fptr.close()
```

**Watch out.** Without the failure memo, inputs like `a aa aaa …` followed by an impossible tail take exponential time. The attempt is up to 2000 characters long, so the recursion limit is raised.

```stdin
3
6
because can do must we what
wedowhatwemustbecausewecan
2
hello planet
helloworld
3
ab abcd cd
abcd
```

```stdout
we do what we must because we can
WRONG PASSWORD
ab cd
```

### Arithmetic Expressions

**Problem.** Put `+`, `-` or `*` between the numbers (evaluated strictly left to right) so that the result is divisible by 101. Any valid expression is accepted.

**Idea.** Left-to-right evaluation means only the running value modulo 101 matters. Keep the set of reachable residues after each number, and for each one remember the parent residue and the operator. When residue 0 is reachable at the end, walk the parents back.

**Steps.**
1. `reach[0] = {a₀ mod 101}`. For each next number, apply the three operators to every reachable residue.
2. Backtrack from residue 0 to rebuild the operators.

```python
import sys


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    a = list(map(int, data[1:1 + n]))
    parent = [dict() for _ in range(n)]          # parent[i][residue] = (prev residue, op)
    parent[0][a[0] % 101] = None
    for i in range(1, n):
        x = a[i]
        cur = parent[i]
        for v in parent[i - 1]:
            for op, nv in (('+', (v + x) % 101), ('-', (v - x) % 101), ('*', v * x % 101)):
                if nv not in cur:
                    cur[nv] = (v, op)
    ops = []
    v = 0
    for i in range(n - 1, 0, -1):
        pv, op = parent[i][v]
        ops.append(op)
        v = pv
    ops.reverse()
    print(str(a[0]) + ''.join(op + str(x) for op, x in zip(ops, a[1:])))


main()
```

**Watch out.** There are at most 101 residues per step, so the work is about `3·101·n`. Once the value is 0, `*` keeps it 0, which is why a solution always exists in practice. The hidden test evaluates the printed expression left to right.

```stdin
3
22 79 21
```

```check
n = int(stdin.split()[0])
a = list(map(int, stdin.split()[1:1 + n]))
expr = output.strip().replace(' ', '')
import re
tokens = re.findall(r'\d+|[+\-*]', expr)
nums = [int(t) for t in tokens[0::2]]
ops = tokens[1::2]
assert nums == a, (nums, a)
v = nums[0]
for op, x in zip(ops, nums[1:]):
    v = v + x if op == '+' else v - x if op == '-' else v * x
assert v % 101 == 0, v
assert len(expr) <= 10 * n
```

### Stone Division, Revisited

**Problem.** A move splits a pile of `y` stones into `y/x` equal piles, for some `x` in `S` with `x | y` and `x ≠ y`. Starting from `n`, find the maximum number of moves.

**Idea.** Piles only ever have sizes `n` or `x ∈ S`, and only the `x` dividing `n` matter. For a pile `y`:

`best(y) = max over x ∈ S, x | y, x < y of 1 + (y/x)·best(x)`

The `y/x` new piles are each worked on independently. Memoise over the at most `|S| + 1` sizes.

**Steps.**
1. Keep only the `x ∈ S` that divide `n`.
2. Memoised recursion as above; print `best(n)`.

```python
import os
from functools import lru_cache


def stoneDivision(n, s):
    cand = sorted(x for x in s if n % x == 0)

    @lru_cache(maxsize=None)
    def best(y):
        res = 0
        for x in cand:
            if x >= y:
                break
            if y % x == 0:
                res = max(res, 1 + (y // x) * best(x))
        return res

    return best(n)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        n, m = map(int, input().split())
        s = list(map(int, input().rstrip().split()))
        fptr.write(str(stoneDivision(n, s)) + '\n')
    fptr.close()
```

**Watch out.** Splitting into piles of size 1 is allowed only if `1 ∈ S`; after that no move applies to a pile of size 1 (`x ≠ y`). The answer can be large, but Python integers handle it.

```stdin
1
12 3
2 3 4
```

```stdout
4
```

### K Factorization

**Problem.** Reach `N` from 1 by repeatedly multiplying by numbers from `A`. Use the fewest states, and among those print the lexicographically smallest list of states, or `-1`.

**Idea.** Every state is a divisor of `N`.
- **Distances.** Compute `dist(v)`, the fewest multiplications from `v` to `N`, by memoised recursion over the divisors: `dist(N) = 0`, and `dist(v) = 1 + min dist(v·a)` over `a ∈ A` with `v·a | N`.
- **Path.** All shortest paths have the same length, so the lexicographically smallest one is built greedily: from 1, always step to the **smallest** next state that keeps the distance optimal.

**Steps.**
1. `dist` with `lru_cache`; if `dist(1)` is infinite, print `-1`.
2. Walk greedily from 1 and print the states.

```python
import os
from functools import lru_cache

INF = float('inf')


def kFactorization(n, A):
    @lru_cache(maxsize=None)
    def dist(v):
        if v == n:
            return 0
        best = INF
        for a in A:
            if n % (v * a) == 0:
                best = min(best, 1 + dist(v * a))
        return best

    if dist(1) == INF:
        return [-1]
    path = [1]
    v = 1
    while v != n:
        v = min(v * a for a in A if n % (v * a) == 0 and dist(v * a) == dist(v) - 1)
        path.append(v)
    return path


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    A = list(map(int, input().rstrip().split()))
    fptr.write(' '.join(map(str, kFactorization(n, A))) + '\n')
    fptr.close()
```

**Watch out.** Compare the lists of **states**, not of multipliers. In the example, `1 3 12` beats `1 4 12` even though it multiplies by `3` and then `4`. `N = 1` needs no steps, so the answer is just `1`.

```stdin
12 3
2 3 4
```

```stdout
1 3 12
```

### Bowling Pins

**Problem.** Players alternately knock down one pin or two adjacent pins, and whoever takes the last pin wins. Given the configuration, do you (moving first) win?

**Idea.** This is the game **Kayles**. The standing runs are independent games, so by Sprague–Grundy the position is winning exactly when the XOR of the runs' Grundy numbers is non-zero. For a run of length `L`, a move removes 1 or 2 pins and splits the rest into two runs `a` and `b` with `a + b = L − 1` or `L − 2`. So `G(L) = mex { G(a) ⊕ G(b) }`. Precompute it up to 300.

**Steps.**
1. Grundy table for `L ≤ 300`.
2. Split the string on `X`, XOR the Grundy values, and print `WIN` if non-zero.

```python
import os


def grundy_table(n):
    G = [0] * (n + 1)
    for L in range(1, n + 1):
        seen = set()
        for take in (1, 2):
            for a in range(L - take + 1):
                b = L - take - a
                if b >= 0:
                    seen.add(G[a] ^ G[b])
        g = 0
        while g in seen:
            g += 1
        G[L] = g
    return G


G = grundy_table(300)


def isWinning(n, config):
    x = 0
    for run in config.split('X'):
        x ^= G[len(run)]
    return 'WIN' if x else 'LOSE'


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n = int(input().strip())
        config = input().strip()
        fptr.write(isWinning(n, config) + '\n')
    fptr.close()
```

**Watch out.** Splitting on `X` gives empty strings for adjacent `X`s; `G[0] = 0`, so they are harmless. Build the table once, not per test.

```stdin
4
4
IXXI
4
XIIX
5
IIXII
5
IIIII
```

```stdout
LOSE
WIN
LOSE
WIN
```

### Simplified Chess Engine II

**Problem.** The same game as *Simplified Chess Engine*, now with Pawns: one step forward onto an empty square, diagonal captures, no double step, no en passant, and a mandatory promotion to Bishop, Knight or Rook on the last row. Up to 1000 games.

**Idea.** The same memoised AND–OR search over (board, plies left). Pawn moves are added to the move generator. A promotion branches into the three possible pieces, so White may pick any of them, and Black's three choices must all be answered.

**Steps.**
1. Extend the move generator with pawns (a white pawn moves up, a black pawn moves down) and promotions.
2. Run the same `win(board, m)` search.

```python
import sys

KN = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]
DIAG = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
ORTH = [(1, 0), (-1, 0), (0, 1), (0, -1)]
DIRS = {'B': DIAG, 'R': ORTH, 'Q': DIAG + ORTH}


def moves(board, color):
    out = []                                         # (from, to, piece placed on `to`)
    for s, piece in enumerate(board):
        if piece is None or piece[0] != color:
            continue
        r, c = divmod(s, 4)
        t = piece[1]
        if t == 'P':
            dr = 1 if color == 'W' else -1
            rr = r + dr
            last = rr == (3 if color == 'W' else 0)
            kinds = ('B', 'N', 'R') if last else ('P',)
            targets = []
            if board[rr * 4 + c] is None:
                targets.append(rr * 4 + c)
            for dc in (-1, 1):
                cc = c + dc
                if 0 <= cc < 4:
                    d = board[rr * 4 + cc]
                    if d is not None and d[0] != color:
                        targets.append(rr * 4 + cc)
            for to in targets:
                for k in kinds:
                    out.append((s, to, (color, k)))
        elif t == 'N':
            for dr, dc in KN:
                rr, cc = r + dr, c + dc
                if 0 <= rr < 4 and 0 <= cc < 4:
                    d = board[rr * 4 + cc]
                    if d is None or d[0] != color:
                        out.append((s, rr * 4 + cc, piece))
        else:
            for dr, dc in DIRS[t]:
                rr, cc = r + dr, c + dc
                while 0 <= rr < 4 and 0 <= cc < 4:
                    d = board[rr * 4 + cc]
                    if d is None:
                        out.append((s, rr * 4 + cc, piece))
                    else:
                        if d[0] != color:
                            out.append((s, rr * 4 + cc, piece))
                        break
                    rr += dr
                    cc += dc
    return out


def play(board, mv):
    b = list(board)
    b[mv[1]] = mv[2]
    b[mv[0]] = None
    return tuple(b)


def solve(board, m):
    memo = {}

    def win(b, p):
        key = (b, p)
        if key in memo:
            return memo[key]
        res = False
        wm = moves(b, 'W')
        if any(b[mv[1]] == ('B', 'Q') for mv in wm):
            res = True
        elif p >= 3:
            for mv in wm:
                b1 = play(b, mv)
                ok = True
                for bm in moves(b1, 'B'):
                    if b1[bm[1]] == ('W', 'Q') or not win(play(b1, bm), p - 2):
                        ok = False
                        break
                if ok:
                    res = True
                    break
        memo[key] = res
        return res

    return win(board, m)


def main():
    data = sys.stdin.read().split()
    g = int(data[0])
    pos = 1
    out = []
    for _ in range(g):
        w, b, m = int(data[pos]), int(data[pos + 1]), int(data[pos + 2])
        pos += 3
        board = [None] * 16
        for i in range(w + b):
            t, c, r = data[pos], data[pos + 1], data[pos + 2]
            pos += 3
            board[(int(r) - 1) * 4 + (ord(c) - 65)] = ('W' if i < w else 'B', t)
        out.append('YES' if solve(tuple(board), m) else 'NO')
    print('\n'.join(out))


main()
```

**Watch out.** A pawn's forward step needs an **empty** square and cannot capture. Promotion is forced, and promoting to a Queen is not allowed. Checking "can I take the Queen right now" before searching deeper settles most positions immediately.

```stdin
1
2 1 1
Q B 1
P B 3
Q A 4
```

```stdout
YES
```

### Repetitive K-Sums

**Problem.** Given all the sums of `K`-element multisets of an unknown non-decreasing sequence `A` (in any order), recover `A`.

**Idea.** Sort the sums.
- **First element.** The smallest sum is `K·A₁`.
- **Later elements.** Go through the sums in increasing order, keeping a counter of the sums already explained by the elements found so far. The first sum that is **not** explained must be `(K−1)·A₁ + A_new`, the cheapest multiset using the new element.
- **Explaining sums.** For each new element, add to the counter the sum of every `K`-multiset that uses it at least once (together with earlier elements). Each multiset is generated exactly once, so the total work equals the input size.

**Steps.**
1. `A₁ = min / K`, then register `K·A₁`.
2. Scan the sorted sums: skip the explained ones. Otherwise derive the new element and register its multisets with a recursion over (elements left, slots left).

```python
import sys
from collections import Counter
from math import comb


def restore(n, k, sums):
    sums.sort()
    a = [sums[0] // k]
    pending = Counter()
    pending[sums[0]] += 1
    out_sums = []

    def gen(m, r, base):                         # multisets of size r from a[0..m-1]
        if r == 0:
            out_sums.append(base)
            return
        if m == 1:
            out_sums.append(base + r * a[0])
            return
        x = a[m - 1]
        for c in range(r + 1):
            gen(m - 1, r - c, base + c * x)

    for s in sums:
        if len(a) == n:
            break
        if pending[s]:
            pending[s] -= 1
            continue
        new = s - (k - 1) * a[0]
        a.append(new)
        m = len(a)
        out_sums.clear()
        for j in range(1, k + 1):                # j copies of the new element
            gen(m - 1, k - j, j * new)
        for v in out_sums:
            pending[v] += 1
        pending[s] -= 1                          # the current sum is one of them
    return a


def main():
    data = sys.stdin.buffer.read().split()
    t = int(data[0])
    pos = 1
    out = []
    for _ in range(t):
        n, k = int(data[pos]), int(data[pos + 1])
        pos += 2
        m = comb(n + k - 1, k) if n > 1 else 1   # number of sums in this test
        sums = list(map(int, data[pos:pos + m]))
        pos += m
        out.append(' '.join(map(str, restore(n, k, sums))))
    print('\n'.join(out))


main()
```

**Watch out.** The number of sums is `C(N+K−1, K)`, which is how the input is split into test cases. `K` can be 10⁹ only when `N = 1` (then there is a single sum). The recursion only goes as deep as the number of elements, which is small whenever `K ≥ 2`.

```stdin
3
1 3
3
2 2
12 34 56
3 2
2 3 4 4 5 6
```

```stdout
1
6 28
1 2 3
```
