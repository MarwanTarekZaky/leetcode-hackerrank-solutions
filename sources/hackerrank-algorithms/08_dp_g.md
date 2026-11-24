## Dynamic Programming

### Square Subsequences

**Problem.** Count the subsequences (by positions) of `S` that are square strings `XX`, modulo 10⁹+7.

**Idea.** A square subsequence is a pair of equal subsequences, one wholly before the other. Fix where the first half ends: the split `k`, with the first half ending exactly at `s[k−1]`. Count the pairs of equal subsequences of `a = s[:k]` and `b = s[k:]` (as index sequences) that *end* with `a`'s last character.
- **The table.** `f[i][j]` counts the equal-subsequence pairs of `a[:i]` and `b[:j]`, including the empty pair. It equals 1 plus the sum of `f[i'−1][j'−1]` over the matching cells `(i', j')`, so each row is the previous row plus a prefix sum. That makes each row one NumPy step.
- **Each split's count.** `Σ_j [b_j = a_{k−1}]·f[k−1][j]`.

**Steps.**
1. For each split `k`, build `f` row by row over `a[:k−1]`.
2. Add the matches of the last character of `a` against every position of `b`.

```python
import os

import numpy as np

MOD = 10 ** 9 + 7


def squareSubsequences(s):
    codes = np.frombuffer(s.encode(), dtype=np.uint8)
    n = len(s)
    total = 0
    for k in range(1, n):
        a, b = codes[:k], codes[k:]
        m = len(b)
        f = np.ones(m + 1, dtype=np.int64)            # row i = 0: only the empty pair
        for i in range(k - 1):
            match = np.zeros(m + 1, dtype=np.int64)
            match[1:] = np.where(b == a[i], f[:m], 0)
            f = (f + np.cumsum(match)) % MOD
        total += int(f[:m][b == a[k - 1]].sum())
    return total % MOD


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        fptr.write(str(squareSubsequences(input().strip())) + '\n')
    fptr.close()
```

**Watch out.** Requiring the first half to end at `s[k−1]` gives each square subsequence exactly one split, so nothing is double counted. Subsequences are counted by positions: `aaa` has 3 squares (`aa` three ways).

```stdin
3
aaa
abab
baaba
```

```stdout
3
3
6
```

### Dorsey Thief

**Problem.** Passengers each buy exactly `a_i` grams for `v_i`. Sell exactly `X` grams in total, maximising the money, or print `Got caught!`.

**Idea.** This is an *exact* 0/1 knapsack. `N` can be 10⁶, but only a few items of each weight are useful. With weight `w`, at most `⌊X / w⌋` items fit, so keep only the most valuable ones of that weight. That leaves about `X·ln X ≈ 4·10⁴` items. Each item is one NumPy update `dp[w:] = max(dp[w:], dp[:−w] + v)`, which reads the old row and is therefore a correct 0/1 update.

**Steps.**
1. Group the values by weight `≤ X` and keep the top `X // w` of each.
2. Run the knapsack with `−∞` for unreachable weights; `dp[X]` is the answer.

```python
import sys
from collections import defaultdict

import numpy as np


def main():
    data = sys.stdin.buffer.read().split()
    n, x = int(data[0]), int(data[1])
    by_w = defaultdict(list)
    for i in range(n):
        v, a = int(data[2 + 2 * i]), int(data[3 + 2 * i])
        if a <= x:
            by_w[a].append(v)
    neg = -(1 << 60)
    dp = np.full(x + 1, neg, dtype=np.int64)
    dp[0] = 0
    for w, vals in by_w.items():
        for v in sorted(vals, reverse=True)[:x // w]:
            dp[w:] = np.maximum(dp[w:], dp[:-w] + v)
    print(dp[x] if dp[x] >= 0 else 'Got caught!')


main()
```

**Watch out.** "Exactly `X` grams" means unreachable sums must stay at `−∞`; a plain "at most" knapsack starts everything at 0 and is wrong here. Two same-weight items with equal value are interchangeable, so keeping the best ones loses nothing.

```stdin
4 10
460 4
590 6
550 5
590 5
```

```stdout
1140
```

### Mining

**Problem.** Mines lie on a line, each with an amount of gold. Consolidate all the gold into exactly `k` of the mines, moving gold costing `distance × weight`. Minimise the cost.

**Idea.**
- **One group.** Each pickup serves a contiguous group of mines, and the best pickup is the group's *weighted median*. With prefix sums of `w` and `x·w`, a group's cost is O(log n): binary search for the median, then a few subtractions.
- **Exactly `k` groups.** The cost is convex in the number of groups, so use the "Aliens" trick (WQS binary search). Charge `λ` per group, solve the unconstrained problem, and search for the `λ` that produces `k` groups.
- **The unconstrained DP.** It satisfies the quadrangle inequality, so a monotone deque with binary-searched takeover points solves it in O(n log n).

**Steps.**
1. `cost(i, j)` for mines `i..j−1` via the median.
2. `solve(λ)` returns `(value, groups)`, preferring fewer groups on ties.
3. Binary search the smallest `λ` with `groups ≤ k`; the answer is `value − λ·k`.

```python
import os
from bisect import bisect_left


def mining(k, mines):
    n = len(mines)
    xs = [x for x, _ in mines]
    W = [0] * (n + 1)
    XW = [0] * (n + 1)
    for i, (x, w) in enumerate(mines):
        W[i + 1] = W[i] + w
        XW[i + 1] = XW[i] + x * w

    def cost(i, j):                       # mines i..j-1
        half = (W[i] + W[j] + 1) // 2
        m = bisect_left(W, half, i + 1, j + 1) - 1
        xm = xs[m]
        left = xm * (W[m + 1] - W[i]) - (XW[m + 1] - XW[i])
        right = (XW[j] - XW[m + 1]) - xm * (W[j] - W[m + 1])
        return left + right

    def solve(lam):
        val = [0] * (n + 1)
        cnt = [0] * (n + 1)

        def f(i, j):
            return (val[i] + cost(i, j) + lam, cnt[i] + 1)

        dq = [[0, 1]]                     # [candidate i, first j where it is best]
        head = 0
        for j in range(1, n + 1):
            while head + 1 < len(dq) and dq[head + 1][1] <= j:
                head += 1
            i = dq[head][0]
            val[j], cnt[j] = f(i, j)
            # add candidate j for future positions
            while len(dq) > head and dq[-1][1] > j and f(j, dq[-1][1]) <= f(dq[-1][0], dq[-1][1]):
                dq.pop()
            if len(dq) == head:
                dq.append([j, j + 1])
                continue
            lo, hi = max(dq[-1][1], j + 1), n + 1
            while lo < hi:
                mid = (lo + hi) // 2
                if f(j, mid) <= f(dq[-1][0], mid):
                    hi = mid
                else:
                    lo = mid + 1
            if lo <= n:
                dq.append([j, lo])
        return val[n], cnt[n]

    lo, hi = 0, cost(0, n) + 1
    while lo < hi:
        mid = (lo + hi) // 2
        if solve(mid)[1] <= k:
            hi = mid
        else:
            lo = mid + 1
    value, _ = solve(lo)
    return value - lo * k


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    mines = [list(map(int, input().split())) for _ in range(n)]
    fptr.write(str(mining(k, mines)) + '\n')
    fptr.close()
```

**Watch out.**
- **Tie-breaking.** Use fewest groups on ties, then search for the smallest penalty reaching `≤ k` groups. That is what makes the final `value − λ·k` exact even when several `k` share a slope.
- **Why not the plain DP.** A layered O(k·n²) DP is far too slow for `n = 5000`.

```stdin
6 2
10 15
12 17
16 18
18 13
30 10
32 1
```

```stdout
182
```

### Police Operation

**Problem.** Criminals sit at sorted positions on a line. Each officer costs `h` plus the squared length of the segment he drives. Cover everyone at minimum cost.

**Idea.** The officers cover contiguous groups. `dp[i] = min_j dp[j] + h + (x_i − x_{j+1})²`. Expanding the square gives a line in `x_i`: slope `−2·x_{j+1}`, intercept `dp[j] + x_{j+1}²`, plus `x_i² + h`. Slopes decrease and queries `x_i` increase, so a monotone convex-hull-trick deque answers every query in amortised O(1).

**Steps.**
1. For each `i`, add the line for the group starting at `i`, then query the deque at `x_i` (popping lines that are no longer the minimum).
2. `dp[i] = query + x_i² + h`. The answer is `dp[n]` (0 when there are no criminals).

```python
import sys


def main():
    data = sys.stdin.buffer.read().split()
    n, h = int(data[0]), int(data[1])
    xs = list(map(int, data[2:2 + n]))
    if n == 0:
        print(0)
        return
    lines = []                            # (slope, intercept), slopes decreasing
    head = 0
    prev = 0                              # dp of the prefix before the current group start

    def bad(l1, l2, l3):
        return (l3[1] - l1[1]) * (l1[0] - l2[0]) <= (l2[1] - l1[1]) * (l1[0] - l3[0])

    for i in range(n):
        s = xs[i]
        line = (-2 * s, prev + s * s)
        while len(lines) - head >= 2 and bad(lines[-2], lines[-1], line):
            lines.pop()
        lines.append(line)
        head = min(head, len(lines) - 1)
        x = xs[i]
        while head + 1 < len(lines) and lines[head + 1][0] * x + lines[head + 1][1] <= lines[head][0] * x + lines[head][1]:
            head += 1
        prev = lines[head][0] * x + lines[head][1] + x * x + h
    print(prev)


main()
```

**Watch out.** A group of a single criminal costs exactly `h`, which the formula gives with the starting line. Values reach about 10¹⁸ times `n`, fine in Python but 128-bit territory elsewhere. The cross-multiplied "bad line" test avoids floating-point error.

```stdin
5 10
1 4 5 6 9
```

```stdout
34
```

### Zurikela's Graph

**Problem.** Sets of nodes are created, connected set-to-set (complete bipartite), and collapsed into new sets. Report the maximum independent set of the final graph.

**Idea.** Treat each *set* as a weighted super-node. Within a set all nodes are independent, and an edge between two sets joins every pair, so an optimal answer takes whole sets. The super-graph is a forest, and its maximum-weight independent set is a two-state tree DP. Operation `C x` collapses `x`'s component into a single new set whose weight is that component's MWIS. At the end, add up the MWIS of every remaining component.

**Steps.**
1. `A x`: new set of weight `x`. `B x y`: super-edge. `C x`: DFS the component, run the take/skip DP, mark the component dead and create a new set with weight = MWIS.
2. Finally, sum the MWIS over the components of the alive sets.

```python
import sys


def mwis(root, weight, adj, alive):
    """Max-weight independent set of the tree containing root; returns (value, nodes)."""
    order, parent = [root], {root: 0}
    for v in order:
        for w in adj[v]:
            if alive[w] and w not in parent:
                parent[w] = v
                order.append(w)
    take, skip = {}, {}
    for v in reversed(order):
        t, s = weight[v], 0
        for w in adj[v]:
            if alive[w] and parent.get(w) == v:
                t += skip[w]
                s += max(take[w], skip[w])
        take[v], skip[v] = t, s
    return max(take[root], skip[root]), order


def main():
    lines = sys.stdin.read().split('\n')
    q = int(lines[0])
    weight, adj, alive = [0], [[]], [False]
    for line in lines[1:1 + q]:
        parts = line.split()
        if parts[0] == 'A':
            weight.append(int(parts[1]))
            adj.append([])
            alive.append(True)
        elif parts[0] == 'B':
            x, y = int(parts[1]), int(parts[2])
            adj[x].append(y)
            adj[y].append(x)
        else:
            value, comp = mwis(int(parts[1]), weight, adj, alive)
            for v in comp:
                alive[v] = False
            weight.append(value)
            adj.append([])
            alive.append(True)
    total, seen = 0, set()
    for v in range(1, len(weight)):
        if alive[v] and v not in seen:
            value, comp = mwis(v, weight, adj, alive)
            seen.update(comp)
            total += value
    print(total)


main()
```

**Watch out.** The new set from `C` has no edges; its nodes keep their independence structure through the MWIS weight. Edges to dead sets must be ignored afterwards, hence the `alive` checks.

```stdin
8
A 1
A 2
B 1 2
C 1
A 2
A 3
B 3 4
B 4 5
```

```stdout
5
```

### Modify The Sequence

**Problem.** Replace as few elements as possible (with any positive integers) so that the sequence becomes strictly increasing.

**Idea.** Keep a set of elements and fill the gaps with replacements. A kept `a_i` at (1-based) position `i` needs `a_i ≥ i`, room for positive values before it, and any two kept values need enough room between them: `a_j − a_i ≥ j − i`. With `b_i = a_i − i`, that is just `b` non-decreasing with every `b_i ≥ 0`. So keep the longest non-decreasing subsequence of `b` among the non-negative `b_i`.

**Steps.**
1. Compute `b_i = a_i − i`, skip negatives, and run patience sorting with `bisect_right` (non-strict).
2. Answer `n − length`.

```python
import os
from bisect import bisect_right


def modifySequence(arr):
    tails = []
    for i, a in enumerate(arr, 1):
        b = a - i
        if b < 0:
            continue
        p = bisect_right(tails, b)
        if p == len(tails):
            tails.append(b)
        else:
            tails[p] = b
    return len(arr) - len(tails)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    arr = list(map(int, input().split()))
    fptr.write(str(modifySequence(arr)) + '\n')
    fptr.close()
```

**Watch out.** A plain LIS of `a` ignores the room needed for replacements: `1 2 2 3 4` has an increasing subsequence of length 4, but the answer is 3 replacements. Values must stay positive, which is the `b ≥ 0` filter.

```stdin
5
1 2 2 3 4
```

```stdout
3
```

### Longest Mod Path

**Problem.** `N` rooms and `N` corridors form a connected graph with exactly one cycle. Walking a corridor forward adds `x`, backward subtracts it. For each query `(S, E, M)`, maximise `score mod M` on reaching `E`.

**Idea.**
- **Which scores are reachable.** Going back and forth along a corridor cancels out. So every walk from `S` to `E` scores `d + t·C`, where `d = pot[E] − pot[S]` comes from potentials on a spanning tree, `C` is the value of the one cycle, and `t` is any integer (the cycle can be looped either way).
- **The best residue.** Modulo `M`, these scores are exactly the residues `≡ d (mod g)` with `g = gcd(C, M)`. The largest one below `M` is `M − g + (d mod g)`.

**Steps.**
1. BFS potentials over a spanning tree; the one extra edge gives `C = pot[a] + x − pot[b]`.
2. Per query: `d = pot[E] − pot[S]`, `g = gcd(|C|, M)`, answer `M − g + d mod g`.

```python
import sys
from collections import deque
from math import gcd


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    adj = [[] for _ in range(n + 1)]
    edges = []
    pos = 1
    for _ in range(n):
        a, b, x = int(data[pos]), int(data[pos + 1]), int(data[pos + 2])
        pos += 3
        edges.append((a, b, x))
        adj[a].append((b, x))
        adj[b].append((a, -x))
    pot = [None] * (n + 1)
    pot[1] = 0
    queue = deque([1])
    while queue:
        u = queue.popleft()
        for v, w in adj[u]:
            if pot[v] is None:
                pot[v] = pot[u] + w
                queue.append(v)
    cycle = 0
    for a, b, x in edges:
        cycle = gcd(cycle, abs(pot[a] + x - pot[b]))
    q = int(data[pos]); pos += 1
    out = []
    for _ in range(q):
        s, e, m = int(data[pos]), int(data[pos + 1]), int(data[pos + 2])
        pos += 3
        g = gcd(cycle, m)
        out.append(m - g + (pot[e] - pot[s]) % g)
    print('\n'.join(map(str, out)))


main()
```

**Watch out.** Taking `gcd` over all edges is harmless: tree edges give 0 and only the cycle edge contributes. If the cycle value is 0, `g = M` and the answer is simply `d mod M`. Python's `%` is already non-negative.

```stdin
3
1 3 5
2 3 8
2 1 31
1
1 2 13
```

```stdout
12
```

### P-sequences

**Problem.** Count the sequences of `N` positive integers where every adjacent product is at most `P` (`P ≤ 10⁹`), modulo 10⁹+7.

**Idea.** What matters about a value `a` is `⌊P/a⌋`, and that takes only about `2√P` distinct values. Split `1..P` into blocks where `⌊P/a⌋` is constant. A block's partner limit `⌊P/a⌋` is exactly the right end of the mirror-image block. So the values allowed after block `s` form the first `m + 1 − s` blocks, a prefix. One step of the DP is `new[s] = len_s · prefix(old)[m + 1 − s]`, a reversed cumulative sum, vectorised with NumPy.

**Steps.**
1. Build the blocks (their lengths) by iterating over the distinct values of `⌊P/a⌋`.
2. Start with `dp = len`, then apply the step `N − 1` times and sum.

```python
import os

import numpy as np

MOD = 10 ** 9 + 7


def pSequences(n, p):
    lens = []
    a = 1
    while a <= p:
        q = p // a
        b = p // q
        lens.append(b - a + 1)
        a = b + 1
    lens = np.array(lens, dtype=np.int64) % MOD
    dp = lens.copy()
    for _ in range(n - 1):
        pre = np.cumsum(dp) % MOD
        dp = lens * pre[::-1] % MOD          # block s pairs with blocks 1..m+1-s
    return int(dp.sum() % MOD)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    p = int(input().strip())
    fptr.write(str(pSequences(n, p)) + '\n')
    fptr.close()
```

**Watch out.** The mirror property (block `s` pairs with the first `m + 1 − s` blocks) is what keeps a step O(√P). Iterating over the values themselves would be 10⁹ per step.

```stdin
2
2
```

```stdout
3
```

### Robot

**Problem.** At each step the robot either collects `V[i]` (spending one energy) or recharges to `P[i]` (collecting nothing). It must never run out, and the last step always collects. Maximise the total.

**Idea.** Collecting everything except the recharge steps means **minimising the `V` lost at recharge points**.
- **Which recharges are legal.** Step 1 must be a recharge, since energy starts at 0. A recharge at `r` keeps the robot going until step `r + P[r]`, so the next recharge must come by then (or `r + P[r] ≥ N` finishes the run).
- **The DP.** `cost[r] = V[r] + min{cost[q] : q < r, q + P[q] ≥ r}`. A min-heap of `(cost, reach)` with lazy deletion of expired reaches answers each step.

**Steps.**
1. Push `cost[1] = V[1]` (if `P[1] > 0`). For each later `r < N` with `P[r] > 0`: drop expired heap tops, then `cost[r] = V[r] + top`.
2. The answer is `ΣV − min{cost[r] : r + P[r] ≥ N}`.

```python
import os
from heapq import heappop, heappush


def robot(vp):
    n = len(vp)
    total = sum(v for v, _ in vp)
    if n == 1:
        return total
    best_end = None
    heap = []
    for r in range(1, n):                 # recharge candidates are steps 1..N-1
        v, p = vp[r - 1]
        if p <= 0:
            continue
        if r == 1:
            c = v
        else:
            while heap and heap[0][1] < r:
                heappop(heap)
            if not heap:
                continue
            c = v + heap[0][0]
        heappush(heap, (c, r + p))
        if r + p >= n and (best_end is None or c < best_end):
            best_end = c
    return total - best_end


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    vp = [list(map(int, input().split())) for _ in range(n)]
    fptr.write(str(robot(vp)) + '\n')
    fptr.close()
```

**Watch out.** A recharge with `P = 0` would kill the robot at once, so those steps can't recharge. The heap only grows invalid at its top, so popping expired tops lazily keeps the whole thing O(n log n).

```stdin
4
4 2
0 2
4 0
3 4
```

```stdout
7
```

### Lucky Numbers

**Problem.** Count the numbers in `[a, b]` (up to 10¹⁸) whose digit sum and sum of squared digits are both prime, for up to 10⁴ queries.

**Idea.** Digit DP with a table that does all the work in advance. `G[len][s][q]` is the number of `len`-digit strings that make the total lucky, given that the digits fixed so far contribute sum `s` and square-sum `q`. It satisfies `G[len][s][q] = Σ_d G[len−1][s+d][q+d²]` with `G[0] = isPrime(s) ∧ isPrime(q)`, so each length is 10 shifted NumPy additions. A query then walks the digits of the bound, adding `G` for each smaller digit.

**Steps.**
1. Build `G` for lengths 0..18 over `s ≤ 162` and `q ≤ 1458`.
2. `count(N)` = lucky numbers in `[0, N]`. Answer `count(b) − count(a − 1)`.

```python
import sys

import numpy as np

MAXS, MAXQ = 9 * 19 + 1, 81 * 19 + 1


def build():
    sieve = np.ones(MAXQ + 1, dtype=bool)
    sieve[:2] = False
    for i in range(2, int(MAXQ ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = False
    G = [np.outer(sieve[:MAXS], sieve[:MAXQ]).astype(np.int64)]
    for _ in range(19):
        prev = G[-1]
        cur = np.zeros_like(prev)
        for d in range(10):
            cur[:MAXS - d, :MAXQ - d * d] += prev[d:, d * d:]
        G.append(cur)
    return G


G = build()


def count(n):
    if n < 0:
        return 0
    digits = list(map(int, str(n)))
    total, s, q = 0, 0, 0
    for i, dig in enumerate(digits):
        rest = len(digits) - i - 1
        for d in range(dig):
            total += int(G[rest][s + d, q + d * d])
        s += dig
        q += dig * dig
    return total + int(G[0][s, q])


def main():
    data = sys.stdin.read().split()
    t = int(data[0])
    out = []
    for i in range(t):
        a, b = int(data[1 + 2 * i]), int(data[2 + 2 * i])
        out.append(count(b) - count(a - 1))
    print('\n'.join(map(str, out)))


main()
```

**Watch out.** Numbers shorter than the bound appear as strings with leading zeros, and zeros add nothing to either sum, so they are counted correctly. 0 itself is not lucky, since 0 isn't prime. The counts stay below 10¹⁸, which fits in `int64`.

```stdin
2
1 20
120 130
```

```stdout
4
1
```

### Unfair Game

**Problem.** Add stones (never remove) to the Nim piles so that the XOR becomes 0, using as few stones as possible.

**Idea.** Choose the final piles `t_i ≥ s_i` bit by bit from the top. A pile is *tight* while its prefix equals `s_i`'s prefix, and *free* once it has gone above, after which its lower bits are unrestricted.
- **At each bit.** Tight piles copy `s`'s bit, or a tight pile with a 0 there may jump to 1 and become free. Free piles use 0, except that one of them may set a 1 to fix the parity.
- **The DP.** The state is the mask of free piles; the value is the total of the `t` bits so far. Freeing more than two piles at one bit never helps, so the transitions stay small.

**Steps.**
1. For bits 32 down to 0, transition every state over freeing ∅, `{i}` or `{i, j}` among the tight piles with a 0 bit. An odd parity needs an existing free pile.
2. The answer is the minimum total minus `Σ s_i`.

```python
import os
from itertools import combinations


def unfairGame(s):
    n = len(s)
    full = (1 << n) - 1
    states = {0: 0}
    for b in range(32, -1, -1):
        sb = sum(1 << i for i in range(n) if s[i] >> b & 1)
        new = {}
        for free, cost in states.items():
            tight = full & ~free
            forced = bin(tight & sb).count('1')
            zeros = [i for i in range(n) if tight >> i & 1 and not sb >> i & 1]
            for group in [()] + [(i,) for i in zeros] + list(combinations(zeros, 2)):
                ones = forced + len(group)
                nf = free
                for i in group:
                    nf |= 1 << i
                if ones % 2:
                    if not free:
                        continue
                    ones += 1
                c = cost + (ones << b)
                if c < new.get(nf, float('inf')):
                    new[nf] = c
        states = new
    return min(states.values()) - sum(s)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        input()
        s = list(map(int, input().split()))
        fptr.write(str(unfairGame(s)) + '\n')
    fptr.close()
```

**Watch out.**
- **Parity fixes.** A free pile's later bits are free, so a single free pile can fix every lower parity at the cost of the bits it sets. A pile that was just freed has a 1 at this bit, so it can't also flip the parity here.
- **How this was checked.** Against exhaustive search over small inputs.

```stdin
3
2
1 3
3
1 1 1
4
10 4 5 1
```

```stdout
2
3
6
```

### Oil Well

**Problem.** Build wells on all marked cells. The first is free; each later well costs its maximum Chebyshev distance to the wells already built. Minimise the total.

**Idea.** An optimal order grows a rectangle: the next well always lies on the border of the current bounding box. So use an interval DP over rectangles, shrinking the grid first to the bounding box of the marked cells.
- **The transition.** A rectangle is built from a smaller one by adding its top row, bottom row, left column or right column. A cell in the added row costs `max(height−1, distance to the left edge, distance to the right edge)`, which is its distance to the farthest point of the rectangle.
- **Speed.** For each rectangle size, all positions are handled at once with NumPy, and each strip's costs are a weighted sliding sum.

**Steps.**
1. `dp[(H, W)]` is an array over the top-left corners. Fill sizes in increasing order from the four smaller neighbours.
2. The answer is `dp` of the full bounding box.

```python
import os

import numpy as np


def oilWell(blocks):
    cells = [(i, j) for i, row in enumerate(blocks) for j, v in enumerate(row) if v]
    if not cells:
        return 0
    r0, r1 = min(i for i, _ in cells), max(i for i, _ in cells)
    c0, c1 = min(j for _, j in cells), max(j for _, j in cells)
    g = np.array([row[c0:c1 + 1] for row in blocks[r0:r1 + 1]], dtype=np.int64)
    R, C = g.shape
    dp = {(1, 1): np.zeros((R, C), dtype=np.int64)}
    big = 1 << 60
    for H in range(1, R + 1):
        for W in range(1, C + 1):
            if H == 1 and W == 1:
                continue
            nr, nc = R - H + 1, C - W + 1
            best = np.full((nr, nc), big, dtype=np.int64)
            if H > 1:
                prev = dp[(H - 1, W)]
                k = [max(H - 1, t, W - 1 - t) for t in range(W)]
                top = sum(g[0:nr, t:t + nc] * k[t] for t in range(W))
                bottom = sum(g[H - 1:H - 1 + nr, t:t + nc] * k[t] for t in range(W))
                best = np.minimum(best, prev[1:1 + nr, :] + top)
                best = np.minimum(best, prev[0:nr, :] + bottom)
            if W > 1:
                prev = dp[(H, W - 1)]
                k = [max(W - 1, t, H - 1 - t) for t in range(H)]
                left = sum(g[t:t + nr, 0:nc] * k[t] for t in range(H))
                right = sum(g[t:t + nr, W - 1:W - 1 + nc] * k[t] for t in range(H))
                best = np.minimum(best, prev[:, 1:1 + nc] + left)
                best = np.minimum(best, prev[:, 0:nc] + right)
            dp[(H, W)] = best
    return int(dp[(R, C)][0, 0])


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    r, c = map(int, input().split())
    blocks = [list(map(int, input().split())) for _ in range(r)]
    fptr.write(str(oilWell(blocks)) + '\n')
    fptr.close()
```

**Watch out.** The cost uses the rectangle's corners even when they are empty. Such rectangles are never optimal compared with the tight ones the DP also considers, so the minimum is still exact. This was checked against trying every build order on small grids.

```stdin
3 4
1 0 0 0
1 0 0 0
0 0 1 0
```

```stdout
3
```

### Find the Seed

**Problem.** A linear recurrence `F(K) = Σ C(i)·F(K−i) mod p` produced `F(K)..F(K−N+1)`. Recover the seeds `F(N−1)..F(0)`.

**Idea.** The recurrence can be run backwards: `C(N) ≠ 0 mod p`, so `F(K−N) = C(N)⁻¹·(F(K) − Σ_{i<N} C(i)·F(K−i))`. Write that step as an `N × N` matrix `B` acting on the window `[F(K), …, F(K−N+1)]`. Then raise `B` to the power `K − N + 1` by repeated squaring and apply it once.

**Steps.**
1. Build `B`: its last row holds the inverted recurrence, and the other rows shift the window.
2. Compute `B^(K−N+1)` (pure Python, mod `p`) and multiply it by the given window.

```python
import os

MOD = 10 ** 9 + 7


def mat_mul(a, b):
    n, m, k = len(a), len(b), len(b[0])
    bt = list(zip(*b))
    return [[sum(x * y for x, y in zip(a[i], bt[j])) % MOD for j in range(k)] for i in range(n)]


def findSeed(k, f, c):
    n = len(c)
    inv = pow(c[n - 1], MOD - 2, MOD)
    # window v = [F(K), F(K-1), ..., F(K-N+1)] -> [F(K-1), ..., F(K-N)]
    B = [[0] * n for _ in range(n)]
    for i in range(n - 1):
        B[i][i + 1] = 1
    B[n - 1][0] = inv
    for i in range(1, n):
        B[n - 1][i] = (-c[i - 1] * inv) % MOD
    steps = k - n + 1
    result = [[int(i == j) for j in range(n)] for i in range(n)]
    while steps:
        if steps & 1:
            result = mat_mul(result, B)
        B = mat_mul(B, B)
        steps >>= 1
    vec = mat_mul(result, [[x] for x in f])
    return [row[0] for row in vec]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    f = list(map(int, input().split()))
    c = list(map(int, input().split()))
    fptr.write(' '.join(map(str, findSeed(k, f, c))) + '\n')
    fptr.close()
```

**Watch out.** The new oldest value `F(K−N)` depends on all the current window values. That is why `B`'s last row carries the coefficients, while the other rows just shift. `K` up to 10⁹ needs the O(N³ log K) matrix power, not stepping one by one.

```stdin
2 6
13 8
1 1
```

```stdout
1 1
```

### The Blacklist

**Problem.** Each mercenary (used at most once) can kill one contiguous block of gangsters and charges per gangster. Kill all `N ≤ 20` gangsters at minimum total cost.

**Idea.** `dp[i][mask]` = the cheapest way to kill gangsters `0..i−1` using the mercenary set `mask`. From `(i, mask)`, pick an unused mercenary `m` and a block end `j > i`, paying `m`'s cost for gangsters `i..j−1`, which is a prefix-sum lookup. With `N·2^K·K·N` ≈ 4·10⁶ transitions, it is fast enough.

**Steps.**
1. Prefix sums for each mercenary.
2. Forward DP over `i`, then `mask`, then the unused `m`, then `j`; the answer is `min(dp[N])`.

```python
import os


def blacklist(amounts):
    k, n = len(amounts), len(amounts[0])
    pre = [[0] * (n + 1) for _ in range(k)]
    for m in range(k):
        for j in range(n):
            pre[m][j + 1] = pre[m][j] + amounts[m][j]
    inf = float('inf')
    dp = [[inf] * (1 << k) for _ in range(n + 1)]
    dp[0][0] = 0
    for i in range(n):
        for mask in range(1 << k):
            cur = dp[i][mask]
            if cur == inf:
                continue
            for m in range(k):
                if mask >> m & 1:
                    continue
                nm = mask | 1 << m
                row = pre[m]
                for j in range(i + 1, n + 1):
                    c = cur + row[j] - row[i]
                    if c < dp[j][nm]:
                        dp[j][nm] = c
    return min(dp[n])


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    amounts = [list(map(int, input().split())) for _ in range(k)]
    fptr.write(str(blacklist(amounts)) + '\n')
    fptr.close()
```

**Watch out.** Each mercenary takes one contiguous block at most, so reusing one for a second block is not allowed; the mask enforces that. Not every mercenary has to be used.

```stdin
3 2
1 4 1
2 2 2
```

```stdout
5
```
