## Queues

### Queue using Two Stacks

**Problem.** Process enqueue, dequeue and "print front" queries on a queue, implemented with two stacks.

**Idea.** Push onto an `inbox` stack. Read from an `outbox` stack, refilling it from `inbox` (which reverses the order) only when it is empty. Each element moves at most twice, so every operation is amortised O(1).

**Steps.**
1. Type 1: push to `inbox`. Types 2 and 3: if `outbox` is empty, move everything over; then pop or peek.

```python
import sys


def main():
    data = sys.stdin.read().split()
    q = int(data[0])
    inbox, outbox = [], []
    out = []
    pos = 1
    for _ in range(q):
        t = data[pos]
        if t == '1':
            inbox.append(data[pos + 1])
            pos += 2
            continue
        pos += 1
        if not outbox:
            while inbox:
                outbox.append(inbox.pop())
        if t == '2':
            outbox.pop()
        else:
            out.append(outbox[-1])
    print('\n'.join(out))


main()
```

**Watch out.** Refilling `outbox` while it still holds elements would break the FIFO order; only refill when it is empty.

```stdin
10
1 42
2
1 14
3
1 28
3
1 60
1 78
2
2
```

```stdout
14
14
```

### Castle on the Grid

**Problem.** A piece slides any distance in one of four directions per move, stopping at walls `X` or the grid edge. Find the fewest moves from start to goal.

**Idea.** BFS where the neighbours of a cell are **all** the cells reachable along each direction until blocked. Each move costs 1 however far it slides. While sliding, keep going past cells that were already visited at the same distance, because the slide can continue through them, but stop at a wall.

**Steps.**
1. BFS from the start with `dist`.
2. For each direction, walk cell by cell; record the unvisited cells with `dist + 1`; stop at walls or the edge.

```python
import os
from collections import deque


def minimumMoves(grid, startX, startY, goalX, goalY):
    n = len(grid)
    dist = [[-1] * n for _ in range(n)]
    dist[startX][startY] = 0
    q = deque([(startX, startY)])
    while q:
        x, y = q.popleft()
        if (x, y) == (goalX, goalY):
            return dist[x][y]
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            while 0 <= nx < n and 0 <= ny < n and grid[nx][ny] != 'X':
                if dist[nx][ny] == -1:
                    dist[nx][ny] = dist[x][y] + 1
                    q.append((nx, ny))
                nx += dx
                ny += dy
    return -1


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    grid = [input().strip() for _ in range(n)]
    sx, sy, gx, gy = map(int, input().split())
    fptr.write(str(minimumMoves(grid, sx, sy, gx, gy)) + '\n')
    fptr.close()
```

**Watch out.** Coordinates are `(row, column)`. Breaking the slide at the first visited cell would miss cells beyond it that this move can still reach.

```stdin
3
.X.
.X.
...
0 0 0 2
```

```stdout
3
```

### Down to Zero II

**Problem.** In one move, `N` becomes `N − 1` or `max(a, b)` for any factorisation `N = a·b` with `a, b > 1`. Find the fewest moves to reach 0.

**Idea.** Use a DP over all values up to 10⁶:
- `dp[n] = 1 + min(dp[n−1], min over divisors a ≤ √n of dp[n/a])`, where `n/a` is the larger factor.
- Fill it in **doubling blocks** `[2^k, 2^{k+1})`. Inside a block, every factor term points below the block, so a vectorised pass over the multiples of each `a` fills them.
- The `−1` chain inside the block is a running minimum, `dp[n] = min_m (f[m] + n − m)`, computed with `minimum.accumulate`.

**Steps.**
1. Base cases `dp[0..3]`.
2. For each block: start `f` from the factor terms, then resolve the `−1` chain; answer the queries by lookup.

```python
import sys

import numpy as np


def build(N):
    dp = np.zeros(max(N, 3) + 1, dtype=np.int64)
    dp[1], dp[2], dp[3] = 1, 2, 3
    lo = 4
    while lo <= N:
        hi = min(2 * lo, N + 1)
        f = np.full(hi - lo, 10 ** 9, dtype=np.int64)
        a = 2
        while a * a < hi:
            first = max(lo, a * a)
            first += (-first) % a                 # first multiple of a >= first
            if first < hi:
                ns = np.arange(first, hi, a)
                f[ns - lo] = np.minimum(f[ns - lo], dp[ns // a] + 1)
            a += 1
        idx = np.arange(lo, hi)
        cand = np.minimum(f - idx, dp[lo - 1] + 1 - lo)       # chain from below the block
        dp[lo:hi] = np.minimum.accumulate(cand) + idx
        lo = hi
    return dp


def main():
    data = list(map(int, sys.stdin.read().split()))
    q = data[0]
    ns = data[1:1 + q]
    dp = build(max(ns + [3]))
    print('\n'.join(str(int(dp[n])) for n in ns))


main()
```

**Watch out.** The answer for `N = 0` is 0. Only factor pairs with `a ≤ √n` are needed, because `max(a, b)` is the larger factor `n/a`. Blocks must double so that `n/a < lo` always holds.

```stdin
2
3
4
```

```stdout
3
3
```

### Truck Tour

**Problem.** Petrol pumps sit on a circle, each giving petrol and lying some distance from the next. Find the smallest starting index from which a truck with an empty tank completes the circle.

**Idea.** Greedy. Run a tank balance from a candidate start. If it goes negative at pump `i`, none of the pumps from the candidate up to `i` can be a start, because each would arrive at `i` with even less petrol. So restart from `i + 1`. One pass suffices, because a solution is guaranteed.

**Steps.**
1. `tank += petrol − distance`; on a negative tank, set `start = i + 1` and `tank = 0`.

```python
import os


def truckTour(petrolpumps):
    start = tank = 0
    for i, (petrol, dist) in enumerate(petrolpumps):
        tank += petrol - dist
        if tank < 0:
            start = i + 1
            tank = 0
    return start


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    pumps = [list(map(int, input().rstrip().split())) for _ in range(n)]
    fptr.write(str(truckTour(pumps)) + '\n')
    fptr.close()
```

**Watch out.** There is no need to wrap around and re-check the prefix. If the total petrol covers the total distance (which is guaranteed), the last surviving start works.

```stdin
3
1 5
10 3
3 4
```

```stdout
1
```

### Queries with Fixed Length

**Problem.** For each window length `d`, print the minimum over all windows of length `d` of the window maximum.

**Idea.** Build a **sparse table of range maxima** once (O(n log n) with NumPy). Then each query computes all window maxima at once, `max(sp[k][i], sp[k][i + d − 2^k])`, and takes their minimum. With up to 100 queries over 10⁵ elements, everything stays vectorised.

**Steps.**
1. `sp[0] = arr`; `sp[k] = max(sp[k−1][i], sp[k−1][i + 2^{k−1}])`.
2. Per query `d`: `k = ⌊log₂ d⌋`; the minimum of the elementwise maximum of the two overlapping blocks.

```python
import sys

import numpy as np


def main():
    data = sys.stdin.buffer.read().split()
    n, q = int(data[0]), int(data[1])
    arr = np.array(data[2:2 + n], dtype=np.int64)
    sp = [arr]
    k = 1
    while (1 << k) <= n:
        prev = sp[-1]
        half = 1 << (k - 1)
        sp.append(np.maximum(prev[:-half], prev[half:]))
        k += 1
    out = []
    for d in map(int, data[2 + n:2 + n + q]):
        k = d.bit_length() - 1
        t = sp[k]
        windows = np.maximum(t[:n - d + 1], t[d - (1 << k):d - (1 << k) + n - d + 1])
        out.append(int(windows.min()))
    print('\n'.join(map(str, out)))


main()
```

**Watch out.** The per-query monotonic deque is O(n) per query too, but a Python loop of 10⁷ steps is slow. The two-block sparse-table trick does the same work in C.

```stdin
5 5
33 11 44 11 55
1
2
3
4
5
```

```stdout
11
33
44
44
55
```
