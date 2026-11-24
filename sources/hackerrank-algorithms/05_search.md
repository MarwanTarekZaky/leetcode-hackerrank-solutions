## Search

### Hackerland Radio Transmitters

**Problem.** Houses sit at positions `x[i]`; a transmitter on a house covers `k` units on each side. Return the minimum number of transmitters needed to cover every house.

**Idea.** Greedy from the left: the leftmost uncovered house must be covered, and the best transmitter for it is the **furthest** house within `k` to its right. Then skip everything that transmitter covers.

**Steps.**
1. Sort positions.
2. From the first uncovered house `start`, move right while houses are within `start + k`; put the transmitter on the last such house `t`.
3. Skip all houses within `t + k`; count one transmitter; repeat.

```python
import os


def hackerlandRadioTransmitters(x, k):
    x = sorted(x)
    n, i, count = len(x), 0, 0
    while i < n:
        count += 1
        reach = x[i] + k
        while i < n and x[i] <= reach:
            i += 1
        cover = x[i - 1] + k
        while i < n and x[i] <= cover:
            i += 1
    return count


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    x = list(map(int, input().rstrip().split()))
    result = hackerlandRadioTransmitters(x, k)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** The transmitter must sit on a house, so place it on the last house within reach, not at `start + k`.

```stdin
8 2
7 2 4 6 5 9 12 11
```

```stdout
3
```

### Gridland Metro

**Problem.** An `n × m` grid (up to 10⁹ each) has `k ≤ 1000` horizontal tracks. Count the cells not covered by any track.

**Idea.** Only rows with tracks matter. Merge the overlapping intervals in each such row and subtract the covered length from `n · m`.

**Steps.**
1. Group tracks by row.
2. For each row, sort its intervals and merge overlaps, adding the merged lengths.
3. Return `n * m - covered`.

```python
import os
from collections import defaultdict


def gridlandMetro(n, m, k, track):
    rows = defaultdict(list)
    for r, c1, c2 in track:
        rows[r].append((c1, c2))
    covered = 0
    for intervals in rows.values():
        intervals.sort()
        start, end = intervals[0]
        for c1, c2 in intervals[1:]:
            if c1 > end:
                covered += end - start + 1
                start, end = c1, c2
            else:
                end = max(end, c2)
        covered += end - start + 1
    return n * m - covered


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m, k = map(int, input().split())
    track = [list(map(int, input().rstrip().split())) for _ in range(k)]
    result = gridlandMetro(n, m, k, track)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Tracks in the same row can overlap; adding their lengths separately double counts. The grid is up to 10¹⁸ cells, which Python handles natively.

```stdin
4 4 3
2 2 3
3 1 4
4 4 4
```

```stdout
9
```

### Ice Cream Parlor

**Problem.** Find the two flavours (1-based indices) whose prices add up to exactly `m`.

**Idea.** Two Sum: remember the index of each price seen so far; for each new price, check whether `m - price` was seen.

**Steps.**
1. For each index `i` and cost `c`: if `m - c` is in `seen`, return `[seen[m - c], i]`.
2. Otherwise store `seen[c] = i` (keep the first occurrence).

```python
import os


def icecreamParlor(m, arr):
    seen = {}
    for i, c in enumerate(arr, 1):
        if m - c in seen:
            return [seen[m - c], i]
        seen.setdefault(c, i)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        m = int(input().strip())
        n = int(input().strip())
        arr = list(map(int, input().rstrip().split()))
        fptr.write(' '.join(map(str, icecreamParlor(m, arr))) + '\n')
    fptr.close()
```

**Watch out.** Check before inserting, so a flavour isn't paired with itself (`m = 4`, price 2 appearing once).

```stdin
2
4
5
1 4 5 3 2
4
4
2 2 4 3
```

```stdout
1 4
1 2
```

### KnightL on a Chessboard

**Problem.** For every `1 <= a, b < n`, find the minimum number of `KnightL(a, b)` moves from `(0, 0)` to `(n-1, n-1)` on an `n × n` board, or `-1`.

**Idea.** BFS from the corner for each `(a, b)`. `(a, b)` and `(b, a)` move identically, so compute each unordered pair once.

**Steps.**
1. For each `a <= b`, BFS over the board with the 8 moves `(±a, ±b)` and `(±b, ±a)`.
2. Fill both `ans[a][b]` and `ans[b][a]`.

```python
import os
from collections import deque


def knightlOnAChessboard(n):
    def bfs(a, b):
        moves = {(da, db) for x, y in ((a, b), (b, a)) for da in (x, -x) for db in (y, -y)}
        dist = [[-1] * n for _ in range(n)]
        dist[0][0] = 0
        q = deque([(0, 0)])
        while q:
            r, c = q.popleft()
            if (r, c) == (n - 1, n - 1):
                return dist[r][c]
            for dr, dc in moves:
                nr, nc = r + dr, c + dc
                if 0 <= nr < n and 0 <= nc < n and dist[nr][nc] == -1:
                    dist[nr][nc] = dist[r][c] + 1
                    q.append((nr, nc))
        return -1

    ans = [[0] * (n - 1) for _ in range(n - 1)]
    for a in range(1, n):
        for b in range(a, n):
            ans[a - 1][b - 1] = ans[b - 1][a - 1] = bfs(a, b)
    return ans


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    result = knightlOnAChessboard(n)
    fptr.write('\n'.join([' '.join(map(str, x)) for x in result]))
    fptr.write('\n')
    fptr.close()
```

**Watch out.** When `a == b`, the 8 moves collapse to 4; using a set avoids duplicate work.

```stdin
5
```

```stdout
4 4 2 8
4 2 4 4
2 4 -1 -1
8 4 -1 1
```

### Minimum Loss

**Problem.** Buy the house in one year and sell it in a later year at a lower price. Minimize the loss.

**Idea.** Sort the prices. The smallest loss is always between two **neighbouring** prices in sorted order, valid only if the higher price comes earlier in time.

**Steps.**
1. Sort `(price, year)` pairs.
2. For each neighbouring pair `(low, high)` in sorted order, if `high` came first in time, `high - low` is a candidate.
3. Return the smallest candidate.

```python
import os


def minimumLoss(price):
    order = sorted(range(len(price)), key=price.__getitem__)
    best = float("inf")
    for lo, hi in zip(order, order[1:]):
        if hi < lo:
            best = min(best, price[hi] - price[lo])
    return best


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    price = list(map(int, input().rstrip().split()))
    result = minimumLoss(price)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Why only neighbours: if some price lies between `low` and `high`, one of the two closer pairs is also valid and has a smaller loss.

```stdin
5
20 7 8 2 5
```

```stdout
2
```

### Missing Numbers

**Problem.** `brr` is the original list; `arr` lost some elements. Return, sorted and without repeats, every number whose count in `arr` is smaller than in `brr`.

**Idea.** Subtract the counters: what remains is exactly the missing numbers.

**Steps.**
1. Return `sorted(Counter(brr) - Counter(arr))`.

```python
import os
from collections import Counter


def missingNumbers(arr, brr):
    return sorted(Counter(brr) - Counter(arr))


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    arr = list(map(int, input().rstrip().split()))
    m = int(input().strip())
    brr = list(map(int, input().rstrip().split()))
    result = missingNumbers(arr, brr)
    fptr.write(' '.join(map(str, result)))
    fptr.write('\n')
    fptr.close()
```

**Watch out.** A number that exists in both lists but less often in `arr` is still missing; set difference would miss it.

```stdin
10
203 204 205 206 207 208 203 204 205 206
13
203 204 204 205 206 207 205 208 203 206 205 206 204
```

```stdout
204 205 206
```

### Pairs

**Problem.** Count pairs of distinct values whose difference is exactly `k`.

**Idea.** Put the values in a set; count the values `x` for which `x + k` is also present.

**Steps.**
1. Return `sum(x + k in values for x in values)`.

```python
import os


def pairs(k, arr):
    values = set(arr)
    return sum(x + k in values for x in values)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    arr = list(map(int, input().rstrip().split()))
    result = pairs(k, arr)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Checking only `x + k` (not also `x - k`) counts each pair exactly once.

```stdin
5 2
1 5 3 4 2
```

```stdout
3
```

### Sherlock and Array

**Problem.** Is there an element whose left sum equals its right sum?

**Idea.** With the total known, the right sum at `i` is `total - left - a[i]`; one pass checks every position.

**Steps.**
1. `left = 0`; for each `x`: if `2 * left + x == total`, return `YES`; then `left += x`.

```python
import os


def balancedSums(arr):
    total, left = sum(arr), 0
    for x in arr:
        if 2 * left + x == total:
            return "YES"
        left += x
    return "NO"


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    T = int(input().strip())
    for _ in range(T):
        n = int(input().strip())
        arr = list(map(int, input().rstrip().split()))
        fptr.write(balancedSums(arr) + '\n')
    fptr.close()
```

**Watch out.** A single element is balanced (both sides are empty).

```stdin
2
3
1 2 3
4
1 2 3 3
```

```stdout
NO
YES
```

### Maximum Subarray Sum

**Problem.** Find the maximum value of `(subarray sum) mod m`.

**Idea.** With prefix sums `P` (mod `m`), a subarray `(j, i]` gives `(P[i] - P[j]) mod m`. That's `P[i]` itself, or larger than `P[i]` only when an **earlier** prefix `P[j]` is bigger than `P[i]`: then the value is `P[i] - P[j] + m`, best when `P[j]` is the smallest earlier prefix above `P[i]`. Sort prefixes by value; it's enough to check neighbours in sorted order whose larger value comes earlier in time.

**Steps.**
1. Compute prefix sums mod `m`; the best starts as `max(prefix)`.
2. Sort `(value, index)`; for neighbours with `v2 > v1` and `i2 < i1`, candidate `v1 - v2 + m`.

```python
import os


def maximumSum(a, m):
    prefix, s = [], 0
    for x in a:
        s = (s + x) % m
        prefix.append(s)
    best = max(prefix)
    order = sorted(range(len(prefix)), key=lambda i: (prefix[i], i))
    for i1, i2 in zip(order, order[1:]):
        if prefix[i2] > prefix[i1] and i2 < i1:
            best = max(best, prefix[i1] - prefix[i2] + m)
    return best


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        n, m = map(int, input().split())
        a = list(map(int, input().rstrip().split()))
        fptr.write(str(maximumSum(a, m)) + '\n')
    fptr.close()
```

**Watch out.** Equal prefix values give a difference of 0, not `m`; that's why the strict `v2 > v1` check (and sorting ties by index) matters.

```stdin
1
5 7
3 3 9 9 5
```

```stdout
6
```

### Connected Cells in a Grid

**Problem.** Find the size of the largest region of `1`s, where cells connect in all 8 directions.

**Idea.** Flood fill each unvisited `1` with DFS and track the largest region.

**Steps.**
1. For each `1` not yet visited, DFS with a stack, marking cells as visited (set them to 0) and counting.
2. Return the maximum count.

```python
import os


def connectedCell(matrix):
    n, m = len(matrix), len(matrix[0])
    best = 0
    for i in range(n):
        for j in range(m):
            if matrix[i][j]:
                matrix[i][j] = 0
                stack, size = [(i, j)], 0
                while stack:
                    r, c = stack.pop()
                    size += 1
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            x, y = r + dr, c + dc
                            if 0 <= x < n and 0 <= y < m and matrix[x][y]:
                                matrix[x][y] = 0
                                stack.append((x, y))
                best = max(best, size)
    return best


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    m = int(input().strip())
    matrix = [list(map(int, input().rstrip().split())) for _ in range(n)]
    result = connectedCell(matrix)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Diagonal neighbours count here, unlike most grid problems.

```stdin
4
4
1 1 0 0
0 1 1 0
0 0 1 0
1 0 0 0
```

```stdout
5
```

### Short Palindrome

**Problem.** Count index tuples `a < b < c < d` with `s[a] = s[d]` and `s[b] = s[c]`, modulo 10⁹+7 (`|s|` up to 10⁶).

**Idea.** Scan left to right with counts of partial patterns: `c1[x]` = occurrences of `x`, `c2[y][x]` = pairs `x…y`, `c3[y][x]` = triples `x…y…y`. When the current letter is `x`, every triple `x y y` completes a tuple. Storing `c2`/`c3` by the second letter `y` lets each step update one row.

**Steps.**
1. For each letter `ch`: `answer += total3[ch]` (all triples starting with `ch`).
2. Triples ending here: `c3[ch][x] += c2[ch][x]` for all `x`, and `total3[x] += c2[ch][x]`.
3. Pairs ending here: `c2[ch][x] += c1[x]`; then `c1[ch] += 1`.

```python
import os

MOD = 10 ** 9 + 7


def shortPalindrome(s):
    c1 = [0] * 26
    c2 = [[0] * 26 for _ in range(26)]
    total3 = [0] * 26
    answer = 0
    for ch in s:
        y = ord(ch) - 97
        answer += total3[y]
        row = c2[y]
        total3 = [(t + r) % MOD for t, r in zip(total3, row)]
        c2[y] = [(r + c) % MOD for r, c in zip(row, c1)]
        c1[y] += 1
    return answer % MOD


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    s = input()
    result = shortPalindrome(s)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Only the per-first-letter totals of triples are ever read, so `c3` itself doesn't need storing. It's still ~50 additions per character: choose PyPy 3 on HackerRank for 10⁶ letters.

```stdin
kkkkkkz
```

```stdout
15
```

### Maximizing Mission Points

**Problem.** Visit cities in strictly increasing height; consecutive cities must differ by at most `d_lat` in latitude and `d_long` in longitude. Maximize the sum of points (visiting none is allowed).

**Idea.** In height order, `dp[i] = points[i] + max(0, best dp[j])` over already-processed cities inside the box `|lat| <= d_lat`, `|long| <= d_long`. That's a 2D range-maximum query with insertions. Use a **range tree**: a segment tree over latitude where every node keeps its cities' longitudes sorted plus a small max-segment-tree over them.

**Steps.**
1. Rank cities by latitude (latitudes are distinct). Each segment-tree node stores the sorted longitudes of the cities in its latitude range, and a max-tree initialised to `-inf`.
2. Process cities by height: query the `O(log n)` nodes covering the latitude window; in each, binary-search the longitude window and take the max.
3. `dp = points + max(0, best)`; insert `dp` into every node on the leaf-to-root path.
4. Answer `max(0, max dp)`.

```python
import sys
from bisect import bisect_left, bisect_right
from heapq import merge


def main():
    data = sys.stdin.buffer.read().split()
    n, d_lat, d_long = int(data[0]), int(data[1]), int(data[2])
    cities = [tuple(map(int, data[3 + 4 * i: 7 + 4 * i])) for i in range(n)]
    by_lat = sorted(range(n), key=lambda i: cities[i][0])
    lats = [cities[i][0] for i in by_lat]
    rank = {city: r for r, city in enumerate(by_lat)}
    size = 1
    while size < n:
        size *= 2
    longs = [[] for _ in range(2 * size)]
    for r, i in enumerate(by_lat):
        longs[size + r] = [cities[i][1]]
    for v in range(size - 1, 0, -1):
        longs[v] = list(merge(longs[2 * v], longs[2 * v + 1]))
    NEG = float("-inf")
    trees = [[NEG] * (2 * len(l)) for l in longs]

    def node_max(v, lo, hi):
        t, m = trees[v], len(longs[v])
        lo += m
        hi += m
        best = NEG
        while lo < hi:
            if lo & 1:
                best = max(best, t[lo])
                lo += 1
            if hi & 1:
                hi -= 1
                best = max(best, t[hi])
            lo //= 2
            hi //= 2
        return best

    answer = 0
    for i in sorted(range(n), key=lambda i: cities[i][2]):
        lat, lng, _, pts = cities[i]
        lo = bisect_left(lats, lat - d_lat) + size
        hi = bisect_right(lats, lat + d_lat) + size
        best = NEG
        while lo < hi:
            for v in ((lo,) if lo & 1 else ()) + ((hi - 1,) if hi & 1 else ()):
                l = longs[v]
                best = max(best, node_max(v, bisect_left(l, lng - d_long), bisect_right(l, lng + d_long)))
            lo = (lo + 1) // 2
            hi //= 2
        dp = pts + max(0, best)
        answer = max(answer, dp)
        v = size + rank[i]
        while v:
            l, t = longs[v], trees[v]
            p = bisect_left(l, lng) + len(l)
            while p and t[p] < dp:
                t[p] = dp
                p //= 2
            v //= 2
    print(answer)


if __name__ == '__main__':
    main()
```

**Watch out.**
- The points can be negative, so a city may start a new mission (`max(0, best)`), and the empty mission makes the answer at least 0.
- This is O(n log² n) with heavy constants; choose PyPy 3 on HackerRank for `n = 2·10⁵`.

```stdin
3 1 1
1 1 1 3
2 2 2 -1
3 3 3 3
```

```stdout
5
```

### Count Luck

**Problem.** In a forest maze with exactly one path from `M` to `*`, Hermione waves her wand at every cell on the path where more than one direction could be taken. Print `Impressed` if the number of waves equals Ron's guess `k`, else `Oops!`.

**Idea.** Find the unique path with DFS (remembering parents), then walk it from `M`: at each cell except `*`, count the free neighbours other than the cell you came from; if there are two or more, that's a wave.

**Steps.**
1. DFS/BFS from `M` recording each cell's parent until `*` is reached.
2. Walk back from `*` to `M` to list the path.
3. For each path cell before `*`, count open neighbours (`.` or `*`) excluding its parent; count a wave when it's at least 2.

```python
import os


def countLuck(matrix, k):
    n, m = len(matrix), len(matrix[0])
    start = next((i, j) for i in range(n) for j in range(m) if matrix[i][j] == "M")

    def free(r, c):
        return 0 <= r < n and 0 <= c < m and matrix[r][c] != "X"

    parent = {start: None}
    stack = [start]
    while stack:
        r, c = stack.pop()
        if matrix[r][c] == "*":
            end = (r, c)
            break
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if free(nr, nc) and (nr, nc) not in parent:
                parent[(nr, nc)] = (r, c)
                stack.append((nr, nc))
    path, cell = [], parent[end]
    while cell is not None:
        path.append(cell)
        cell = parent[cell]
    waves = 0
    for r, c in path:
        options = sum(free(nr, nc) and (nr, nc) != parent[(r, c)]
                      for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)))
        waves += options >= 2
    return "Impressed" if waves == k else "Oops!"


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n, m = map(int, input().split())
        matrix = [input() for _ in range(n)]
        k = int(input().strip())
        fptr.write(countLuck(matrix, k) + '\n')
    fptr.close()
```

**Watch out.** At the start cell there is no "came from", so all open neighbours count. The destination cell itself never needs a wave.

```stdin
3
2 3
*.M
.X.
1
4 11
.X.X......X
.X*.X.XXX.X
.XX.X.XM...
......XXXX.
3
4 11
.X.X......X
.X*.X.XXX.X
.XX.X.XM...
......XXXX.
4
```

```stdout
Impressed
Impressed
Oops!
```

### Cut the Tree

**Problem.** Cut one edge of a weighted tree to split it into two parts with the smallest difference of sums.

**Idea.** Cutting the edge above node `v` leaves `subtree(v)` and `total - subtree(v)`. Compute every subtree sum with one DFS.

**Steps.**
1. Iterative DFS from node 1 to get a parent order.
2. Process nodes in reverse order, adding each subtree sum to its parent.
3. Return `min(|total - 2 · subtree(v)|)` over non-root nodes.

```python
import os


def cutTheTree(data, edges):
    n = len(data)
    adj = [[] for _ in range(n + 1)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    order, parent = [], [0] * (n + 1)
    parent[1] = -1
    stack = [1]
    while stack:
        u = stack.pop()
        order.append(u)
        for v in adj[u]:
            if v != parent[u]:
                parent[v] = u
                stack.append(v)
    sub = [0] + data[:]
    for u in reversed(order[1:]):
        sub[parent[u]] += sub[u]
    total = sub[1]
    return min(abs(total - 2 * sub[u]) for u in order[1:])


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    data = list(map(int, input().rstrip().split()))
    edges = [list(map(int, input().rstrip().split())) for _ in range(n - 1)]
    result = cutTheTree(data, edges)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Recursive DFS overflows Python's stack on a path-shaped tree of 10⁵ nodes; use an explicit stack.

```stdin
6
100 200 100 500 100 600
1 2
2 3
2 5
4 5
5 6
```

```stdout
400
```

### Making Candies

**Problem.** Each pass makes `machines × workers` candies; after a pass you may buy machines or workers for `p` candies each. Find the minimum number of passes to have `n` candies.

**Idea.** At every point there are two choices: stop investing and just wait, or spend everything on new machines/workers, keeping them as balanced as possible (the product is largest when they're equal). Simulate investing, and at each step record "if I stop now, how many passes in total". When you can't afford anything yet, jump ahead by several passes at once.

**Steps.**
1. If you can't afford a purchase, skip ahead `(p - candy) // (m·w)` passes.
2. Otherwise buy `candy // p` units, split to balance `m` and `w`, keep the remainder.
3. After each step, `best = min(best, passes + ceil((n - candy) / (m·w)))`.
4. Stop when `candy >= n`; return the smaller of the passes and `best`.

```python
import os
from math import ceil


def minimumPasses(m, w, p, n):
    candy = passes = 0
    best = float("inf")
    while candy < n:
        step = (p - candy) // (m * w)
        if step <= 0:
            total = candy // p + m + w
            half = ceil(total / 2)
            if m > w:
                m = max(m, half)
                w = total - m
            else:
                w = max(w, half)
                m = total - w
            candy %= p
            step = 1
        candy += step * m * w
        passes += step
        best = min(best, passes + ceil((n - candy) / (m * w)))
    return min(passes, best)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    m, w, p, n = map(int, input().split())
    result = minimumPasses(m, w, p, n)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Values reach 10¹²: never simulate pass by pass while saving up, and keep the arithmetic in integers (`m * w` can be about 10²⁴).

```stdin
3 1 2 12
```

```stdout
3
```

### Gena Playing Hanoi

**Problem.** Tower of Hanoi with 4 rods and up to 10 disks in some legal position. Find the minimum moves to put all disks back on rod 1.

**Idea.** BFS over positions (each disk's rod). There are up to 4¹⁰ ≈ 10⁶ positions, so search from **both** ends at once (bidirectional BFS): the two frontiers meet after exploring only a small fraction.

**Steps.**
1. Encode a position as a tuple of rods (disk `i` on rod `pos[i]`).
2. Moves: the top disk of a rod is its smallest disk; move it to any rod whose top is larger (or empty).
3. Expand the smaller frontier each round until a position is seen from both sides; return the sum of the distances.

```python
import os


def hanoi(posts):
    start = tuple(p - 1 for p in posts)
    goal = (0,) * len(posts)
    if start == goal:
        return 0

    def neighbours(state):
        tops = {}
        for disk, rod in enumerate(state):
            tops.setdefault(rod, disk)
        for rod, disk in tops.items():
            for target in range(4):
                if target != rod and (target not in tops or tops[target] > disk):
                    yield state[:disk] + (target,) + state[disk + 1:]

    dist = [{start: 0}, {goal: 0}]
    frontier = [[start], [goal]]
    while True:
        side = 0 if len(frontier[0]) <= len(frontier[1]) else 1
        mine, other = dist[side], dist[1 - side]
        nxt = []
        for state in frontier[side]:
            d = mine[state] + 1
            for nb in neighbours(state):
                if nb in other:
                    return d + other[nb]
                if nb not in mine:
                    mine[nb] = d
                    nxt.append(nb)
        frontier[side] = nxt


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    loc = list(map(int, input().rstrip().split()))
    res = hanoi(loc)
    fptr.write(str(res) + '\n')
    fptr.close()
```

**Watch out.** Moves are reversible, so BFS from the goal uses the same move generator. Checking for the meeting point while expanding (not after) keeps the result a shortest path.

```stdin
3
1 4 1
```

```stdout
3
```

### Beautiful Quadruples

**Problem.** Count multisets `{W, X, Y, Z}` with `1 <= W <= A`, `X <= B`, `Y <= C`, `Z <= D` and `W ⊕ X ⊕ Y ⊕ Z != 0`.

**Idea.** Sort the bounds so that `A <= B <= C <= D` and count sorted quadruples `W <= X <= Y <= Z` (each multiset exactly once). Fix `Y`; all pairs `(W, X)` with `W <= X <= Y` are kept in a count array indexed by `W ⊕ X`. For each `Z >= Y`, the beautiful ones are all pairs except those with `W ⊕ X = Y ⊕ Z`.

**Steps.**
1. Sort `A, B, C, D`.
2. For `Y = 1..C`: if `Y <= B`, add the pairs `(W, Y)` for `W <= min(A, Y)` into `cnt[W ^ Y]`.
3. Add `pairs × (D - Y + 1) − Σ_{Z=Y..D} cnt[Y ^ Z]` to the total.

```python
import os


def beautifulQuadruples(a, b, c, d):
    a, b, c, d = sorted((a, b, c, d))
    cnt = [0] * 4096
    pairs = total = 0
    for y in range(1, c + 1):
        if y <= b:
            for w in range(1, min(a, y) + 1):
                cnt[w ^ y] += 1
                pairs += 1
        total += pairs * (d - y + 1) - sum([cnt[y ^ z] for z in range(y, d + 1)])
    return total


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    a, b, c, d = map(int, input().split())
    result = beautifulQuadruples(a, b, c, d)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Counting "all minus XOR-zero" is easier than counting nonzero XORs directly. The inner sum is up to 9·10⁶ lookups in total, so PyPy 3 is the safer choice on HackerRank.

```stdin
1 2 3 4
```

```stdout
11
```

### Red Knight's Shortest Path

**Problem.** The red knight moves `UL, UR, R, LR, LL, L` (`(-2,-1), (-2,1), (0,2), (2,1), (2,-1), (0,-2)`). Print the shortest number of moves and the path, preferring moves earlier in that list when several shortest paths exist; or `Impossible`.

**Idea.** BFS **from the destination** gives every cell's distance to it. Then walk from the start: at each step pick the first move (in priority order) that lands on a cell one step closer.

**Steps.**
1. BFS from the end (the move set is symmetric, so reverse moves are the same set).
2. If the start is unreachable, print `Impossible`.
3. From the start, repeatedly take the first priority move whose cell has distance one less.

```python
from collections import deque

MOVES = [("UL", -2, -1), ("UR", -2, 1), ("R", 0, 2), ("LR", 2, 1), ("LL", 2, -1), ("L", 0, -2)]


def printShortestPath(n, i_start, j_start, i_end, j_end):
    dist = [[-1] * n for _ in range(n)]
    dist[i_end][j_end] = 0
    q = deque([(i_end, j_end)])
    while q:
        r, c = q.popleft()
        for _, dr, dc in MOVES:
            x, y = r + dr, c + dc
            if 0 <= x < n and 0 <= y < n and dist[x][y] == -1:
                dist[x][y] = dist[r][c] + 1
                q.append((x, y))
    if dist[i_start][j_start] == -1:
        print("Impossible")
        return
    r, c, path = i_start, j_start, []
    while (r, c) != (i_end, j_end):
        for name, dr, dc in MOVES:
            x, y = r + dr, c + dc
            if 0 <= x < n and 0 <= y < n and dist[x][y] == dist[r][c] - 1:
                path.append(name)
                r, c = x, y
                break
    print(len(path))
    print(" ".join(path))


if __name__ == '__main__':
    n = int(input().strip())
    i_start, j_start, i_end, j_end = map(int, input().split())
    printShortestPath(n, i_start, j_start, i_end, j_end)
```

**Watch out.** BFS from the start with a fixed neighbour order does **not** guarantee the priority rule for the whole path; distances to the target do.

```stdin
7
6 6 0 1
```

```stdout
4
UL UL UL L
```

### Bike Racers

**Problem.** `N` bikers and `M` bikes; `K` bikers must each get a different bike. Minimize the time until `K` bikes are taken, and print its square.

**Idea.** Binary search on the answer (a squared distance from the candidate list). For a threshold `T`, keep only the biker–bike edges with squared distance `<= T` and check whether a matching of size `K` exists (bipartite matching).

**Steps.**
1. Compute all squared distances; sort the distinct values.
2. Binary search the smallest value whose graph has a matching of at least `K` (Kuhn's augmenting paths, stopping once `K` are found).

```python
import sys


def bikeRacers(bikers, bikes, k):
    d = [[(x1 - x2) ** 2 + (y1 - y2) ** 2 for x2, y2 in bikes] for x1, y1 in bikers]
    values = sorted({v for row in d for v in row})

    def matching(limit):
        adj = [[j for j, v in enumerate(row) if v <= limit] for row in d]
        owner = [-1] * len(bikes)

        def augment(u, seen):
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    if owner[v] == -1 or augment(owner[v], seen):
                        owner[v] = u
                        return True
            return False

        found = 0
        for u in range(len(bikers)):
            if augment(u, [False] * len(bikes)):
                found += 1
                if found == k:
                    return True
        return False

    lo, hi = 0, len(values) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if matching(values[mid]):
            hi = mid
        else:
            lo = mid + 1
    return values[lo]


if __name__ == '__main__':
    sys.setrecursionlimit(10000)
    data = sys.stdin.read().split()
    n, m, k = int(data[0]), int(data[1]), int(data[2])
    nums = list(map(int, data[3:]))
    bikers = [nums[2 * i: 2 * i + 2] for i in range(n)]
    bikes = [nums[2 * (n + j): 2 * (n + j) + 2] for j in range(m)]
    print(bikeRacers(bikers, bikes, k))
```

**Watch out.** HackerRank's Python starter reads `N` lines of bikes instead of `M`; reading all numbers at once avoids that bug. Comparing squared distances keeps everything in exact integers.

```stdin
3 3 2
0 1
0 2
0 3
100 1
200 2
300 3
```

```stdout
40000
```

### Task Scheduling

**Problem.** Tasks have deadlines `D` and durations `M`, and can be split. After each new task, print the minimum possible maximum lateness of the tasks seen so far.

**Idea.** Earliest-deadline-first is optimal, and its maximum lateness equals `max over d of (total work with deadline <= d) − d`, never below 0. Adding a task `(D, M)` adds `M` to that expression for every `d >= D`: a range add, then a global maximum. A segment tree with range-add and max does both in O(log D).

**Steps.**
1. Leaf `d` starts at value `-d` (for `d = 1..10⁵`).
2. For each task: add `M` on `[D, max]`, then output `max(0, root)`.

```python
import sys


def main():
    data = sys.stdin.buffer.read().split()
    t = int(data[0])
    LIMIT = 100000
    size = 1
    while size < LIMIT + 1:
        size *= 2
    NEG = float("-inf")
    tree = [NEG] * (2 * size)
    lazy = [0] * (2 * size)
    for d in range(1, LIMIT + 1):
        tree[size + d] = -d
    for v in range(size - 1, 0, -1):
        tree[v] = max(tree[2 * v], tree[2 * v + 1])

    def pull(v):
        while v > 1:
            v //= 2
            tree[v] = max(tree[2 * v], tree[2 * v + 1]) + lazy[v]

    out = []
    for i in range(t):
        d, m = int(data[1 + 2 * i]), int(data[2 + 2 * i])
        lo, hi = d + size, LIMIT + 1 + size
        l0, r0 = lo, hi - 1
        while lo < hi:
            if lo & 1:
                tree[lo] += m
                lazy[lo] += m
                lo += 1
            if hi & 1:
                hi -= 1
                tree[hi] += m
                lazy[hi] += m
            lo //= 2
            hi //= 2
        pull(l0)
        pull(r0)
        out.append(max(0, tree[1]))
    print("\n".join(map(str, out)))


if __name__ == '__main__':
    main()
```

**Watch out.** With only a global query, lazy values never need to be pushed down: each node's value already includes its own pending addition, so recomputing the parents along the two border paths is enough.

```stdin
5
2 2
1 1
4 3
10 1
2 1
```

```stdout
0
1
2
2
3
```

### Similar Pair

**Problem.** Count pairs `(a, b)` where `a` is an ancestor of `b` and `|a - b| <= k`.

**Idea.** During a DFS, the nodes on the current root path are exactly the ancestors. Keep them in a Fenwick tree indexed by label; at each node, count ancestors with labels in `[v - k, v + k]`. Insert when entering, remove when leaving.

**Steps.**
1. Find the root (the node that is never a child).
2. Iterative DFS: on entry, add the count of labels in range, then insert `v`; on exit, remove `v`.

```python
import os


def similarPair(n, k, edges):
    children = [[] for _ in range(n + 1)]
    is_child = [False] * (n + 1)
    for p, c in edges:
        children[p].append(c)
        is_child[c] = True
    root = next(v for v in range(1, n + 1) if not is_child[v])
    tree = [0] * (n + 1)

    def add(i, delta):
        while i <= n:
            tree[i] += delta
            i += i & -i

    def prefix(i):
        s = 0
        while i > 0:
            s += tree[i]
            i -= i & -i
        return s

    total = 0
    stack = [(root, False)]
    while stack:
        v, leaving = stack.pop()
        if leaving:
            add(v, -1)
            continue
        total += prefix(min(n, v + k)) - prefix(max(0, v - k - 1))
        add(v, 1)
        stack.append((v, True))
        stack.extend((c, False) for c in children[v])
    return total


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    edges = [list(map(int, input().rstrip().split())) for _ in range(n - 1)]
    result = similarPair(n, k, edges)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Query before inserting `v` itself, otherwise each node pairs with itself.

```stdin
5 2
3 2
3 1
1 4
1 5
```

```stdout
4
```

### Absolute Element Sums

**Problem.** Each query adds `x` to every element (permanently) and asks for the sum of absolute values. Up to 5·10⁵ elements and queries.

**Idea.** Keep the array sorted and track only the total shift `s`. Elements with `a + s < 0` contribute `-(a + s)`, the rest `a + s`. With prefix sums of the sorted array and one binary search for the split point, each query is O(log n).

**Steps.**
1. Sort, build prefix sums.
2. For each query: `s += x`; `i = bisect_left(arr, -s)` (elements below `-s` are negative after shifting).
3. Answer = `-(prefix[i] + s·i) + (total - prefix[i]) + s·(n - i)`.

```python
import sys
from bisect import bisect_left
from itertools import accumulate


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    arr = sorted(map(int, data[1:1 + n]))
    q = int(data[1 + n])
    prefix = [0] + list(accumulate(arr))
    total = prefix[-1]
    s, out = 0, []
    for x in data[2 + n:2 + n + q]:
        s += int(x)
        i = bisect_left(arr, -s)
        out.append(-(prefix[i] + s * i) + (total - prefix[i]) + s * (n - i))
    sys.stdout.write("\n".join(map(str, out)) + "\n")


if __name__ == '__main__':
    main()
```

**Watch out.** The input and output are huge: read everything with `sys.stdin.buffer` and write one joined string.

```stdin
3
-1 2 -3
3
1 -2 3
```

```stdout
5
7
6
```

### Sorted Subsegments

**Problem.** Apply `q` "sort the segment `[l, r]`" operations to an array, then print the element at index `k`.

**Idea.** Binary search on the answer value `x`. Replace the array with bits `a[i] >= x`; sorting a segment of bits just moves all its 0s to the front. Then the final value at `k` is `>= x` exactly when the final bit at `k` is 1. Store the bit array as a list of runs, so each sort costs a few run operations instead of the segment length.

**Steps.**
1. Candidate values = sorted distinct elements; binary search the largest `x` with final bit 1 at `k`.
2. For one `x`: build runs (`starts`, `bits`); for each query split runs at `l` and `r + 1`, count the ones inside, and replace the runs inside by one run of 0s and one run of 1s.
3. Read the bit of the run containing `k`.

```python
import os
from bisect import bisect_right


def sortedSubsegments(k, a, queries):
    n = len(a)

    def final_bit(x):
        bits = [1 if v >= x else 0 for v in a]
        starts = [i for i in range(n) if i == 0 or bits[i] != bits[i - 1]]
        vals = [bits[i] for i in starts]

        def split(pos):
            i = bisect_right(starts, pos) - 1
            if starts[i] != pos:
                starts.insert(i + 1, pos)
                vals.insert(i + 1, vals[i])
                return i + 1
            return i

        for l, r in queries:
            i = split(l)
            j = split(r + 1) if r + 1 < n else len(starts)
            ones = 0
            for t in range(i, j):
                if vals[t]:
                    end = starts[t + 1] if t + 1 < j else r + 1
                    ones += end - starts[t]
            zeros = r - l + 1 - ones
            new_starts, new_vals = [], []
            if zeros:
                new_starts.append(l)
                new_vals.append(0)
            if ones:
                new_starts.append(l + zeros)
                new_vals.append(1)
            starts[i:j] = new_starts
            vals[i:j] = new_vals
        return vals[bisect_right(starts, k) - 1]

    values = sorted(set(a))
    lo, hi = 0, len(values) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if final_bit(values[mid]):
            lo = mid
        else:
            hi = mid - 1
    return values[lo]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, q, k = map(int, input().split())
    a = list(map(int, input().rstrip().split()))
    queries = [list(map(int, input().rstrip().split())) for _ in range(q)]
    result = sortedSubsegments(k, a, queries)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Each sort leaves at most two runs inside its range and creates at most two splits, so the number of runs stays small and every check runs in roughly O((n + q) log n).

```stdin
3 1 1
3 2 1
0 1
```

```stdout
3
```

### Distant Pairs

**Problem.** `n` pairs of points on a circle of circumference `c`. The distance between two pairs is the minimum of the six circular distances among their four points. Maximize it over all pairs of pairs.

**Idea.** For four points on a circle, the minimum of the six distances is simply the smallest of the four gaps between consecutive points. Binary search on the answer `D`: only pairs whose own distance is at least `D` can be used ("active"). Write each pair as `x < y`. Another active pair `(x', y')` works with `(x, y)` exactly when it fits in one of these regions, each a rectangle in `(x', y')`:
- nested inside: `x' >= x + D`, `y' <= y - D`;
- entirely after (gaps through the wrap): `x' >= y + D`, `y' <= x + c - D`;
- interleaved: `x + D <= x' <= y - D` and `y + D <= y' <= x + c - D`.

The other three cases are the same ones seen from the other pair.

**Steps.**
1. Binary search `D` in `[0, c/2]`.
2. Nested/after checks: active pairs sorted by `x'` with suffix minima of `y'` answer "exists `x' >= X` with `y' <= Y`".
3. Interleaved check: offline, sweep `x + D` downward, insert active pairs with `x' >= x + D` into a min-segment-tree over `y'` storing `x'`, and test whether the minimum `x'` with `y'` in range is `<= y - D`.

```python
import sys
from bisect import bisect_left, bisect_right


def main():
    data = sys.stdin.buffer.read().split()
    n, c = int(data[0]), int(data[1])
    pairs = []
    for i in range(n):
        a, b = int(data[2 + 2 * i]), int(data[3 + 2 * i])
        x, y = min(a, b), max(a, b)
        pairs.append((x, y, min(y - x, c - (y - x))))

    def ok(D):
        act = sorted((x, y) for x, y, d in pairs if d >= D)
        if len(act) < 2:
            return False
        xs = [p[0] for p in act]
        suf = [0] * (len(act) + 1)
        suf[-1] = float("inf")
        for i in range(len(act) - 1, -1, -1):
            suf[i] = min(suf[i + 1], act[i][1])

        def exists(xmin, ymax):
            return suf[bisect_left(xs, xmin)] <= ymax

        for x, y in act:
            if exists(x + D, y - D) or exists(y + D, x + c - D):
                return True
        ys = sorted({p[1] for p in act})
        size = 1
        while size < len(ys):
            size *= 2
        tree = [float("inf")] * (2 * size)
        j = len(act) - 1
        for x, y in sorted(act, key=lambda p: -(p[0] + D)):
            while j >= 0 and act[j][0] >= x + D:
                pos = bisect_left(ys, act[j][1]) + size
                while pos and tree[pos] > act[j][0]:
                    tree[pos] = act[j][0]
                    pos //= 2
                j -= 1
            lo, hi = bisect_left(ys, y + D) + size, bisect_right(ys, x + c - D) + size
            best = float("inf")
            while lo < hi:
                if lo & 1:
                    best = min(best, tree[lo])
                    lo += 1
                if hi & 1:
                    hi -= 1
                    best = min(best, tree[hi])
                lo //= 2
                hi //= 2
            if best <= y - D:
                return True
        return False

    lo, hi = 0, c // 2
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if ok(mid):
            lo = mid
        else:
            hi = mid - 1
    print(lo)


if __name__ == '__main__':
    main()
```

**Watch out.**
- A pair whose two points coincide has distance 0, so it can only matter when the answer is 0.
- Each check is O(n log n) and there are ~20 of them, so choose PyPy 3 on HackerRank for `n = 10⁵`.

```stdin
5 8
0 4
2 6
1 5
3 7
4 4
```

```stdout
2
```

### King Richard's Knights

**Problem.** `N × N` knights receive `S` nested commands, each rotating a square clockwise by 90°. For several knights (by original label), print their final row and column. `N` up to 3·10⁷.

**Idea.** A clockwise rotation of the square `(a, b, d)` is `(r, c) → (c + (a - b), -r + (a + b + d))`: a 90° rotation plus a translation. Compositions of such maps keep that form, so store the prefix composition after each command. Because the squares are nested, a knight is affected by commands `1..t` for the largest `t` such that its position after `t - 1` commands lies in square `t`, and that condition is monotone in `t`, so binary search finds it.

**Steps.**
1. Prefix maps `P_t = (k_t, T_t)`: `P_t(p) = rot^{k_t}(p) + T_t`, built by `rot(T) + translation_t`.
2. For knight `w`: start at `(w // N + 1, w % N + 1)`; binary search the largest `t` with `P_{t-1}(p)` inside square `t`.
3. Output `P_t(p)`.

```python
import sys


def rot(k, r, c):
    k %= 4
    if k == 0:
        return r, c
    if k == 1:
        return c, -r
    if k == 2:
        return -r, -c
    return -c, r


def main():
    data = sys.stdin.buffer.read().split()
    n, s = int(data[0]), int(data[1])
    cmds = [tuple(map(int, data[2 + 3 * i: 5 + 3 * i])) for i in range(s)]
    pos = 2 + 3 * s
    L = int(data[pos])
    knights = list(map(int, data[pos + 1: pos + 1 + L]))
    maps = [(0, 0, 0)]
    for a, b, d in cmds:
        k, tr, tc = maps[-1]
        r, c = rot(1, tr, tc)
        maps.append((k + 1, r + (a - b), c + (a + b + d)))

    def apply(t, r, c):
        k, tr, tc = maps[t]
        r, c = rot(k, r, c)
        return r + tr, c + tc

    out = []
    for w in knights:
        r0, c0 = w // n + 1, w % n + 1
        lo, hi = 0, s
        while lo < hi:
            mid = (lo + hi + 1) // 2
            a, b, d = cmds[mid - 1]
            r, c = apply(mid - 1, r0, c0)
            if a <= r <= a + d and b <= c <= b + d:
                lo = mid
            else:
                hi = mid - 1
        out.append("%d %d" % apply(lo, r0, c0))
    print("\n".join(out))


if __name__ == '__main__':
    main()
```

**Watch out.** Never simulate the board: `N` is up to 3·10⁷. The whole answer is O(S + L log S).

```stdin
7
4
1 2 4
2 3 3
3 4 1
3 4 0
7
0
6
9
11
24
25
48
```

```stdout
1 1
1 7
4 6
3 4
2 5
2 4
7 7
```

### Almost Integer Rock Garden

**Problem.** One stone sits at integer point `(x, y)` in `[-12, 12]²`. Place 11 more stones at distinct integer points so that no stone is an integer distance from the origin, and the sum of all 12 distances is within `10⁻¹²` of an integer. Any valid placement is accepted.

**Idea.** A stone's distance depends only on `r² = x² + y²`, and there are only 68 non-square values of `r²` in the square. So the answer depends only on the first stone's `r²` class, and it can be **precomputed offline**:
- **Offline search.** For each class, find 11 radii whose square roots, added to `√r²`, land within `10⁻¹²` of an integer.
- **Meet in the middle.** Over sums of 5 and 6 square roots, sort the fractional parts of one half and binary-search the complement of each sum from the other half. Repeat over random subsets of the radii until all 68 classes have a solution, then confirm each hit with 50-digit `Decimal` arithmetic.
- **Online.** The program just looks up the table and turns each radius into any unused lattice point of that class.

**Steps.**
1. Group the lattice points by `r²`, keeping only non-square, non-zero values.
2. Look up the 11 radii for the first stone's `r²`.
3. For each radius, output the next unused point of that class, never reusing the first stone's point.

```python
from math import isqrt

TABLE = {
    2: (73,82,89,122,122,148,149,149,164,170,170), 5: (10,13,26,61,130,50,74,104,117,117,125), 8: (10,18,97,97,97,137,145,153,160,160,164),
    10: (40,50,97,97,145,40,97,137,153,160,164), 13: (5,10,26,74,104,50,61,117,117,125,130), 17: (10,68,97,137,145,50,97,97,160,160,164),
    18: (8,10,97,97,97,137,145,153,160,160,164), 20: (10,13,50,74,104,26,61,80,117,117,130), 26: (5,10,13,50,61,74,104,117,117,125,130),
    29: (8,97,97,101,104,104,113,128,180,180,221), 32: (29,72,97,97,101,104,104,113,180,180,221), 34: (37,89,97,106,113,130,136,136,181,200,242),
    37: (45,72,137,146,148,160,164,181,244,244,244), 40: (10,40,50,145,153,97,97,97,137,160,164), 41: (10,41,97,137,145,50,97,97,153,160,160),
    45: (10,13,26,50,130,45,61,74,104,117,117), 50: (10,10,90,145,153,97,97,97,137,160,164), 52: (10,50,74,117,130,26,45,45,52,61,104),
    53: (65,68,80,137,145,157,162,185,244,244,244), 58: (10,13,40,98,101,125,130,146,193,193,193), 61: (5,10,13,26,50,74,104,117,117,125,130),
    65: (10,41,65,109,109,113,113,136,164,208,265), 68: (10,17,50,97,145,97,97,137,160,160,164), 72: (29,32,97,97,101,104,104,113,180,180,221),
    73: (29,32,65,65,74,90,116,125,136,148,208), 74: (5,10,13,50,130,26,61,104,117,117,125), 80: (10,13,50,74,104,20,26,61,117,117,130),
    82: (5,72,85,90,97,101,145,164,202,265,265), 85: (5,72,82,90,97,101,145,164,202,265,265), 89: (2,73,82,122,122,148,149,149,164,170,170),
    90: (17,50,68,97,164,40,97,97,137,145,160), 97: (10,10,50,97,153,90,97,137,145,160,164), 98: (10,13,40,58,101,125,130,146,193,193,193),
    101: (8,29,97,97,104,104,113,128,180,180,221), 104: (5,10,13,50,130,26,61,74,117,117,125), 106: (34,37,89,97,113,130,136,136,181,200,242),
    109: (2,10,34,80,82,116,122,130,193,208,244), 113: (8,29,97,97,101,104,104,128,180,180,221), 116: (2,10,34,80,82,109,122,130,193,208,244),
    117: (5,10,13,26,61,50,74,104,117,125,130), 122: (2,73,82,89,122,148,149,149,164,170,170), 125: (5,10,13,26,61,50,74,104,117,117,130),
    128: (10,13,34,65,68,104,104,104,106,146,164), 130: (5,10,13,26,61,50,74,104,117,117,125), 136: (10,41,65,65,109,109,113,113,164,208,265),
    137: (10,10,50,97,153,90,97,97,145,160,164), 145: (10,10,50,90,153,97,97,97,137,160,164), 146: (10,13,40,58,98,101,125,130,193,193,193),
    148: (37,45,72,137,146,160,164,181,244,244,244), 149: (41,80,104,117,160,162,164,170,170,193,265), 153: (10,10,50,90,145,97,97,97,137,160,164),
    157: (53,65,68,80,137,145,162,185,244,244,244), 160: (10,17,50,68,145,97,97,97,137,160,164), 162: (34,37,89,97,106,113,130,136,136,181,288),
    164: (97,97,97,137,160,10,17,50,68,145,160), 170: (13,85,85,101,122,122,125,137,164,164,265), 180: (10,26,26,26,61,13,50,74,117,117,130),
    181: (34,37,89,97,106,113,130,136,136,162,288), 185: (53,65,68,80,137,145,157,162,244,244,244), 193: (10,13,40,58,98,101,125,130,146,193,193),
    200: (20,29,80,97,97,101,104,104,113,180,221), 202: (5,72,82,85,90,97,101,145,164,265,265), 208: (5,5,10,50,74,26,61,80,104,117,130),
    221: (58,74,106,130,146,61,89,89,89,117,149), 242: (34,37,89,97,106,113,130,136,136,181,200), 244: (13,26,40,85,113,74,82,130,137,149,157),
    265: (13,85,85,101,122,122,125,137,164,164,170), 288: (34,37,89,97,106,113,130,136,136,162,181),
}


def main():
    x0, y0 = map(int, input().split())
    points = {}
    for x in range(-12, 13):
        for y in range(-12, 13):
            r2 = x * x + y * y
            if r2 and isqrt(r2) ** 2 != r2 and (x, y) != (x0, y0):
                points.setdefault(r2, []).append((x, y))
    out = []
    for r2 in TABLE[x0 * x0 + y0 * y0]:
        x, y = points[r2].pop()
        out.append(f"{x} {y}")
    print('\n'.join(out))


main()
```

**Watch out.**
- **Precision.** Floats carry only about 16 significant digits, and a sum near 30 leaves about 3·10⁻¹⁵ of slack, so a float search produces false hits near the `10⁻¹²` boundary. Every table entry was therefore re-checked with `Decimal` at 50 digits, with a margin (`≤ 9·10⁻¹³`).
- **Repeated radii.** A radius may repeat, but only as many times as its class has lattice points (counting the first stone's point).
- **Why precompute.** Searching at run time is far too slow. Precomputing a small table is the intended approach for an "any valid answer" problem like this.

```stdin
7 11
```

```check
from decimal import Decimal, getcontext
getcontext().prec = 50
x0, y0 = map(int, stdin.split())
pts = [tuple(map(int, line.split())) for line in output.strip().split('\n')]
assert len(pts) == 11, pts
allp = [(x0, y0)] + pts
assert len(set(allp)) == 12, 'duplicate point'
total = Decimal(0)
for x, y in allp:
    assert -12 <= x <= 12 and -12 <= y <= 12
    r2 = x * x + y * y
    assert int(r2 ** 0.5 + 0.5) ** 2 != r2, (x, y)
    total += Decimal(r2).sqrt()
assert abs(total - total.to_integral_value()) <= Decimal('1e-12'), total
```
