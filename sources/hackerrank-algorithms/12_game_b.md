## Game Theory

### Kitty and Katty

**Problem.** Blocks `1..N`. A move replaces two blocks `A`, `B` by `A − B`. When one block `X` is left: `X mod 3 = 1` means Kitty wins, `2` means Katty wins, and `0` means whoever moved last wins. Kitty moves first.

**Idea.** There are `N − 1` moves, so the last mover is Kitty when `N` is even and Katty when `N` is odd. That last mover can always steer the final residue their way: with the last two blocks, they choose between `A − B` and `B − A`, which have opposite residues. So for `N ≥ 2`:
- Kitty wins when `N` is even;
- Katty wins when `N` is odd.

`N = 1` leaves `X = 1` without any move, so Kitty wins. A brute force over residue counts confirms this.

**Steps.**
1. Print `Kitty` if `N == 1` or `N` is even, else `Katty`.

```python
import sys

data = sys.stdin.read().split()
t = int(data[0])
print('\n'.join('Kitty' if n == 1 or n % 2 == 0 else 'Katty' for n in map(int, data[1:1 + t])))
```

**Watch out.** The two orders matter only through the sign: `A − B` and `B − A` are negatives, which swaps residues 1 and 2 and keeps 0. That is exactly the freedom the last mover needs.

```stdin
2
2
3
```

```stdout
Kitty
Katty
```

### Powers Game

**Problem.** In `*2¹ *2² … *2ⁿ`, players alternately replace an asterisk by `+` or `−`. Player 2 wins if the final value is divisible by 17. Who wins?

**Idea.** Since `2⁴ = 16 ≡ −1 (mod 17)`, the powers pair up: `2^i` and `2^{i+4}` are negatives modulo 17. If `n` is a multiple of 8, the terms split into such pairs, and player 2 answers each move by giving the partner term the **same** sign. Each pair then sums to 0 modulo 17, so player 2 wins. Otherwise player 1 wins, which brute force confirms for small `n`.

**Steps.**
1. Print `Second` if `n % 8 == 0`, else `First`.

```python
import sys

data = sys.stdin.buffer.read().split()
t = int(data[0])
sys.stdout.write('\n'.join('Second' if int(x) % 8 == 0 else 'First' for x in data[1:1 + t]) + '\n')
```

**Watch out.** There can be 10⁶ test lines, so read and write in bulk.

```stdin
1
2
```

```stdout
First
```

### Deforestation

**Problem.** A move cuts an edge of a rooted tree, and the part no longer connected to the root disappears. Whoever cannot move loses.

**Idea.** This is **Green Hackenbush** on a tree. By the colon principle, a vertex's value is the XOR over its children of `(child value + 1)`. Alice wins exactly when the root's value is non-zero.

**Steps.**
1. Build the tree from root 1 (BFS order).
2. Process the vertices in reverse BFS order: `g[parent] ^= g[child] + 1`.

```python
import sys


def main():
    data = list(map(int, sys.stdin.read().split()))
    t = data[0]
    pos = 1
    out = []
    for _ in range(t):
        n = data[pos]
        pos += 1
        adj = [[] for _ in range(n + 1)]
        for _ in range(n - 1):
            u, v = data[pos], data[pos + 1]
            pos += 2
            adj[u].append(v)
            adj[v].append(u)
        parent = [0] * (n + 1)
        order = [1]
        parent[1] = -1
        for x in order:
            for y in adj[x]:
                if y != parent[x]:
                    parent[y] = x
                    order.append(y)
        g = [0] * (n + 1)
        for x in reversed(order[1:]):
            g[parent[x]] ^= g[x] + 1
        out.append('Alice' if g[1] else 'Bob')
    print('\n'.join(out))


main()
```

**Watch out.** A path of `k` edges hanging from a vertex is a Nim pile of size `k`, which is where the "+1 per edge" comes from. The XOR combines sibling branches.

```stdin
1
5
1 2
3 1
3 4
4 5
```

```stdout
Alice
```

### Bob and Ben

**Problem.** A forest of special trees. A move removes one node: removing a leaf keeps the rest of the tree, and removing a non-leaf makes the whole tree vanish. Whoever cannot move loses.

**Idea.** Every tree with `m ≥ 3` nodes has a non-leaf, so "vanish" (value 0) is always an option. Removing a leaf leaves a tree with `m − 1` nodes. So the value depends only on `m`:
- `g(1) = 1`;
- `g(2) = mex{g(1)} = 0`;
- for `m ≥ 3`, `g(m) = mex{0, g(m−1)}`, which alternates: 1 for odd `m` and 2 for even `m`.

The shape parameter `k` never matters.

**Steps.**
1. XOR `g(m_i)` over the trees; print `BOB` if non-zero.

```python
import sys


def g(m):
    if m == 1:
        return 1
    if m == 2:
        return 0
    return 1 if m % 2 else 2


def main():
    data = sys.stdin.buffer.read().split()
    games = int(data[0])
    pos = 1
    out = []
    for _ in range(games):
        n = int(data[pos])
        pos += 1
        x = 0
        for i in range(n):
            x ^= g(int(data[pos + 2 * i]))
        pos += 2 * n
        out.append('BOB' if x else 'BEN')
    print('\n'.join(out))


main()
```

**Watch out.** A lone node has no edge, so it is not a leaf; removing it is the "vanish" move, which ends the same way. Up to 10⁶ trees in total: read the input in bulk.

```stdin
2
2
1 2
1 3
1
3 2
```

```stdout
BEN
BOB
```

### Tower Breakers - The Final Battle

**Problem.** P1 splits a tower of height `H` into `x ≥ 2` towers; P2 picks the `k`-th one, gets `k²` coins, and play continues on that tower. Height 1 ends the game. P1 minimises and P2 maximises the coins. Find the payout for height `N` (up to 10¹⁸).

**Idea.** Invert the question: `G(c)` is the largest height P1 can handle while paying at most `c`. In a split, the `k`-th tower may be as tall as `G(c − k²)`. So

`G(c) = Σ_{k ≥ 1, k² ≤ c} G(c − k²)`

when at least two terms exist, and `G(c) = 1` otherwise. The answer is the smallest `c` with `G(c) ≥ N`. `G` grows exponentially, so `c` stays small.

**Steps.**
1. Grow `G` until it exceeds 10¹⁸.
2. For each query, find the first `c` with `G(c) ≥ N`.

```python
import sys
from bisect import bisect_left


def build():
    G = []
    c = 0
    while not G or G[-1] < 10 ** 18:
        terms = [G[c - k * k] for k in range(1, int(c ** 0.5) + 1)]
        G.append(sum(terms) if len(terms) >= 2 else 1)
        c += 1
    return G


def main():
    G = build()
    best = []                                    # running maximum, for bisect
    m = 0
    for v in G:
        m = max(m, v)
        best.append(m)
    data = sys.stdin.read().split()
    t = int(data[0])
    print('\n'.join(str(bisect_left(best, int(x))) for x in data[1:1 + t]))


main()
```

**Watch out.** P1 orders the towers so the cheap indices get the tall towers. That is why the `k`-th term uses `c − k²`. With `c < 4` only `k = 1` fits, so no real split is possible and only height 1 is reachable.

```stdin
3
4
2
7
```

```stdout
6
4
8
```

### Simple Game

**Problem.** `N` stones in `M` ordered piles; a move splits a pile (of size `≥ 2`) into 2 to `K` non-empty piles. Count the arrangements (compositions of `N` into `M` parts) where the first player wins, modulo 10⁹+7.

**Idea.** **Grundy values.**
- **`K = 2`.** Splitting into exactly two parts gives `g(s) = 1` for even `s` and 0 for odd `s`.
- **`K ≥ 4`.** `g(s) = s − 1`.
- **`K = 3`.** The values are irregular. Compute them: `g(s)` is the mex of the XORs of all 2-part and 3-part splits, with the 2-part XOR sets kept as boolean arrays.

All three facts were verified by brute force.

**Counting ordered tuples with XOR ≠ 0.** Use a Walsh–Hadamard transform over the XOR values. After it, choosing a pile of size `a` multiplies by the sign `χ_w(g(a)) = ±1`. So the pile generating function for "character" `w` is `P_w(z) = Σ_a χ_w(g(a)) z^a`, and the number of tuples with XOR 0 is `(1/W) Σ_w [z^N] P_w(z)^M`.
- **Polynomial products.** Multiply the `M` factors with a float FFT along `z`, for all `w` at once.
- **Staying exact.** The running values are split into 10-bit chunks, so each convolution stays far below 2⁵³ and rounds back exactly. Recombine modulo 10⁹+7.
- **Answer.** All compositions `C(N−1, M−1)` minus the XOR-0 count.

**Steps.**
1. Grundy table for the given `K`.
2. Sign matrix `χ_w(g(a))`, its FFT, then `M` chunked FFT multiplications.
3. Sum `[z^N]` over `w`, divide by `W`, subtract from the total.

```python
import sys
from math import comb

import numpy as np

MOD = 10 ** 9 + 7


def grundy_table(N, K):
    if K == 2:
        return [0] + [1 if s % 2 == 0 else 0 for s in range(1, N + 1)]
    if K >= 4:
        return [0] + [s - 1 for s in range(1, N + 1)]
    W = 1024
    idx = np.arange(W)
    g = [0] * (N + 1)
    two = [None] * (N + 1)                       # xor values of 2-part splits
    for t in range(1, N + 1):
        p2 = np.zeros(W, dtype=bool)
        for a in range(1, t):
            p2[g[a] ^ g[t - a]] = True
        p3 = np.zeros(W, dtype=bool)
        for a in range(1, t - 1):
            p3 |= two[t - a][idx ^ g[a]]
        two[t] = p2
        g[t] = int(np.flatnonzero(~(p2 | p3))[0])
    return g


def main():
    N, M, K = map(int, sys.stdin.read().split()[:3])
    g = grundy_table(N, K)
    W = 1
    while W <= max(g):
        W *= 2
    w = np.arange(W)
    ga = np.array(g[1:], dtype=np.int64)
    bits = np.bitwise_and.outer(w, ga)
    par = np.zeros_like(bits)
    while bits.any():
        par ^= bits & 1
        bits >>= 1
    L = 1
    while L < 2 * N + 1:
        L *= 2
    P = np.zeros((W, L))
    P[:, 1:N + 1] = 1 - 2 * par                  # sign of each pile size per character
    FP = np.fft.rfft(P, L, axis=1)
    dp = np.zeros((W, N + 1), dtype=np.int64)
    dp[:, 0] = 1
    for _ in range(M):
        new = np.zeros_like(dp)
        for shift in (0, 10, 20):
            chunk = ((dp >> shift) & 1023).astype(np.float64)
            conv = np.fft.irfft(np.fft.rfft(chunk, L, axis=1) * FP, L, axis=1)[:, :N + 1]
            new = (new + (np.rint(conv).astype(np.int64) % MOD << shift)) % MOD
        dp = new
    zero = int(dp[:, N].sum() % MOD) * pow(W, MOD - 2, MOD) % MOD
    print((comb(N - 1, M - 1) - zero) % MOD)


main()
```

**Watch out.**
- **What `K` means.** "Split into 2 to `K` piles" includes every count up to `K`. That is why `K ≥ 4` already gives the clean `s − 1`, while `K = 3` does not.
- **Exactness.** The chunked FFT keeps every intermediate below about `6·10⁸`, so rounding is exact, and the modular recombination never overflows `int64`.

```stdin
4 3 3
```

```stdout
3
```

### Permutation game

**Problem.** Players remove one number at a time from a permutation (`n ≤ 15`). Whoever leaves an increasing sequence wins.

**Idea.** A DP over the subsets of remaining positions. Let `win[mask]` be true if the player to move wins. A move removes position `i`; it wins at once if `mask − i` is increasing, and otherwise it wins if `win[mask − i]` is false.
- **Vectorised.** Process the masks layer by layer (by popcount) with NumPy, over all `2¹⁵` masks at once.
- **Increasing test.** A mask is increasing when it contains no "bad pair" `i < j` with `p_i > p_j`.

**Steps.**
1. `inc[mask]` from the list of bad pairs.
2. For each popcount layer, `win[mask] = OR_i (inc[mask^bit] | ~win[mask^bit])` over the bits in the mask.

```python
import sys

import numpy as np


def solve(p):
    n = len(p)
    full = 1 << n
    masks = np.arange(full)
    inc = np.ones(full, dtype=bool)
    for i in range(n):
        for j in range(i + 1, n):
            if p[i] > p[j]:
                pm = (1 << i) | (1 << j)
                inc &= (masks & pm) != pm
    pop = np.zeros(full, dtype=np.int64)
    for i in range(n):
        pop += (masks >> i) & 1
    win = np.zeros(full, dtype=bool)
    for c in range(2, n + 1):
        layer = masks[pop == c]
        res = np.zeros(len(layer), dtype=bool)
        for i in range(n):
            has = (layer >> i) & 1 == 1
            sub = layer[has] ^ (1 << i)
            res[has] |= inc[sub] | ~win[sub]
        win[layer] = res & ~inc[layer]
    return 'Alice' if win[full - 1] else 'Bob'


def main():
    data = list(map(int, sys.stdin.read().split()))
    t = data[0]
    pos = 1
    out = []
    for _ in range(t):
        n = data[pos]
        out.append(solve(data[pos + 1:pos + 1 + n]))
        pos += 1 + n
    print('\n'.join(out))


main()
```

**Watch out.** A mask that is already increasing is a finished game. It never needs a `win` value because no one moves from it, which is why `win` is masked with `~inc`. The pure-Python recursion over 3·10⁶ transitions per test is too slow for 100 tests.

```stdin
2
3
1 3 2
5
5 3 2 1 4
```

```stdout
Alice
Bob
```

### Move the Coins

**Problem.** In a rooted tree, a move pushes one or more coins from a node to its parent. Each query re-hangs the subtree of `u` under `v`. Print whether the first player wins, or `INVALID` if the result is no longer a tree.

**Idea.** This is **staircase Nim**: only the coins at odd depth matter, and the game value is the XOR of `c_i` over odd-depth nodes. Coins moved from even to odd depth can be moved straight back.

Re-hanging the subtree of `u` under `v` shifts every depth in that subtree by `depth(v) + 1 − depth(u)`.
- **Even shift.** Nothing changes.
- **Odd shift.** Every coin in the subtree swaps parity, so the value changes by the XOR of **all** coins in the subtree.
- **Invalid.** The query is invalid when `v` lies inside `u`'s subtree (Euler-tour interval test).

**Steps.**
1. Iterative DFS for depth, `tin`/`tout`, and the subtree XOR of the coins.
2. For each query: `INVALID`, or `YES`/`NO` from the adjusted XOR.

```python
import sys


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    c = [0] + [int(x) for x in data[1:1 + n]]
    adj = [[] for _ in range(n + 1)]
    pos = 1 + n
    for _ in range(n - 1):
        a, b = int(data[pos]), int(data[pos + 1])
        pos += 2
        adj[a].append(b)
        adj[b].append(a)
    depth = [0] * (n + 1)
    parent = [0] * (n + 1)
    tin = [0] * (n + 1)
    tout = [0] * (n + 1)
    sub = c[:]
    order = []
    stack = [1]
    parent[1] = -1
    timer = 0
    while stack:
        x = stack.pop()
        tin[x] = timer
        timer += 1
        order.append(x)
        for y in adj[x]:
            if y != parent[x]:
                parent[y] = x
                depth[y] = depth[x] + 1
                stack.append(y)
    for x in reversed(order):
        if parent[x] > 0:
            sub[parent[x]] ^= sub[x]
    size = [1] * (n + 1)
    for x in reversed(order):
        if parent[x] > 0:
            size[parent[x]] += size[x]
    for x in range(1, n + 1):
        tout[x] = tin[x] + size[x]
    total = 0
    for x in range(1, n + 1):
        if depth[x] % 2:
            total ^= c[x]
    q = int(data[pos])
    pos += 1
    out = []
    for _ in range(q):
        u, v = int(data[pos]), int(data[pos + 1])
        pos += 2
        if tin[u] <= tin[v] < tout[u]:
            out.append('INVALID')
            continue
        x = total
        if (depth[v] + 1 - depth[u]) % 2:
            x ^= sub[u]
        out.append('YES' if x else 'NO')
    print('\n'.join(out))


main()
```

**Watch out.** The DFS stack visits each subtree in one contiguous block of `tin` values, so `[tin, tin + size)` is a valid interval. Coins at the root (depth 0) never count.

```stdin
6
0 2 2 1 3 2
1 2
1 3
3 4
3 5
4 6
3
6 2
4 1
3 6
```

```stdout
NO
YES
INVALID
```

### Play on benders

**Problem.** Soldiers sit on the nodes of a DAG. A move pushes one soldier along an edge; whoever cannot move loses. Bumi moves first. Answer several starting configurations.

**Idea.** A sum of games on a DAG: each node's Grundy value is the mex of its successors' values, computed in reverse topological order (Kahn's algorithm on the reversed edges). XOR the values of the soldiers' nodes.

**Steps.**
1. Out-degree counts; start from the sinks (value 0); a node is processed once all its successors have been.
2. For each query, print `Bumi` if the XOR is non-zero, else `Iroh`.

```python
import sys


def main():
    data = sys.stdin.buffer.read().split()
    n, m = int(data[0]), int(data[1])
    succ = [[] for _ in range(n + 1)]
    pred = [[] for _ in range(n + 1)]
    pos = 2
    for _ in range(m):
        u, v = int(data[pos]), int(data[pos + 1])
        pos += 2
        succ[u].append(v)
        pred[v].append(u)
    outdeg = [len(s) for s in succ]
    g = [0] * (n + 1)
    ready = [x for x in range(1, n + 1) if outdeg[x] == 0]
    while ready:
        x = ready.pop()
        seen = {g[y] for y in succ[x]}
        v = 0
        while v in seen:
            v += 1
        g[x] = v
        for p in pred[x]:
            outdeg[p] -= 1
            if outdeg[p] == 0:
                ready.append(p)
    q = int(data[pos])
    pos += 1
    out = []
    for _ in range(q):
        k = int(data[pos])
        x = 0
        for i in range(k):
            x ^= g[int(data[pos + 1 + i])]
        pos += 1 + k
        out.append('Bumi' if x else 'Iroh')
    print('\n'.join(out))


main()
```

**Watch out.** Several soldiers on the same node cancel in pairs. Recursion would overflow on long chains, so the topological order is iterative.

```stdin
10 10
1 10
3 10
7 8
6 8
7 4
9 4
7 6
5 8
1 8
2 8
5
4
10 7 6 4
3
1 9 4
3
8 3 5
3
4 9 7
3
7 9 10
```

```stdout
Bumi
Iroh
Iroh
Bumi
Bumi
```

### New Year Game

**Problem.** Players alternately take numbers into their own scores. Koca (second) wins if `|S_b − S_k|` is divisible by 3. Who wins?

**Idea.** Only the residues modulo 3 matter, and multiples of 3 are irrelevant. Koca can pair the moves: answer every residue-1 number with another residue-1 number, and the same for residue 2. Then the difference stays `≡ 0 (mod 3)`, which works exactly when both counts are even. If either count is odd, Balsa wins. Brute force over the residue counts confirms it.

**Steps.**
1. Count the numbers `≡ 1` and `≡ 2 (mod 3)`; print `Koca` if both counts are even.

```python
import sys


def main():
    data = list(map(int, sys.stdin.read().split()))
    t = data[0]
    pos = 1
    out = []
    for _ in range(t):
        n = data[pos]
        a = data[pos + 1:pos + 1 + n]
        pos += 1 + n
        c1 = sum(1 for x in a if x % 3 == 1)
        c2 = sum(1 for x in a if x % 3 == 2)
        out.append('Koca' if c1 % 2 == 0 and c2 % 2 == 0 else 'Balsa')
    print('\n'.join(out))


main()
```

**Watch out.** Multiples of 3 act as free "pass" moves for either side, which does not change the parity argument.

```stdin
2
3
7 6 18
1
3
```

```stdout
Balsa
Koca
```

### Stone Piles

**Problem.** A move splits a pile into **two or more piles of distinct sizes**. Piles up to 50; whoever cannot move loses.

**Idea.** Compute `g(x)` for `x ≤ 50` as the mex over all partitions of `x` into at least two distinct parts of the XOR of their values. The number of distinct-part partitions of 50 is only 3658, so enumerate them recursively (increasing parts).

**Steps.**
1. Grundy table by increasing `x`, enumerating the distinct partitions.
2. XOR over the piles; print `ALICE` if non-zero.

```python
import sys


def build(N):
    g = [0] * (N + 1)
    for x in range(1, N + 1):
        seen = set()

        def rec(rem, smallest, acc, parts):
            if rem == 0:
                if parts >= 2:
                    seen.add(acc)
                return
            for p in range(smallest, rem + 1):
                if p == rem or rem - p > p:           # next parts must be larger than p
                    rec(rem - p, p + 1, acc ^ g[p], parts + 1)

        rec(x, 1, 0, 0)
        v = 0
        while v in seen:
            v += 1
        g[x] = v
    return g


G = build(50)


def main():
    data = list(map(int, sys.stdin.read().split()))
    t = data[0]
    pos = 1
    out = []
    for _ in range(t):
        n = data[pos]
        x = 0
        for v in data[pos + 1:pos + 1 + n]:
            x ^= G[v]
        pos += 1 + n
        out.append('ALICE' if x else 'BOB')
    print('\n'.join(out))


main()
```

**Watch out.** A pile of 1 or 2 cannot be split into distinct parts, so its value is 0. The pruning `rem − p > p` keeps the parts strictly increasing.

```stdin
4
1
4
2
1 2
3
1 3 4
1
8
```

```stdout
BOB
BOB
ALICE
BOB
```

### Chocolate Game

**Problem.** For every contiguous segment (length `≥ 2`) of a non-decreasing array, play: a move lowers one pile while keeping the order. The last mover wins. Count the segments the first player wins.

**Idea.** Use the differences `d_i = a_i − a_{i−1}` (the first one relative to 0). Lowering `a_i` moves units from `d_i` into `d_{i+1}`, which is **staircase Nim** with the last difference as the "floor". So the game value is the XOR of `d_r, d_{r−2}, d_{r−4}, …` down the segment, where the segment's first pile counts with its full height `a_l`.

Let `Q[i] = d_i ⊕ Q[i−2]` (prefix XOR within each parity class). For a segment `[l, r]`:
- if `r − l` is odd, the value is `Q[r] ⊕ Q[l−1]`;
- if `r − l` is even, the value is `Q[r] ⊕ Q[l] ⊕ a_l`.

Count the zero-value segments with two hash maps (one per parity of `l`) and subtract from the total.

**Steps.**
1. Compute `d` and `Q`.
2. Sweep `r`, querying and updating the two maps; answer = all segments − zero segments.

```python
import sys
from collections import defaultdict


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    a = [0] + [int(x) for x in data[1:1 + n]]          # 1-based
    Q = [0] * (n + 1)
    for i in range(1, n + 1):
        Q[i] = (a[i] - a[i - 1]) ^ (Q[i - 2] if i >= 2 else 0)
    odd_map = [defaultdict(int), defaultdict(int)]      # by parity of l: counts of Q[l-1]
    even_map = [defaultdict(int), defaultdict(int)]     # by parity of l: counts of Q[l] ^ a[l]
    zero = 0
    for r in range(1, n + 1):
        if r >= 2:                                      # odd gap: l = r-1, r-3, ...
            l = r - 1
            odd_map[l % 2][Q[l - 1]] += 1
            zero += odd_map[(r + 1) % 2][Q[r]]
        if r >= 3:                                      # even gap: l = r-2, r-4, ...
            l = r - 2
            even_map[l % 2][Q[l] ^ a[l]] += 1
            zero += even_map[r % 2][Q[r]]
    total = n * (n - 1) // 2
    print(total - zero)


main()
```

**Watch out.** Segments of length 2 have `r − l = 1` (the odd case). A start `l` is added to its map just before the first `r` that may use it, so each segment is counted once. The answer is checked against a brute-force game search on small arrays.

```stdin
5
1 1 2 2 3
```

```stdout
5
```

### The Prime Game

**Problem.** Nim where each move removes exactly 2, 3, 5, 7, 11 or 13 balls from one bucket (up to 10¹⁸ balls). Who wins?

**Idea.** A subtraction game has eventually periodic Grundy values. For this set, the values have period 9: `0, 0, 1, 1, 2, 2, 3, 3, 4` for `n mod 9 = 0..8` (checked by direct computation up to 10⁴). XOR them over the buckets.

**Steps.**
1. `g(n) = [0,0,1,1,2,2,3,3,4][n % 9]`; print `Manasa` if the XOR is non-zero.

```python
import sys

TABLE = [0, 0, 1, 1, 2, 2, 3, 3, 4]


def main():
    data = sys.stdin.read().split()
    t = int(data[0])
    pos = 1
    out = []
    for _ in range(t):
        n = int(data[pos])
        x = 0
        for v in data[pos + 1:pos + 1 + n]:
            x ^= TABLE[int(v) % 9]
        pos += 1 + n
        out.append('Manasa' if x else 'Sandy')
    print('\n'.join(out))


main()
```

**Watch out.** Win/lose alone is not enough with several buckets; you need the Grundy numbers to XOR them.

```stdin
2
2
10 10
3
2 2 3
```

```stdout
Sandy
Manasa
```

### Vertical Rooks

**Problem.** Each column holds one rook of each player; rooks move vertically without jumping. Whoever cannot move loses, and player 2 moves first.

**Idea.** In each column, the only thing that matters is the gap between the two rooks, `|r₁ − r₂| − 1`. Moving toward the opponent shrinks the gap like a Nim pile. Moving away is reversible (the opponent follows), exactly as in Poker Nim. So it is Nim on the gaps. The player to move (player 2) wins if the XOR is non-zero.

**Steps.**
1. XOR `|r1[i] − r2[i]| − 1` over the columns; print `player-2` if non-zero.

```python
import sys


def main():
    data = list(map(int, sys.stdin.read().split()))
    t = data[0]
    pos = 1
    out = []
    for _ in range(t):
        n = data[pos]
        r1 = data[pos + 1:pos + 1 + n]
        r2 = data[pos + 1 + n:pos + 1 + 2 * n]
        pos += 1 + 2 * n
        x = 0
        for a, b in zip(r1, r2):
            x ^= abs(a - b) - 1
        out.append('player-2' if x else 'player-1')
    print('\n'.join(out))


main()
```

**Watch out.** Moving away cannot go on forever: the board edge limits it, and the Nim winner simply undoes such moves.

```stdin
1
3
1
2
2
3
1
1
```

```stdout
player-2
```

### A stones game

**Problem.** Piles `1, 2, …, N`; a move destroys at least half of a pile. Print the smallest number of stones the first player must destroy in a winning first move, or 0 if the first player loses.

**Idea.** After a move, a pile `x` leaves any `y ≤ ⌊x/2⌋`, so `g(x) = bit_length(x)`. Over `1..N`, each full bit-length class `b ≥ 2` has an even size `2^{b−1}` and cancels. Only class 1 (the pile `1`) and the top class `B = bit_length(N)` (if its count is odd) remain, which gives the total `X`.

A winning move takes a pile of class `b` down to class `t = b ⊕ X < b`, so `b` must contain the top bit of `X`. The cheapest choice is the smallest such `b` (cost grows with `b`), using its smallest pile `2^{b−1}`. It leaves either `y = 2^t − 1` (if `t ≤ b − 2`) or `y = x/2` (if `t = b − 1`).

The result depends only on `B` and the parity of the top class, so the answers are tabulated once.

**Steps.**
1. Precompute the answer for every `(B, parity)` (62 cases).
2. Per query: look up `B = bit_length(N)` and `(N − 2^{B−1} + 1) mod 2`.

```python
import sys


def answer(B, top_odd):
    X = 1 if B == 1 else (1 ^ (B if top_odd else 0))
    if X == 0:
        return 0
    b = X.bit_length()                    # smallest class containing X's top bit
    b = 1 << (b - 1)
    t = b ^ X
    x = 1 << (b - 1)                      # smallest pile of class b
    y = 0 if t == 0 else min(x // 2, (1 << t) - 1)
    return x - y


def main():
    table = {(B, p): answer(B, p) for B in range(1, 32) for p in (0, 1)}
    data = sys.stdin.buffer.read().split()
    t = int(data[0])
    out = []
    for x in data[1:1 + t]:
        n = int(x)
        B = n.bit_length()
        out.append(table[(B, (n - (1 << (B - 1)) + 1) & 1)])
    sys.stdout.write('\n'.join(map(str, out)) + '\n')


main()
```

**Watch out.**
- **Class versus pile size.** The "class" `b` is a bit length (1, 2, …), not a pile size. The smallest class containing `X`'s top bit is the power of two `2^{⌊log₂ X⌋}` used as a bit length.
- **Testing.** The table is checked against a brute-force search for small `N`. There are up to 10⁶ queries, hence the lookup table.

```stdin
5
1
10
6
8
123456
```

```stdout
1
7
2
7
32768
```

### Tastes Like Winning

**Problem.** Count the ordered `n`-tuples of **distinct** values in `[1, 2^m)` whose XOR is non-zero (so the first player wins Nim), modulo 10⁹+7.

**Idea.** Let `A(k) = (2^m − 1)(2^m − 2)…(2^m − k)` be all the ordered `k`-tuples of distinct non-zero values, and let `Z(k)` count those with XOR 0. Choose the first `k − 1` values freely; the last one is forced to be their XOR. That forced value is invalid when:
- it is 0, which happens `Z(k−1)` times; or
- it equals one of the earlier values. Removing that value leaves a `(k−2)`-tuple with XOR 0, the removed value has `2^m − 1 − (k−2)` options, and its position has `k − 1` options.

So `Z(k) = A(k−1) − Z(k−1) − (k−1)(2^m − k + 1) Z(k−2)`, and the answer is `A(n) − Z(n)`.

**Steps.**
1. If `2^m − 1 < n`, the answer is 0.
2. Iterate the recurrence modulo p, `O(n)` time.

```python
import sys

MOD = 10 ** 9 + 7


def main():
    n, m = map(int, sys.stdin.read().split()[:2])
    if m < 30 and (1 << m) - 1 < n:
        print(0)
        return
    V = (pow(2, m, MOD) - 1) % MOD                 # 2^m - 1 (mod p)
    A_prev = 1                                     # A(0)
    z2, z1 = 1, 0                                  # Z(0) = 1 (empty tuple), Z(1) = 0
    A_cur = V % MOD                                # A(1)
    for k in range(2, n + 1):
        z = (A_cur - z1 - (k - 1) * ((V - (k - 2)) % MOD) % MOD * z2) % MOD
        A_cur = A_cur * ((V - (k - 1)) % MOD) % MOD
        z2, z1 = z1, z
    print((A_cur - (z1 if n >= 2 else 0)) % MOD)


main()
```

**Watch out.** `Z(0) = 1`: the empty tuple has XOR 0, which makes the "repeated value" term right for `k = 2` (a pair `(x, x)` is not allowed). The loop runs up to 10⁷ times, so it is kept to a few multiplications per step.

```stdin
2 2
```

```stdout
6
```
