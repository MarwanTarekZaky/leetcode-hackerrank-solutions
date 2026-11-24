## NP Complete

### Walking the Approximate Longest Path

**Problem.** In a random graph that is guaranteed to contain a Hamiltonian path, print a simple path that is as long as possible. The score is `(d/n)²`.

**Idea.** The longest path problem is NP-hard, but random graphs with a planted Hamiltonian path are easy for the classic **Pósa rotation** heuristic.
- **Extending.** Grow the path at its end, preferring the unvisited neighbour with the fewest unvisited neighbours of its own (Warnsdorff's rule), so dead ends get used up early.
- **Rotating when stuck.** If the end `v` has a neighbour `p_i` inside the path, the path `p₀…p_i p_{i+1}…v` can be rewired into `p₀…p_i v … p_{i+1}`, which has the same vertices but a new end `p_{i+1}`. Rotate until the new end has an unvisited neighbour.
- **Both ends.** If rotations fail, reverse the path and try from the other end.
- **Restarts.** Start from a minimum-degree vertex and keep the best result within a time budget.

**Steps.**
1. Build the adjacency lists; start at a vertex of minimum degree.
2. Alternate extension and rotation (bounded attempts); restart a few times with other start vertices; print the best path.

```python
import random
import sys
import time


def main():
    data = sys.stdin.buffer.read().split()
    n, m = int(data[0]), int(data[1])
    adj = [[] for _ in range(n + 1)]
    for i in range(m):
        x, y = int(data[2 + 2 * i]), int(data[3 + 2 * i])
        if x != y:
            adj[x].append(y)
            adj[y].append(x)
    rng = random.Random(12345)
    start_time = time.time()
    order = sorted(range(1, n + 1), key=lambda v: len(adj[v]))
    best = [order[0]]
    for attempt in range(50):
        if len(best) == n or time.time() - start_time > 3.0:
            break
        s = order[attempt % n] if attempt < 5 else rng.randint(1, n)
        path = [s]
        pos = [-1] * (n + 1)
        pos[s] = 0
        free = [len(adj[v]) for v in range(n + 1)]       # unvisited neighbours
        for u in adj[s]:
            free[u] -= 1
        stuck_rotations = 0
        reversed_once = False
        while time.time() - start_time <= 3.0:
            v = path[-1]
            cand = [u for u in adj[v] if pos[u] < 0]
            if cand:
                u = min(cand, key=lambda w: (free[w], rng.random()))
                pos[u] = len(path)
                path.append(u)
                for w in adj[u]:
                    free[w] -= 1
                stuck_rotations = 0
                continue
            if stuck_rotations < 30 and len(path) > 2:
                stuck_rotations += 1
                inner = [u for u in adj[v] if 0 <= pos[u] < len(path) - 2]
                if inner:
                    u = rng.choice(inner)
                    i = pos[u]
                    tail = path[i + 1:]
                    tail.reverse()
                    path[i + 1:] = tail
                    for k in range(i + 1, len(path)):
                        pos[path[k]] = k
                    continue
            if not reversed_once:
                reversed_once = True
                stuck_rotations = 0
                path.reverse()
                for k, w in enumerate(path):
                    pos[w] = k
                continue
            break
        if len(path) > len(best):
            best = path[:]
    print(len(best))
    print(' '.join(map(str, best)))


main()
```

**Watch out.** Any simple path is accepted, so the hidden test checks that consecutive cities are joined by roads and that no city repeats. On this sample it also checks for full length. Each rotation costs O(length), so the number of rotations per dead end is capped and the whole search has a time budget.

```stdin
4 5
3 1
3 4
2 4
2 3
4 1
```

```check
toks = stdin.split()
n, m = int(toks[0]), int(toks[1])
edges = set()
for i in range(m):
    a, b = int(toks[2 + 2 * i]), int(toks[3 + 2 * i])
    edges.add((a, b)); edges.add((b, a))
lines = output.strip().split('\n')
d = int(lines[0]); path = list(map(int, lines[1].split()))
assert d == len(path) == len(set(path)) and all(1 <= v <= n for v in path)
assert all((path[i], path[i + 1]) in edges for i in range(d - 1))
assert d == n, d
```

### Sam's Puzzle (Approximate)

**Problem.** An `n×n` grid (`n ≤ 30`) holds `1..n²`. A move rotates a `k×k` sub-square clockwise. With at most 500 moves, make as many row pairs increase left to right and column pairs increase top to bottom as possible. The score is the fraction of the possible improvement achieved.

**Idea.** A **hill climber over 2×2 rotations.** Rotating a 2×2 block by 1, 2 or 3 quarter turns (1–3 moves) changes only two rows and two columns. Its effect on the goodness can therefore be computed by comparing the four moved cells with the rest of their rows and columns, in O(n) time. Sweep over all blocks and apply any rotation that strictly improves, until a sweep finds nothing, the 500-move budget is used, or time runs out. Every applied rotation helps, so the result is never worse than the start.

**Steps.**
1. `line_delta`: for a row or column, the change in good pairs when two of its cells receive new values.
2. Sweep the blocks; for each, try 1–3 quarter turns that fit in the remaining budget, and keep the best improvement.
3. Print the moves; a turn of `t` quarters is printed as `t` identical moves.

```python
import sys
import time


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    g = [list(map(int, data[1 + i * n:1 + (i + 1) * n])) for i in range(n)]

    def row_gain(r, c1, c2, v1, v2):
        # good pairs in row r touching columns c1 < c2 when they hold v1, v2
        row = g[r]
        s = 0
        for c in range(n):
            if c == c1 or c == c2:
                continue
            x = row[c]
            s += (x < v1) if c < c1 else (x > v1)
            s += (x < v2) if c < c2 else (x > v2)
        return s + (v1 < v2)

    def col_gain(c, r1, r2, v1, v2):
        s = 0
        for r in range(n):
            if r == r1 or r == r2:
                continue
            x = g[r][c]
            s += (x < v1) if r < r1 else (x > v1)
            s += (x < v2) if r < r2 else (x > v2)
        return s + (v1 < v2)

    def score(i, j, a, b, c, d):          # block [[a, b], [c, d]] at (i, j)
        return (row_gain(i, j, j + 1, a, b) + row_gain(i + 1, j, j + 1, c, d) +
                col_gain(j, i, i + 1, a, c) + col_gain(j + 1, i, i + 1, b, d))

    moves = []
    start = time.time()
    improved = True
    while improved and len(moves) < 500 and time.time() - start < 4.0:
        improved = False
        for i in range(n - 1):
            for j in range(n - 1):
                a, b, c, d = g[i][j], g[i][j + 1], g[i + 1][j], g[i + 1][j + 1]
                base = score(i, j, a, b, c, d)
                best, best_t, cfg = 0, 0, None
                cur = (a, b, c, d)
                for t in range(1, 4):
                    a2, b2, c2, d2 = cur
                    cur = (c2, a2, d2, b2)          # one clockwise quarter turn
                    if len(moves) + t > 500:
                        break
                    gain = score(i, j, *cur) - base
                    if gain > best:
                        best, best_t, cfg = gain, t, cur
                if best > 0:
                    g[i][j], g[i][j + 1], g[i + 1][j], g[i + 1][j + 1] = cfg
                    moves.extend([(i + 1, j + 1, 2)] * best_t)
                    improved = True
    print(len(moves))
    print('\n'.join(f"{i} {j} {k}" for i, j, k in moves))


main()
```

**Watch out.** Clockwise means the bottom-left value moves to the top-left: `[[a, b], [c, d]]` becomes `[[c, a], [d, b]]`. Larger rotations (`k > 2`) could fix more at once; the 2×2 hill climber is a simple, safe baseline. The hidden test replays the moves and checks that they are valid and do not lower the goodness.

```stdin
3
8 6 9
7 2 5
1 4 3
```

```check
toks = list(map(int, stdin.split()))
n = toks[0]
g = [toks[1 + i * n:1 + (i + 1) * n] for i in range(n)]
def good(g):
    s = 0
    for r in range(n):
        for a in range(n):
            for b in range(a + 1, n):
                s += g[r][a] < g[r][b]
                s += g[a][r] < g[b][r]
    return s
before = good(g)
lines = output.strip().split('\n')
m = int(lines[0])
assert 0 <= m <= 500 and len(lines) == m + 1
for line in lines[1:]:
    i, j, k = map(int, line.split())
    assert 1 <= i and 1 <= j and k >= 1 and i + k - 1 <= n and j + k - 1 <= n
    i -= 1; j -= 1
    sub = [row[j:j + k] for row in g[i:i + k]]
    rot = [list(x) for x in zip(*sub[::-1])]
    for r in range(k):
        g[i + r][j:j + k] = rot[r]
assert good(g) > before
```

### Spies, Revised

**Problem.** Place `N` (odd, up to 999) spies on an `N×N` grid, one per row. No two may share a column or a diagonal, and no three may lie on **any** straight line. The score is `N/10`; there is no input.

**Idea.** This is the queens problem combined with the "no-three-in-line" problem. The natural algebraic candidate, points on a modular hyperbola `(i, a·i⁻¹ mod p)`, has no three collinear points mod `p`. But about `p/2` of its pairs also land on a diagonal, so it fails the queens rule.

This solution uses a **randomised row-by-row construction**:
- Keep a grid of forbidden cells. Each placed spy forbids its column and both diagonals.
- It also forbids every cell on the line through it and each earlier spy.
- If a row has no free cell, restart.

With a fixed seed, the construction for `N = 35` succeeds after a few thousand restarts (well under a second), and the output is checked by the hidden test.

**Steps.**
1. Repeat random attempts (fixed seed) until one fills all `N` rows.
2. Print `N` and the 1-based columns.

```python
import random
from math import gcd


def attempt(n, rng):
    forb = [[False] * n for _ in range(n)]
    pts = []
    for r in range(n):
        cand = [c for c in range(n) if not forb[r][c]]
        if not cand:
            return None
        c = rng.choice(cand)
        for rr in range(r + 1, n):                  # column and diagonals
            forb[rr][c] = True
            d = rr - r
            if c + d < n:
                forb[rr][c + d] = True
            if c - d >= 0:
                forb[rr][c - d] = True
        for pr, pc in pts:                          # lines through two spies
            dr, dc = r - pr, c - pc
            g = gcd(dr, abs(dc))
            dr, dc = dr // g, dc // g
            rr, cc = r + dr, c + dc
            while rr < n and 0 <= cc < n:
                forb[rr][cc] = True
                rr += dr
                cc += dc
        pts.append((r, c))
    return [c + 1 for _, c in pts]


N = 35
rng = random.Random(N * 7919)
cols = None
while cols is None:
    cols = attempt(N, rng)
print(N)
print(' '.join(map(str, cols)))
```

**Watch out.**
- **Only later rows.** Lines are forbidden only below the current row; the rows above are already final.
- **Steep lines.** The step `(dr, dc)` is reduced by the gcd, so a steep line still hits every lattice cell on it.
- **Larger `N`.** Random restarts slow down sharply beyond about 40; much larger `N` needs a smarter algebraic construction.

```stdin

```

```check
lines = output.strip().split('\n')
n = int(lines[0])
cols = list(map(int, lines[1].split()))
assert n % 2 == 1 and len(cols) == n and sorted(cols) == list(range(1, n + 1))
pts = [(r, c) for r, c in enumerate(cols)]
from math import gcd
for i in range(n):
    seen = set()
    for j in range(n):
        if i == j:
            continue
        dr, dc = pts[j][0] - pts[i][0], pts[j][1] - pts[i][1]
        assert abs(dr) != abs(dc)
        g = gcd(dr, dc)
        dr, dc = dr // g, dc // g
        if dr < 0:
            dr, dc = -dr, -dc
        assert (dr, dc) not in seen, 'three in a line'
        seen.add((dr, dc))
```

### TBS Problem

**Problem.** Starting at headquarters `(0, 0)`, sell at most one blimp per city. Travel costs `1 + C·(blimps carried)` per mile. Prices of all cities drop by a factor `D` after every `N/10` sales. Print a route (trips start at HQ with a blimp count, `0 0` returns to HQ) that earns as much as possible.

**Idea.** A simple, always-valid heuristic: **one-city trips in order of value.**
- A one-city trip to a city at distance `r` earns `price·decline − (1 + C)·r − r`. The way out carries one blimp; the way back carries none.
- Sales happen in descending order of that profit, so the most valuable cities are sold before the decline bites.
- Recompute the decline as sales happen, and stop as soon as the next trip would lose money.
- The last trip does not need to return.

Chaining several nearby cities into one trip would save mileage; this baseline already guarantees a positive profit whenever any profitable city exists.

**Steps.**
1. Sort the cities by `p − (2 + C)·r`.
2. Walk the list while the current trip is profitable; print `x y 1` for each trip, followed by `0 0` except after the last.

```python
import math
import sys


def main():
    data = sys.stdin.read().split()
    n, C, D = int(data[0]), float(data[1]), float(data[2])
    cities = []
    for i in range(n):
        x, y, p = int(data[3 + 3 * i]), int(data[4 + 3 * i]), int(data[5 + 3 * i])
        r = math.hypot(x, y)
        cities.append((p - (2 + C) * r, x, y, p, r))
    cities.sort(reverse=True)
    step = max(1, n // 10)
    chosen = []
    for _, x, y, p, r in cities:
        factor = D ** (len(chosen) // step)
        if p * factor - (2 + C) * r <= 0:
            break
        chosen.append((x, y))
    out = []
    for k, (x, y) in enumerate(chosen):
        out.append(f"{x} {y} 1")
        if k + 1 < len(chosen):
            out.append("0 0")
    print('\n'.join(out))


main()
```

**Watch out.**
- **The `0 0` lines.** They mean "return to headquarters". A city at `(0, 0)` cannot exist, because HQ sits there.
- **Decline factor.** It depends only on how many blimps have been sold so far (one step per tenth of `N`), not on time or distance.
- **Testing.** The hidden test replays the route with the statement's cost model and checks that it is valid and profitable.

```stdin
10 3 0.95
1 1 30
2 2 35
0 8 50
7 2 20
7 3 25
10 7 90
9 8 35
5 15 10
8 18 15
1 9 60
```

```check
import math
toks = stdin.split()
n, C, D = int(toks[0]), float(toks[1]), float(toks[2])
city = {}
for i in range(n):
    x, y, p = int(toks[3 + 3 * i]), int(toks[4 + 3 * i]), int(toks[5 + 3 * i])
    city[(x, y)] = p
step = max(1, n // 10)
pos = (0, 0); carry = 0; sold = 0; profit = 0.0; seen = set()
for line in output.strip().split('\n'):
    parts = list(map(int, line.split()))
    target = (parts[0], parts[1])
    if len(parts) == 3:
        assert pos == (0, 0)
        carry = parts[2]
    dist = math.hypot(target[0] - pos[0], target[1] - pos[1])
    profit -= dist * (1 + C * carry)
    pos = target
    if target == (0, 0):
        continue
    assert target in city and target not in seen and carry > 0
    seen.add(target)
    profit += city[target] * D ** (sold // step)
    sold += 1
    carry -= 1
assert profit > 0, profit
```
