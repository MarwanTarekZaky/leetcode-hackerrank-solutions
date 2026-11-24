## Implementation

### Cut the sticks

**Problem.** Repeatedly cut every stick by the length of the shortest one and throw away the pieces that become 0. Before each cut, record how many sticks are left.

**Idea.** Each round removes every stick of the current minimum length. Sorting makes this easy: after sorting, the counts before each cut are the sizes of the suffixes that start at each new distinct length.

**Steps.**
1. Sort the lengths.
2. Walk the sorted list; whenever the length changes (or at the start), record `n - i`, the number of sticks from index `i` onward.

```python
import os


def cutTheSticks(arr):
    arr = sorted(arr)
    n = len(arr)
    return [n - i for i in range(n) if i == 0 or arr[i] != arr[i - 1]]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    arr = list(map(int, input().rstrip().split()))
    result = cutTheSticks(arr)
    fptr.write('\n'.join(map(str, result)))
    fptr.write('\n')
    fptr.close()
```

**Watch out.** Simulating the cuts is O(n²) in the worst case; the sorted version is O(n log n).

```stdin
6
5 4 4 2 2 8
```

```stdout
6
4
2
1
```

### Non-Divisible Subset

**Problem.** Find the size of the largest subset where no two numbers sum to a multiple of `k`.

**Idea.** Only remainders mod `k` matter. Remainders `r` and `k - r` can't both appear, so for each such pair keep the larger group. Remainder `0` (and `k/2` when `k` is even) can contribute at most one number.

**Steps.**
1. Count numbers by remainder.
2. Start with `min(count[0], 1)`.
3. For `r` from 1 to `k // 2`: if `r == k - r`, add `min(count[r], 1)`; otherwise add `max(count[r], count[k - r])`.

```python
import os


def nonDivisibleSubset(k, s):
    count = [0] * k
    for x in s:
        count[x % k] += 1
    size = min(count[0], 1)
    for r in range(1, k // 2 + 1):
        if r == k - r:
            size += min(count[r], 1)
        else:
            size += max(count[r], count[k - r])
    return size


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    s = list(map(int, input().rstrip().split()))
    result = nonDivisibleSubset(k, s)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** The two "self-paired" remainders (0, and `k/2` for even `k`) are the usual mistake: two numbers with remainder 0 sum to a multiple of `k`.

```stdin
4 3
1 7 2 4
```

```stdout
3
```

### Repeated String

**Problem.** A string `s` repeats forever. Count the letter `a` in its first `n` characters.

**Idea.** The first `n` characters are `n // len(s)` full copies plus a prefix of length `n % len(s)`.

**Steps.**
1. Return `s.count('a') * (n // len(s)) + s[:n % len(s)].count('a')`.

```python
import os


def repeatedString(s, n):
    full, rest = divmod(n, len(s))
    return s.count("a") * full + s[:rest].count("a")


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    s = input()
    n = int(input().strip())
    result = repeatedString(s, n)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** `n` can be 10¹²: never build the repeated string.

```stdin
aba
10
```

```stdout
7
```

### Jumping on the Clouds

**Problem.** Jump 1 or 2 clouds at a time from the first to the last cloud, never landing on a thundercloud (`1`). Return the minimum number of jumps.

**Idea.** Greedy: jump 2 whenever that cloud is safe, otherwise jump 1. A 2-jump is never worse.

**Steps.**
1. `i = jumps = 0`.
2. While `i < n - 1`: jump to `i + 2` if it exists and is safe, else to `i + 1`; count the jump.

```python
import os


def jumpingOnClouds(c):
    i = jumps = 0
    while i < len(c) - 1:
        i += 2 if i + 2 < len(c) and c[i + 2] == 0 else 1
        jumps += 1
    return jumps


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    c = list(map(int, input().rstrip().split()))
    result = jumpingOnClouds(c)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** The game is always winnable, so two thunderclouds are never adjacent: the 1-jump fallback is always safe.

```stdin
7
0 0 1 0 0 1 0
```

```stdout
4
```

### Equalize the Array

**Problem.** Delete the fewest elements so that all remaining elements are equal.

**Idea.** Keep the most frequent value and delete everything else.

**Steps.**
1. Return `len(arr) - max(Counter(arr).values())`.

```python
import os
from collections import Counter


def equalizeArray(arr):
    return len(arr) - max(Counter(arr).values())


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    arr = list(map(int, input().rstrip().split()))
    result = equalizeArray(arr)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** It's a counting problem, not a sorting one: O(n).

```stdin
5
3 3 2 1 3
```

```stdout
2
```

### Queen's Attack II

**Problem.** A queen on an `n × n` board with obstacles. Count the squares she can attack.

**Idea.** In each of the 8 directions she can reach the board edge unless an obstacle on that line is closer. Start with the distance to the edge, then shrink it for every obstacle that lies on one of her lines.

**Steps.**
1. For each direction `(dr, dc)`, compute the number of free squares to the edge.
2. For each obstacle on the same row, column or diagonal, find its direction and distance; the reach in that direction becomes at most `distance - 1`.
3. Return the sum of the 8 reaches.

```python
import os


def queensAttack(n, k, r_q, c_q, obstacles):
    def to_edge(dr, dc):
        steps = []
        if dr:
            steps.append(n - r_q if dr > 0 else r_q - 1)
        if dc:
            steps.append(n - c_q if dc > 0 else c_q - 1)
        return min(steps)

    sign = lambda x: (x > 0) - (x < 0)
    dirs = [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if dr or dc]
    reach = {d: to_edge(*d) for d in dirs}
    for r, c in obstacles:
        dr, dc = r - r_q, c - c_q
        if dr == 0 or dc == 0 or abs(dr) == abs(dc):
            d = (sign(dr), sign(dc))
            reach[d] = min(reach[d], max(abs(dr), abs(dc)) - 1)
    return sum(reach.values())


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    r_q, c_q = map(int, input().split())
    obstacles = [list(map(int, input().rstrip().split())) for _ in range(k)]
    result = queensAttack(n, k, r_q, c_q, obstacles)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** `n` can be 10⁵: don't walk square by square or build the board. This is O(k).

```stdin
4 0
4 4
```

```stdout
9
```

### ACM ICPC Team

**Problem.** Each person knows some topics (a binary string). For every pair, the team knows the union. Return the maximum topics a team can know and how many teams achieve it.

**Idea.** Turn each string into an integer; the union is a bitwise OR, and the number of topics is the count of 1 bits.

**Steps.**
1. Convert each string with `int(s, 2)`.
2. For every pair, `known = bin(a | b).count("1")`; track the maximum and how often it occurs.

```python
import os
from itertools import combinations


def acmTeam(topic):
    nums = [int(t, 2) for t in topic]
    best = count = 0
    for a, b in combinations(nums, 2):
        known = bin(a | b).count("1")
        if known > best:
            best, count = known, 1
        elif known == best:
            count += 1
    return [best, count]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m = map(int, input().split())
    topic = [input() for _ in range(n)]
    result = acmTeam(topic)
    fptr.write('\n'.join(map(str, result)))
    fptr.write('\n')
    fptr.close()
```

**Watch out.** Comparing the strings character by character for ~125,000 pairs × 500 topics is too slow in Python. Big-integer OR does it in one operation.

```stdin
4 5
10101
11100
11010
00101
```

```stdout
5
2
```

### Taum and B'day

**Problem.** Buy `b` black and `w` white gifts. Black costs `bc`, white costs `wc`, and converting one colour to the other costs `z`. Minimize the total.

**Idea.** Each black gift costs `min(bc, wc + z)` (buy it directly, or buy white and convert). Same for white.

**Steps.**
1. Return `b * min(bc, wc + z) + w * min(wc, bc + z)`.

```python
import os


def taumBday(b, w, bc, wc, z):
    return b * min(bc, wc + z) + w * min(wc, bc + z)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        b, w = map(int, input().split())
        bc, wc, z = map(int, input().split())
        fptr.write(str(taumBday(b, w, bc, wc, z)) + '\n')
    fptr.close()
```

**Watch out.** Values up to 10⁹ multiply to 10¹⁸: fine in Python, needs 64-bit integers elsewhere.

```stdin
5
10 10
1 1 1
5 9
2 3 4
3 6
9 1 1
7 7
4 2 1
3 3
1 9 2
```

```stdout
20
37
12
35
12
```

### Organizing Containers of Balls

**Problem.** `containers[i][j]` is the number of balls of type `j` in container `i`. Using swaps of two balls between containers, can every container end up holding a single type?

**Idea.** A swap never changes how many balls a container holds, and never changes how many balls of a type exist. So it's possible exactly when the multiset of container sizes equals the multiset of type counts.

**Steps.**
1. Container sizes = row sums; type totals = column sums.
2. Return `Possible` if the sorted lists are equal, else `Impossible`.

```python
import os


def organizingContainers(container):
    sizes = sorted(map(sum, container))
    types = sorted(map(sum, zip(*container)))
    return "Possible" if sizes == types else "Impossible"


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        n = int(input().strip())
        container = [list(map(int, input().rstrip().split())) for _ in range(n)]
        fptr.write(organizingContainers(container) + '\n')
    fptr.close()
```

**Watch out.** Finding the invariant (what never changes) is the whole trick; no simulation is needed.

```stdin
2
2
1 1
1 1
2
0 2
1 1
```

```stdout
Possible
Impossible
```

### Encryption

**Problem.** Remove spaces, write the text row by row into a grid with `floor(√L) <= rows <= columns <= ceil(√L)` and `rows × columns >= L` (smallest area), then read it column by column, separating columns with spaces.

**Idea.** `columns = ceil(√L)`. Reading column `c` means taking every `columns`-th character starting at `c`, which is the slice `text[c::columns]`.

**Steps.**
1. `text = s.replace(" ", "")`, `cols = ceil(√len(text))`.
2. Return `" ".join(text[c::cols] for c in range(cols))`.

```python
import math
import os


def encryption(s):
    text = s.replace(" ", "")
    cols = math.ceil(math.sqrt(len(text)))
    return " ".join(text[c::cols] for c in range(cols))


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    s = input()
    result = encryption(s)
    fptr.write(result + '\n')
    fptr.close()
```

**Watch out.** You never need the row count: the column slices handle the shorter last row automatically.

```stdin
haveaniceday
```

```stdout
hae and via ecy
```

### Bigger is Greater

**Problem.** Return the smallest rearrangement of the word that is strictly greater than it, or `no answer`.

**Idea.** This is the classic **next permutation**: find the rightmost position that can be increased, swap it with the smallest larger letter to its right, then sort (reverse) the suffix.

**Steps.**
1. From the right, find the first `i` with `w[i] < w[i + 1]`. If none, return `no answer`.
2. From the right, find the first `j > i` with `w[j] > w[i]`; swap them.
3. Reverse `w[i + 1:]` (it was descending, so this makes it the smallest).

```python
import os


def biggerIsGreater(w):
    w = list(w)
    i = len(w) - 2
    while i >= 0 and w[i] >= w[i + 1]:
        i -= 1
    if i < 0:
        return "no answer"
    j = len(w) - 1
    while w[j] <= w[i]:
        j -= 1
    w[i], w[j] = w[j], w[i]
    w[i + 1:] = reversed(w[i + 1:])
    return "".join(w)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    T = int(input().strip())
    for _ in range(T):
        fptr.write(biggerIsGreater(input()) + '\n')
    fptr.close()
```

**Watch out.** Use `>=` / `<=` in the scans so repeated letters (`bb`) correctly give `no answer`.

```stdin
5
ab
bb
hefg
dhck
dkhc
```

```stdout
ba
no answer
hegf
dhkc
hcdk
```

### Modified Kaprekar Numbers

**Problem.** Print every number `n` in `[p, q]` such that splitting `n²` into a right part with `d` digits (`d` = digits of `n`) and the remaining left part gives two numbers that sum to `n`. Print `INVALID RANGE` if there are none.

**Idea.** Use string slicing on the square: the right part is the last `d` characters, the left part is the rest (or 0 if empty).

**Steps.**
1. For each `n`: `sq = str(n * n)`, `d = len(str(n))`.
2. `right = int(sq[-d:])`, `left = int(sq[:-d] or 0)`; keep `n` if `left + right == n`.
3. Print the numbers separated by spaces, or `INVALID RANGE`.

```python
def kaprekarNumbers(p, q):
    found = []
    for n in range(p, q + 1):
        sq, d = str(n * n), len(str(n))
        if int(sq[:-d] or 0) + int(sq[-d:]) == n:
            found.append(n)
    print(*found) if found else print("INVALID RANGE")


if __name__ == '__main__':
    p = int(input().strip())
    q = int(input().strip())
    kaprekarNumbers(p, q)
```

**Watch out.** For `n = 1`, `sq = "1"` and the left part is empty; `int("" or 0)` handles it.

```stdin
1
100
```

```stdout
1 9 45 55 99
```

### Beautiful Triplets

**Problem.** In a strictly increasing array, count triplets `i < j < k` with `a[j] - a[i] = a[k] - a[j] = d`.

**Idea.** The values are distinct and sorted, so a triplet is determined by its first value `x`: it exists when `x + d` and `x + 2d` are both present.

**Steps.**
1. Put the values in a set.
2. Count `x` with `x + d` and `x + 2d` in the set.

```python
import os


def beautifulTriplets(d, arr):
    values = set(arr)
    return sum(x + d in values and x + 2 * d in values for x in arr)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, d = map(int, input().split())
    arr = list(map(int, input().rstrip().split()))
    result = beautifulTriplets(d, arr)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** This relies on the values being strictly increasing (distinct). With duplicates, you'd multiply counts instead.

```stdin
7 3
1 2 4 5 7 8 10
```

```stdout
3
```

### Minimum Distances

**Problem.** Return the smallest distance between two equal values in the array, or `-1`.

**Idea.** Remember the last index of each value; when a value repeats, the gap to its last occurrence is the only candidate worth checking.

**Steps.**
1. `last = {}`, `best = inf`.
2. For each index `i`: if `a[i]` was seen, update `best` with `i - last[a[i]]`; set `last[a[i]] = i`.
3. Return `best` or `-1`.

```python
import os


def minimumDistances(a):
    last, best = {}, float("inf")
    for i, x in enumerate(a):
        if x in last:
            best = min(best, i - last[x])
        last[x] = i
    return best if best != float("inf") else -1


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    a = list(map(int, input().rstrip().split()))
    result = minimumDistances(a)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Only consecutive occurrences matter: the closest equal pair always involves neighbouring occurrences.

```stdin
6
7 1 3 4 1 7
```

```stdout
3
```

### Halloween Sale

**Problem.** The first game costs `p`; each next one costs `d` less, but never less than `m`. How many games can you buy with `s` dollars?

**Idea.** Simulate purchases while the money lasts.

**Steps.**
1. `price = p`, `count = 0`.
2. While `s >= price`: pay, count it, then `price = max(price - d, m)`.

```python
import os


def howManyGames(p, d, m, s):
    price = p
    count = 0
    while s >= price:
        s -= price
        count += 1
        price = max(price - d, m)
    return count


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    p, d, m, s = map(int, input().split())
    answer = howManyGames(p, d, m, s)
    fptr.write(str(answer) + '\n')
    fptr.close()
```

**Watch out.** `s <= 10⁴` and every game costs at least 1, so the loop is short.

```stdin
20 3 6 80
```

```stdout
6
```

### The Time in Words

**Problem.** Write a time like `5:47` in words: `thirteen minutes to six`, with `o' clock`, `quarter`, `half`, `past` and `to`.

**Idea.** Build the words for 1–29 once, then handle the cases: `:00`, `:15`, `:30`, `:45`, minutes up to 30 (`past` this hour) and after 30 (`to` the next hour).

**Steps.**
1. Words for 1–19 from a list; 20–29 as `twenty` plus the ones word.
2. `m == 0` → `<h> o' clock`; `m <= 30` → `past h`; `m > 30` → `60 - m` `to` the next hour.
3. Use `quarter` for 15, `half` for 30, and `minute` (singular) for 1.

```python
import os

ONES = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
        "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]


def words(x):
    return ONES[x] if x < 20 else "twenty" + ("" if x == 20 else " " + ONES[x - 20])


def timeInWords(h, m):
    if m == 0:
        return f"{words(h)} o' clock"
    hour, minutes, rel = (h, m, "past") if m <= 30 else (h % 12 + 1, 60 - m, "to")
    if minutes == 15:
        part = "quarter"
    elif minutes == 30:
        part = "half"
    else:
        part = f"{words(minutes)} minute{'s' if minutes > 1 else ''}"
    return f"{part} {rel} {words(hour)}"


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    h = int(input().strip())
    m = int(input().strip())
    result = timeInWords(h, m)
    fptr.write(result + '\n')
    fptr.close()
```

**Watch out.** After 12:45 comes `one`, not `thirteen`: `h % 12 + 1`.

```stdin
5
47
```

```stdout
thirteen minutes to six
```

### Chocolate Feast

**Problem.** Bobby has `n` money, bars cost `c`, and `m` wrappers buy a free bar. How many bars does he eat?

**Idea.** Buy as many as possible, then keep trading wrappers while you have at least `m`; each free bar gives a new wrapper.

**Steps.**
1. `bars = wrappers = n // c`.
2. While `wrappers >= m`: `new = wrappers // m`; `bars += new`; `wrappers = wrappers % m + new`.

```python
import os


def chocolateFeast(n, c, m):
    bars = wrappers = n // c
    while wrappers >= m:
        new = wrappers // m
        bars += new
        wrappers = wrappers % m + new
    return bars


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n, c, m = map(int, input().split())
        fptr.write(str(chocolateFeast(n, c, m)) + '\n')
    fptr.close()
```

**Watch out.** Don't forget the leftover wrappers (`wrappers % m`) when trading.

```stdin
3
10 2 5
12 4 4
6 2 2
```

```stdout
6
3
5
```

### Service Lane

**Problem.** For each segment `[i, j]` of the service lane, return the widest vehicle that fits, which is the minimum width in that segment.

**Idea.** The bottleneck is the narrowest point, so take the minimum of the slice. Segments are at most 1000 long, so this is fast enough.

**Steps.**
1. For each `(i, j)`, return `min(width[i:j + 1])`.

```python
import os


def serviceLane(n, cases):
    return [min(width[i:j + 1]) for i, j in cases]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, t = map(int, input().split())
    width = list(map(int, input().rstrip().split()))
    cases = [list(map(int, input().rstrip().split())) for _ in range(t)]
    result = serviceLane(n, cases)
    fptr.write('\n'.join(map(str, result)))
    fptr.write('\n')
    fptr.close()
```

**Watch out.** HackerRank's Python starter passes `n` instead of `width`; `width` is a global read in the main block, which is why the function can use it.

```stdin
8 5
2 3 1 2 3 2 3 3
0 3
4 6
6 7
3 5
0 7
```

```stdout
1
2
3
2
1
```

### Lisa's Workbook

**Problem.** Chapters are printed with at most `k` problems per page, each chapter starting on a new page. A problem is special if its number within the chapter equals its page number. Count the special problems.

**Idea.** Walk page by page. A page holds problems `start..end`; the page is special if its number is in that range.

**Steps.**
1. `page = 1`.
2. For each chapter, for each block of `k` problems `[start, end]`: if `start <= page <= end`, count it; then `page += 1`.

```python
import os


def workbook(n, k, arr):
    page = special = 0
    for problems in arr:
        for start in range(1, problems + 1, k):
            page += 1
            end = min(start + k - 1, problems)
            if start <= page <= end:
                special += 1
    return special


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    arr = list(map(int, input().rstrip().split()))
    result = workbook(n, k, arr)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Problem numbers restart at 1 in each chapter, but page numbers keep counting.

```stdin
5 3
4 2 6 1 10
```

```stdout
4
```

### Flatland Space Stations

**Problem.** Cities `0..n-1` lie on a line; some have space stations. Return the maximum distance from any city to its nearest station.

**Idea.** Sort the stations. The worst city is either before the first station, after the last one, or in the middle of a gap between two stations.

**Steps.**
1. Sort `c`.
2. Candidates: `c[0]`, `n - 1 - c[-1]`, and `(c[i + 1] - c[i]) // 2` for each gap.
3. Return the maximum.

```python
import os


def flatlandSpaceStations(n, c):
    c = sorted(c)
    best = max(c[0], n - 1 - c[-1])
    for a, b in zip(c, c[1:]):
        best = max(best, (b - a) // 2)
    return best


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m = map(int, input().split())
    c = list(map(int, input().rstrip().split()))
    result = flatlandSpaceStations(n, c)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** The station list is unordered in the input; sort it first.

```stdin
5 2
0 4
```

```stdout
2
```

### Fair Rations

**Problem.** Give out loaves so everyone ends with an even number; each loaf to person `i` must come with a loaf to a neighbour. Print the minimum loaves, or `NO` if impossible.

**Idea.** Each handout adds 2 loaves, so an odd total can never become all-even → `NO`. Otherwise, greedily fix odd people from left to right by giving a loaf to them and the next person.

**Steps.**
1. For `i` from 0 to `n - 2`: if `B[i]` is odd, give one to `i` and `i + 1` (count 2).
2. If the last person is odd, return `NO`; else the count.

```python
import os


def fairRations(B):
    B = B[:]
    loaves = 0
    for i in range(len(B) - 1):
        if B[i] % 2:
            B[i] += 1
            B[i + 1] += 1
            loaves += 2
    return "NO" if B[-1] % 2 else str(loaves)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    N = int(input().strip())
    B = list(map(int, input().rstrip().split()))
    result = fairRations(B)
    fptr.write(result + '\n')
    fptr.close()
```

**Watch out.** The function must return a **string** (`"4"` or `"NO"`): the starter writes `result + '\n'`.

```stdin
5
2 3 4 5 6
```

```stdout
4
```

### Cavity Map

**Problem.** Mark every non-border cell whose depth is strictly greater than all four neighbours with `X`.

**Idea.** Check each interior cell against its four neighbours in the original grid, and write the `X` into a copy.

**Steps.**
1. Copy the grid as lists of characters.
2. For each interior cell, if it's greater than up, down, left and right, set it to `X` in the copy.
3. Join the rows back into strings.

```python
import os


def cavityMap(grid):
    n = len(grid)
    out = [list(row) for row in grid]
    for i in range(1, n - 1):
        for j in range(1, n - 1):
            d = grid[i][j]
            if all(d > grid[x][y] for x, y in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1))):
                out[i][j] = "X"
    return ["".join(row) for row in out]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    grid = [input() for _ in range(n)]
    result = cavityMap(grid)
    fptr.write('\n'.join(result))
    fptr.write('\n')
    fptr.close()
```

**Watch out.** Compare against the **original** grid, not the one you're writing `X` into. Comparing single digit characters works because `'0' < '1' < ... < '9'`.

```stdin
4
1112
1912
1892
1234
```

```stdout
1112
1X12
18X2
1234
```

### Manasa and Stones

**Problem.** Starting from 0, each of the next `n - 1` stones adds `a` or `b`. List all possible values of the last stone in increasing order.

**Idea.** Only the number of `b` steps matters: with `i` steps of `b`, the last stone is `(n - 1 - i)·a + i·b`.

**Steps.**
1. Compute that value for `i = 0..n-1`.
2. Return the sorted distinct values.

```python
import os


def stones(n, a, b):
    return sorted({(n - 1 - i) * a + i * b for i in range(n)})


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    T = int(input().strip())
    for _ in range(T):
        n = int(input().strip())
        a = int(input().strip())
        b = int(input().strip())
        fptr.write(' '.join(map(str, stones(n, a, b))) + '\n')
    fptr.close()
```

**Watch out.** When `a == b` there's only one value; the set removes the duplicates.

```stdin
2
3
1
2
4
10
100
```

```stdout
2 3 4
30 120 210 300
```

### The Grid Search

**Problem.** Does the pattern `P` (rows of digits) appear as a block inside the grid `G`?

**Idea.** For each grid row, find every position where the first pattern row starts (`str.find` in a loop), then check that the following pattern rows match at the same column.

**Steps.**
1. For each starting row `i` with room for the pattern:
2. Find each column `j` where `G[i]` contains `P[0]`.
3. If `G[i + t][j:j + c] == P[t]` for every pattern row `t`, return `YES`.

```python
import os


def gridSearch(G, P):
    r, c = len(P), len(P[0])
    for i in range(len(G) - r + 1):
        j = G[i].find(P[0])
        while j != -1:
            if all(G[i + t][j:j + c] == P[t] for t in range(1, r)):
                return "YES"
            j = G[i].find(P[0], j + 1)
    return "NO"


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        R, C = map(int, input().split())
        G = [input() for _ in range(R)]
        r, c = map(int, input().split())
        P = [input() for _ in range(r)]
        fptr.write(gridSearch(G, P) + '\n')
    fptr.close()
```

**Watch out.** Checking only the first match in each row misses overlapping occurrences; keep searching from `j + 1`.

```stdin
2
10 10
7283455864
6731158619
8988242643
3830589324
2229505813
5633845374
6473530293
7053106601
0834282956
4607924137
3 4
9505
3845
3530
15 15
400453592126560
114213133098692
474386082879648
522356951189169
887109450487496
252802633388782
502771484966748
075975207693780
511799789562806
404007454272504
549043809916080
962410809534811
445893523733475
768705303214174
650629270887160
2 2
99
99
```

```stdout
YES
NO
```

### Happy Ladybugs

**Problem.** A board has ladybugs (letters) and empty cells (`_`). A ladybug is happy next to one of the same colour. You may move any ladybug to any empty cell. Can all ladybugs become happy?

**Idea.** If there's at least one empty cell, you can rearrange freely, so every colour just needs at least 2 ladybugs. With no empty cell, nothing can move: check the board as it is.

**Steps.**
1. Count the colours.
2. With an `_`: `YES` if every colour count is at least 2.
3. Without: `YES` if every ladybug has an equal neighbour.

```python
import os
from collections import Counter


def happyLadybugs(b):
    counts = Counter(b)
    if "_" in counts:
        return "YES" if all(v >= 2 for ch, v in counts.items() if ch != "_") else "NO"
    for i, ch in enumerate(b):
        left = i > 0 and b[i - 1] == ch
        right = i < len(b) - 1 and b[i + 1] == ch
        if not (left or right):
            return "NO"
    return "YES"


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    g = int(input().strip())
    for _ in range(g):
        n = int(input().strip())
        b = input()
        fptr.write(happyLadybugs(b) + '\n')
    fptr.close()
```

**Watch out.** A board with only `_` has no unhappy ladybug, so the answer is `YES`.

```stdin
4
7
RBY_YBR
6
X_Y__X
2
__
6
B_RRBR
```

```stdout
YES
NO
YES
YES
```

### Strange Counter

**Problem.** A counter starts at 3 and counts down to 1; then it restarts at double the previous starting value (6, 12, ...). What does it show at time `t`?

**Idea.** Cycle `k` starts at time `start` with value `v` and lasts `v` seconds. Skip whole cycles until `t` falls inside one, then the display is `v - (t - start)`.

**Steps.**
1. `start = 1`, `v = 3`.
2. While `t >= start + v`: `start += v`; `v *= 2`.
3. Return `v - (t - start)`.

```python
import os


def strangeCounter(t):
    start, v = 1, 3
    while t >= start + v:
        start += v
        v *= 2
    return v - (t - start)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    result = strangeCounter(t)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** `t` reaches 10¹², but cycles double, so the loop runs only about 40 times.

```stdin
4
```

```stdout
6
```

### 3D Surface Area

**Problem.** Cubes are stacked on an `H × W` board, `A[i][j]` cubes on each cell. Return the total visible surface area.

**Idea.** Every stack contributes a top and a bottom (2). For each of its four sides, the exposed area is how much taller it is than the neighbour (out-of-board neighbours have height 0).

**Steps.**
1. `area = 2 * H * W` (tops and bottoms; every height is at least 1).
2. For every cell and each of the 4 directions, add `max(0, A[i][j] - neighbour)`.

```python
import os


def surfaceArea(A):
    H, W = len(A), len(A[0])
    area = 2 * H * W
    for i in range(H):
        for j in range(W):
            for x, y in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)):
                neighbour = A[x][y] if 0 <= x < H and 0 <= y < W else 0
                area += max(0, A[i][j] - neighbour)
    return area


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    H, W = map(int, input().split())
    A = [list(map(int, input().rstrip().split())) for _ in range(H)]
    result = surfaceArea(A)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Counting `max(0, a - b)` from both sides of a shared wall counts the difference exactly once.

```stdin
3 3
1 3 4
2 2 3
1 2 4
```

```stdout
60
```

### Absolute Permutation

**Problem.** Find the lexicographically smallest permutation `P` of `1..n` with `|P[i] - i| = k` for every position, or `-1`.

**Idea.** With `k = 0` the identity works. Otherwise positions come in blocks of `k`: the first block takes `i + k`, the next block takes `i - k`, and so on. That only fits if `n` is a multiple of `2k`.

**Steps.**
1. `k == 0` → `1..n`.
2. If `n % (2k) != 0` → `[-1]`.
3. Otherwise position `i` (1-based) gets `i + k` if `((i - 1) // k)` is even, else `i - k`.

```python
import os


def absolutePermutation(n, k):
    if k == 0:
        return list(range(1, n + 1))
    if n % (2 * k):
        return [-1]
    return [i + k if ((i - 1) // k) % 2 == 0 else i - k for i in range(1, n + 1)]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n, k = map(int, input().split())
        fptr.write(' '.join(map(str, absolutePermutation(n, k))) + '\n')
    fptr.close()
```

**Watch out.** Position 1 can only hold `1 + k` (since `1 - k < 1`), which forces the whole block pattern; that's why there's exactly one candidate to check.

```stdin
3
2 1
3 0
3 2
```

```stdout
2 1
1 2 3
-1
```

### The Bomberman Game

**Problem.** Bombs explode 3 seconds after being planted, clearing their cell and its 4 neighbours. Bomberman fills every empty cell with bombs every other second. Print the grid after `n` seconds (`n` up to 10⁹).

**Idea.** The grid repeats with period 4 after the start: even seconds are completely full; seconds 3, 7, 11, ... show the first detonation pattern; seconds 5, 9, 13, ... show the second one.

**Steps.**
1. `n == 1` → the initial grid. `n` even → all `O`.
2. `first` = detonate the initial bombs on a full grid.
3. `n % 4 == 3` → `first`; `n % 4 == 1` → detonate `first`'s bombs on a full grid.

```python
import os


def bomberMan(n, grid):
    r, c = len(grid), len(grid[0])

    def detonate(g):
        out = [["O"] * c for _ in range(r)]
        for i in range(r):
            for j in range(c):
                if g[i][j] == "O":
                    for x, y in ((i, j), (i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)):
                        if 0 <= x < r and 0 <= y < c:
                            out[x][y] = "."
        return ["".join(row) for row in out]

    if n == 1:
        return grid
    if n % 2 == 0:
        return ["O" * c] * r
    first = detonate(grid)
    return first if n % 4 == 3 else detonate(first)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    r, c, n = map(int, input().split())
    grid = [input() for _ in range(r)]
    result = bomberMan(n, grid)
    fptr.write('\n'.join(result))
    fptr.write('\n')
    fptr.close()
```

**Watch out.** Simulating second by second up to 10⁹ is impossible; finding the cycle is the whole problem.

```stdin
6 7 3
.......
...O...
....O..
.......
OO.....
OO.....
```

```stdout
OOO.OOO
OO...OO
OOO...O
..OO.OO
...OOOO
...OOOO
```

### Ema's Supercomputer

**Problem.** In a grid of good (`G`) and bad (`B`) cells, place two non-overlapping pluses made of good cells (equal odd-length arms) and maximize the product of their areas.

**Idea.** The grid is at most 15 × 15, so list every plus (each centre with each arm length) as a set of cells, then try all pairs that don't overlap.

**Steps.**
1. For each good cell, grow the arm length `k = 0, 1, 2, ...` while all four arm cells are good; record `(area = 4k + 1, cells)`.
2. For each pair of pluses, if their cell sets are disjoint, update the best product.

```python
import os


def twoPluses(grid):
    n, m = len(grid), len(grid[0])
    pluses = []
    for i in range(n):
        for j in range(m):
            k, cells = 0, set()
            while (i - k >= 0 and i + k < n and j - k >= 0 and j + k < m and
                   all(grid[x][y] == "G" for x, y in ((i - k, j), (i + k, j), (i, j - k), (i, j + k)))):
                cells |= {(i - k, j), (i + k, j), (i, j - k), (i, j + k)}
                pluses.append((4 * k + 1, frozenset(cells)))
                k += 1
    best = 0
    for a in range(len(pluses)):
        for b in range(a + 1, len(pluses)):
            product = pluses[a][0] * pluses[b][0]
            if product > best and pluses[a][1].isdisjoint(pluses[b][1]):
                best = product
    return best


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m = map(int, input().split())
    grid = [input() for _ in range(n)]
    result = twoPluses(grid)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Using only the **largest** plus at each centre is wrong: a smaller plus may be needed to avoid overlapping the other one. That's why every arm length is recorded.

```stdin
5 6
GGGGGG
GBBBGB
GGGGGG
GGBBGB
GGGGGG
```

```stdout
5
```

### Larry's Array

**Problem.** Can a permutation be sorted using only rotations of 3 consecutive elements (`ABC → BCA`)?

**Idea.** A 3-rotation is two swaps, so it never changes the parity of the number of inversions. It's sortable exactly when the inversion count is even.

**Steps.**
1. Count pairs `i < j` with `A[i] > A[j]`.
2. Return `YES` if the count is even, else `NO`.

```python
import os


def larrysArray(A):
    inversions = sum(1 for i in range(len(A)) for j in range(i + 1, len(A)) if A[i] > A[j])
    return "YES" if inversions % 2 == 0 else "NO"


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n = int(input().strip())
        A = list(map(int, input().rstrip().split()))
        fptr.write(larrysArray(A) + '\n')
    fptr.close()
```

**Watch out.** O(n²) with `n <= 1000` is fine. For bigger inputs, count inversions with merge sort or a Fenwick tree.

```stdin
3
3
3 1 2
4
1 3 4 2
5
1 2 3 5 4
```

```stdout
YES
YES
NO
```

### Almost Sorted

**Problem.** Can the array be sorted with **one** swap or **one** reversal of a segment? Print `yes` (with `swap l r` or `reverse l r`, 1-based) or `no`. Prefer swap when both work.

**Idea.** Compare with the sorted array. The positions that differ must be fixed: exactly two differing positions → swap; otherwise the whole block between the first and last difference must be the sorted block reversed.

**Steps.**
1. `diff` = indices where `arr` and `sorted(arr)` differ. None → `yes`.
2. Two differences → `yes` / `swap l r`.
3. Else if `arr[l:r + 1]` equals the sorted block reversed → `yes` / `reverse l r`; otherwise `no`.

```python
def almostSorted(arr):
    target = sorted(arr)
    diff = [i for i in range(len(arr)) if arr[i] != target[i]]
    if not diff:
        print("yes")
        return
    l, r = diff[0], diff[-1]
    if len(diff) == 2:
        print("yes")
        print("swap", l + 1, r + 1)
    elif arr[l:r + 1] == target[l:r + 1][::-1]:
        print("yes")
        print("reverse", l + 1, r + 1)
    else:
        print("no")


if __name__ == '__main__':
    n = int(input().strip())
    arr = list(map(int, input().rstrip().split()))
    almostSorted(arr)
```

**Watch out.** A segment of length 2 is both a swap and a reversal; the problem wants `swap`, which is why that check comes first.

```stdin
6
1 5 4 3 2 6
```

```stdout
yes
reverse 2 5
```

### Matrix Layer Rotation

**Problem.** Rotate every layer (ring) of an `m × n` matrix anticlockwise `r` times and print the result. `r` can be 10⁹.

**Idea.** Treat each ring as a circular list. Read it clockwise from its top-left corner; an anticlockwise rotation by `r` is just shifting that list left by `r % len(ring)`.

**Steps.**
1. For each layer, list its coordinates clockwise: top row, right column, bottom row, left column.
2. Read the values, shift them left by `r % len`, and write them back to the same coordinates.
3. Print the matrix.

```python
def matrixRotation(matrix, r):
    m, n = len(matrix), len(matrix[0])
    for layer in range(min(m, n) // 2):
        top, left, bottom, right = layer, layer, m - 1 - layer, n - 1 - layer
        ring = ([(top, j) for j in range(left, right)] +
                [(i, right) for i in range(top, bottom)] +
                [(bottom, j) for j in range(right, left, -1)] +
                [(i, left) for i in range(bottom, top, -1)])
        values = [matrix[i][j] for i, j in ring]
        k = r % len(values)
        values = values[k:] + values[:k]
        for (i, j), v in zip(ring, values):
            matrix[i][j] = v
    for row in matrix:
        print(*row)


if __name__ == '__main__':
    m, n, r = map(int, input().split())
    matrix = [list(map(int, input().rstrip().split())) for _ in range(m)]
    matrixRotation(matrix, r)
```

**Watch out.** Rotating step by step is far too slow; always reduce `r` modulo the ring length, which is different for each layer.

```stdin
4 4 2
1 2 3 4
5 6 7 8
9 10 11 12
13 14 15 16
```

```stdout
3 4 8 12
2 11 10 16
1 7 6 15
5 9 13 14
```
