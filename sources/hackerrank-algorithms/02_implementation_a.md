## Implementation

### Grading Students

**Problem.** Round each grade up to the next multiple of 5 when the difference is less than 3, but never round a grade below 38 (it stays failing).

**Idea.** For grade `g`, the next multiple of 5 is `(g // 5 + 1) * 5`. Round only if `g >= 38` and that multiple is less than 3 away.

**Steps.**
1. For each grade compute the next multiple of 5.
2. Use it if `g >= 38` and `next - g < 3`, otherwise keep `g`.

```python
import os


def gradingStudents(grades):
    result = []
    for g in grades:
        nxt = (g // 5 + 1) * 5
        result.append(nxt if g >= 38 and nxt - g < 3 else g)
    return result


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    grades_count = int(input().strip())
    grades = [int(input().strip()) for _ in range(grades_count)]
    result = gradingStudents(grades)
    fptr.write('\n'.join(map(str, result)))
    fptr.write('\n')
    fptr.close()
```

**Watch out.** A grade that is already a multiple of 5 (like 40) gives `next = 45`, 5 away, so it correctly stays the same.

```stdin
4
73
67
38
33
```

```stdout
75
67
40
33
```

### Apple and Orange

**Problem.** The house spans `[s, t]`. Apples fall `d` units from the apple tree at `a`, oranges from the orange tree at `b`. Print how many apples and how many oranges land on the house.

**Idea.** A fruit lands at `tree + d`. Count the landing points inside `[s, t]`.

**Steps.**
1. Count apples with `s <= a + d <= t`.
2. Count oranges with `s <= b + d <= t`.
3. Print both counts on separate lines.

```python
def countApplesAndOranges(s, t, a, b, apples, oranges):
    print(sum(s <= a + d <= t for d in apples))
    print(sum(s <= b + d <= t for d in oranges))


if __name__ == '__main__':
    s, t = map(int, input().split())
    a, b = map(int, input().split())
    m, n = map(int, input().split())
    apples = list(map(int, input().rstrip().split()))
    oranges = list(map(int, input().rstrip().split()))
    countApplesAndOranges(s, t, a, b, apples, oranges)
```

**Watch out.** The range is inclusive on both ends. Distances can be negative (the fruit falls to the left).

```stdin
7 11
5 15
3 2
-2 2 1
5 -6
```

```stdout
1
1
```

### Number Line Jumps

**Problem.** Kangaroo 1 starts at `x1` and jumps `v1`; kangaroo 2 starts at `x2 > x1` and jumps `v2`. Can they land on the same spot after the same number of jumps?

**Idea.** After `j` jumps they meet when `x1 + j·v1 = x2 + j·v2`, i.e. `j = (x2 - x1) / (v1 - v2)`. That needs the back kangaroo to be faster (`v1 > v2`) and the gap to divide evenly.

**Steps.**
1. If `v1 > v2` and `(x2 - x1) % (v1 - v2) == 0`, return `YES`.
2. Otherwise return `NO`.

```python
import os


def kangaroo(x1, v1, x2, v2):
    if v1 > v2 and (x2 - x1) % (v1 - v2) == 0:
        return "YES"
    return "NO"


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    x1, v1, x2, v2 = map(int, input().split())
    result = kangaroo(x1, v1, x2, v2)
    fptr.write(result + '\n')
    fptr.close()
```

**Watch out.** Simulating jumps can loop forever when they never meet. The formula answers in O(1), and `v1 == v2` can never meet because they start apart.

```stdin
0 3 4 2
```

```stdout
YES
```

### Between Two Sets

**Problem.** Count integers `x` such that every element of `a` divides `x`, and `x` divides every element of `b`.

**Idea.** "All of `a` divide `x`" means `x` is a multiple of `lcm(a)`. "`x` divides all of `b`" means `x` divides `gcd(b)`. So count the multiples of `lcm(a)` that divide `gcd(b)`.

**Steps.**
1. `l = lcm(a)`, `g = gcd(b)`.
2. Count `x` in `l, 2l, 3l, ... <= g` with `g % x == 0`.

```python
import os
from functools import reduce
from math import gcd


def getTotalX(a, b):
    l = reduce(lambda x, y: x * y // gcd(x, y), a)
    g = reduce(gcd, b)
    return sum(1 for x in range(l, g + 1, l) if g % x == 0)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m = map(int, input().split())
    arr = list(map(int, input().rstrip().split()))
    brr = list(map(int, input().rstrip().split()))
    total = getTotalX(arr, brr)
    fptr.write(str(total) + '\n')
    fptr.close()
```

**Watch out.** If `lcm(a) > gcd(b)`, the range is empty and the answer is 0.

```stdin
2 3
2 4
16 32 96
```

```stdout
3
```

### Breaking the Records

**Problem.** The first game sets both the season's highest and lowest score. Count how many times the highest record is broken and how many times the lowest is broken.

**Idea.** Track the current maximum and minimum; count each time a score goes strictly above or below them.

**Steps.**
1. `high = low = scores[0]`.
2. For each later score: if it's above `high`, update and count; if it's below `low`, update and count.
3. Return `[high_breaks, low_breaks]`.

```python
import os


def breakingRecords(scores):
    high = low = scores[0]
    most = least = 0
    for s in scores[1:]:
        if s > high:
            high, most = s, most + 1
        elif s < low:
            low, least = s, least + 1
    return [most, least]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    scores = list(map(int, input().rstrip().split()))
    result = breakingRecords(scores)
    fptr.write(' '.join(map(str, result)))
    fptr.write('\n')
    fptr.close()
```

**Watch out.** Equalling a record doesn't break it: use strict `>` and `<`.

```stdin
9
10 5 20 20 4 5 2 25 1
```

```stdout
2 4
```

### Subarray Division

**Problem.** Count contiguous segments of length `m` whose sum is `d`.

**Idea.** Slide a window of length `m` along the array and compare each window's sum with `d`.

**Steps.**
1. Start with the sum of the first `m` squares.
2. Slide the window one step at a time, adding the new square and removing the old one; count windows equal to `d`.

```python
import os


def birthday(s, d, m):
    if m > len(s):
        return 0
    window = sum(s[:m])
    count = int(window == d)
    for i in range(m, len(s)):
        window += s[i] - s[i - m]
        count += window == d
    return count


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    s = list(map(int, input().rstrip().split()))
    d, m = map(int, input().split())
    result = birthday(s, d, m)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** If the bar is shorter than `m`, no segment exists: return 0 instead of testing the whole bar.

```stdin
5
1 2 1 3 2
3 2
```

```stdout
2
```

### Divisible Sum Pairs

**Problem.** Count pairs `i < j` where `ar[i] + ar[j]` is divisible by `k`.

**Idea.** Two numbers sum to a multiple of `k` exactly when their remainders add up to `k` (or both are 0). Count remainders seen so far and, for each number, add how many earlier numbers complete it.

**Steps.**
1. `seen[r]` = how many earlier numbers have remainder `r`.
2. For each `x`: `r = x % k`; add `seen[(k - r) % k]`; then `seen[r] += 1`.

```python
import os


def divisibleSumPairs(n, k, ar):
    seen = [0] * k
    pairs = 0
    for x in ar:
        r = x % k
        pairs += seen[(k - r) % k]
        seen[r] += 1
    return pairs


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    ar = list(map(int, input().rstrip().split()))
    result = divisibleSumPairs(n, k, ar)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** `(k - r) % k` maps remainder 0 to partner 0. The O(n²) double loop also passes here (n ≤ 100), but this O(n) idea is what interviews look for.

```stdin
6 3
1 3 2 6 1 2
```

```stdout
5
```

### Migratory Birds

**Problem.** Return the most common bird type; on a tie, the smallest type id.

**Idea.** Count each type, then pick the maximum count, breaking ties by the smaller id.

**Steps.**
1. `counts = Counter(arr)`.
2. Return `min(counts, key=lambda t: (-counts[t], t))`.

```python
import os
from collections import Counter


def migratoryBirds(arr):
    counts = Counter(arr)
    return min(counts, key=lambda t: (-counts[t], t))


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    arr_count = int(input().strip())
    arr = list(map(int, input().rstrip().split()))
    result = migratoryBirds(arr)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** `Counter.most_common(1)` breaks ties by first appearance, not by smallest id. Use an explicit key.

```stdin
11
1 2 3 4 5 4 3 2 1 3 4
```

```stdout
3
```

### Day of the Programmer

**Problem.** Print the date of the 256th day of year `y` (1700–2700) in Russia, as `dd.mm.yyyy`. Before 1918 Russia used the Julian calendar, from 1919 the Gregorian one, and 1918 skipped 13 days in February.

**Idea.** The first 8 months have 243 days in a normal year (244 in a leap year), so day 256 is September 13 (12 in a leap year). Only the leap-year rule changes between calendars, and 1918 is a special case.

**Steps.**
1. `1918` → `26.09.1918` (February 14 was day 32, so the calendar is 13 days shorter).
2. Julian (`y < 1918`): leap if `y % 4 == 0`. Gregorian: leap if divisible by 400, or by 4 and not by 100.
3. Return `12.09.y` for leap years, `13.09.y` otherwise.

```python
import os


def dayOfProgrammer(year):
    if year == 1918:
        return "26.09.1918"
    if year < 1918:
        leap = year % 4 == 0
    else:
        leap = year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)
    return f"{12 if leap else 13}.09.{year}"


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    year = int(input().strip())
    result = dayOfProgrammer(year)
    fptr.write(result + '\n')
    fptr.close()
```

**Watch out.** 1800 is a leap year in the Julian calendar (divisible by 4) but not in the Gregorian one.

```stdin
1800
```

```stdout
12.09.1800
```

### Bill Division

**Problem.** Anna didn't eat item `k`. Brian charged her `b`. Print `Bon Appetit` if that's exactly half of the items she ate, otherwise print how much he owes her.

**Idea.** Anna's fair share is `(sum(bill) - bill[k]) / 2`. Compare it with `b`.

**Steps.**
1. `fair = (sum(bill) - bill[k]) // 2`.
2. Print `Bon Appetit` if `b == fair`, else `b - fair`.

```python
def bonAppetit(bill, k, b):
    fair = (sum(bill) - bill[k]) // 2
    print("Bon Appetit" if b == fair else b - fair)


if __name__ == '__main__':
    n, k = map(int, input().split())
    bill = list(map(int, input().rstrip().split()))
    b = int(input().strip())
    bonAppetit(bill, k, b)
```

**Watch out.** The problem guarantees the refund is an integer, so integer division is safe.

```stdin
4 1
3 10 2 9
12
```

```stdout
5
```

### Sales by Match

**Problem.** Count how many pairs of socks with the same colour there are.

**Idea.** Count each colour; each colour gives `count // 2` pairs.

**Steps.**
1. Count colours with `Counter`.
2. Sum `c // 2` over the counts.

```python
import os
from collections import Counter


def sockMerchant(n, ar):
    return sum(c // 2 for c in Counter(ar).values())


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    ar = list(map(int, input().rstrip().split()))
    result = sockMerchant(n, ar)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** One pass with a set also works: add a colour when you see it, remove it and count a pair when you see it again.

```stdin
9
10 20 20 10 10 30 50 10 20
```

```stdout
3
```

### Drawing Book

**Problem.** A book of `n` pages opens with page 1 on the right; each turn shows two more pages. What is the minimum number of turns to reach page `p`, starting from the front or the back?

**Idea.** Page `p` is on the spread number `p // 2` from the front. The last spread is `n // 2`, so from the back it takes `n // 2 - p // 2` turns.

**Steps.**
1. Return `min(p // 2, n // 2 - p // 2)`.

```python
import os


def pageCount(n, p):
    return min(p // 2, n // 2 - p // 2)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    p = int(input().strip())
    result = pageCount(n, p)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Thinking in spreads (pairs of pages) instead of single pages avoids the even/odd `n` special cases.

```stdin
6
2
```

```stdout
1
```

### Counting Valleys

**Problem.** A hike is a string of `U` and `D` steps starting and ending at sea level. Count the valleys (stretches below sea level).

**Idea.** Track the altitude. A valley ends exactly when an `U` step brings you back up to sea level.

**Steps.**
1. `level = 0`, `valleys = 0`.
2. For each step, move up or down; if the step was `U` and `level` is now 0, count a valley.

```python
import os


def countingValleys(steps, path):
    level = valleys = 0
    for step in path:
        level += 1 if step == "U" else -1
        if step == "U" and level == 0:
            valleys += 1
    return valleys


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    steps = int(input().strip())
    path = input()
    result = countingValleys(steps, path)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Counting "steps down from sea level" works too; just don't count every step below 0.

```stdin
8
UDDDUDUU
```

```stdout
1
```

### Electronics Shop

**Problem.** Buy one keyboard and one USB drive, spending as much as possible without going over budget `b`. Return `-1` if no pair fits.

**Idea.** Try every pair (at most 10⁶ combinations) and keep the best sum that's within budget.

**Steps.**
1. Take the maximum of `k + d` over all pairs with `k + d <= b`.
2. Default to `-1` when none qualifies.

```python
import os


def getMoneySpent(keyboards, drives, b):
    return max((k + d for k in keyboards for d in drives if k + d <= b), default=-1)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    b, n, m = map(int, input().split())
    keyboards = list(map(int, input().rstrip().split()))
    drives = list(map(int, input().rstrip().split()))
    moneySpent = getMoneySpent(keyboards, drives, b)
    fptr.write(str(moneySpent) + '\n')
    fptr.close()
```

**Watch out.** Faster: sort keyboards ascending and drives descending, then walk two pointers in O(n log n).

```stdin
10 2 3
3 1
5 2 8
```

```stdout
9
```

### Cats and a Mouse

**Problem.** Cat A at `x`, cat B at `y`, mouse at `z`. Print which cat reaches the mouse first, or `Mouse C` if they arrive together.

**Idea.** Compare the distances `|x - z|` and `|y - z|`.

**Steps.**
1. Smaller distance wins; equal distances → `Mouse C`.

```python
import os


def catAndMouse(x, y, z):
    a, b = abs(x - z), abs(y - z)
    if a < b:
        return "Cat A"
    if b < a:
        return "Cat B"
    return "Mouse C"


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input())
    for _ in range(q):
        x, y, z = map(int, input().split())
        fptr.write(catAndMouse(x, y, z) + '\n')
    fptr.close()
```

**Watch out.** Use absolute distances: the cats can be on either side of the mouse.

```stdin
2
1 2 3
1 3 2
```

```stdout
Cat B
Mouse C
```

### Forming a Magic Square

**Problem.** Change the numbers of a 3×3 grid (cost `|a - b|` per change) to make a magic square using 1–9. Return the minimum cost.

**Idea.** There are only 8 magic squares of order 3: one square and its rotations and mirror images. Compute the cost to each and take the minimum.

**Steps.**
1. Start from `8 1 6 / 3 5 7 / 4 9 2`.
2. Generate its 4 rotations and the mirror of each (8 squares).
3. Return the smallest total `|s[i] - magic[i]|`.

```python
import os


def formingMagicSquare(s):
    def rotate(q):
        return [q[6], q[3], q[0], q[7], q[4], q[1], q[8], q[5], q[2]]

    def mirror(q):
        return [q[2], q[1], q[0], q[5], q[4], q[3], q[8], q[7], q[6]]

    flat = [x for row in s for x in row]
    square, best = [8, 1, 6, 3, 5, 7, 4, 9, 2], float("inf")
    for _ in range(4):
        square = rotate(square)
        for candidate in (square, mirror(square)):
            best = min(best, sum(abs(a - b) for a, b in zip(flat, candidate)))
    return best


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    s = [list(map(int, input().rstrip().split())) for _ in range(3)]
    result = formingMagicSquare(s)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** You must reach a real magic square (each of 1–9 exactly once), not just equal row sums. That's why enumerating the 8 squares is the clean solution.

```stdin
4 9 2
3 5 7
8 1 5
```

```stdout
1
```

### Picking Numbers

**Problem.** Find the largest set of numbers from the array where any two differ by at most 1.

**Idea.** Such a set uses only two adjacent values `v` and `v + 1`. Count each value and take the best `count[v] + count[v + 1]`.

**Steps.**
1. Count values.
2. Return the maximum of `c[v] + c[v + 1]` over all `v`.

```python
import os
from collections import Counter


def pickingNumbers(a):
    c = Counter(a)
    return max(c[v] + c[v + 1] for v in c)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    a = list(map(int, input().rstrip().split()))
    result = pickingNumbers(a)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Despite the word "subarray", the elements don't have to be contiguous; it's really a subset.

```stdin
6
4 6 5 3 3 1
```

```stdout
3
```

### Climbing the Leaderboard

**Problem.** The leaderboard uses dense ranking (equal scores share a rank). For each of the player's scores (in increasing order), return the player's rank.

**Idea.** Remove duplicate scores, keep them sorted from high to low, and start a pointer at the bottom. Because the player's scores only increase, the pointer only moves up: O(n + m) overall.

**Steps.**
1. `board` = distinct scores, descending; `i` = last index.
2. For each score: while `i >= 0` and `score >= board[i]`, move `i` up.
3. The rank is `i + 2` (one below the last board score that is still higher).

```python
import os


def climbingLeaderboard(ranked, player):
    board = sorted(set(ranked), reverse=True)
    i = len(board) - 1
    ranks = []
    for score in player:
        while i >= 0 and score >= board[i]:
            i -= 1
        ranks.append(i + 2)
    return ranks


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    ranked_count = int(input().strip())
    ranked = list(map(int, input().rstrip().split()))
    player_count = int(input().strip())
    player = list(map(int, input().rstrip().split()))
    result = climbingLeaderboard(ranked, player)
    fptr.write('\n'.join(map(str, result)))
    fptr.write('\n')
    fptr.close()
```

**Watch out.** Recomputing the rank for each score from scratch is O(n·m) and times out. Binary search (`bisect`) on the deduplicated board is another O(m log n) option.

```stdin
7
100 100 50 40 40 20 10
4
5 25 50 120
```

```stdout
6
4
2
1
```

### The Hurdle Race

**Problem.** The character jumps `k` high; each potion dose adds 1. How many doses are needed to clear the tallest hurdle?

**Idea.** Only the tallest hurdle matters.

**Steps.**
1. Return `max(0, max(height) - k)`.

```python
import os


def hurdleRace(k, height):
    return max(0, max(height) - k)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    height = list(map(int, input().rstrip().split()))
    result = hurdleRace(k, height)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Don't return a negative number when `k` is already high enough.

```stdin
5 4
1 6 3 5 2
```

```stdout
2
```

### Designer PDF Viewer

**Problem.** Each letter has a height; each letter is 1 mm wide. Return the area of the highlight rectangle around a word.

**Idea.** The rectangle's height is the tallest letter in the word; its width is the word's length.

**Steps.**
1. `tallest = max(h[ord(c) - ord('a')] for c in word)`.
2. Return `tallest * len(word)`.

```python
import os


def designerPdfViewer(h, word):
    return max(h[ord(c) - ord('a')] for c in word) * len(word)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    h = list(map(int, input().rstrip().split()))
    word = input()
    result = designerPdfViewer(h, word)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** `ord(c) - ord('a')` maps `a..z` to `0..25`.

```stdin
1 3 1 3 1 4 1 3 2 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5
abc
```

```stdout
9
```

### Utopian Tree

**Problem.** A tree starts at height 1. Each spring it doubles, each summer it grows by 1. Return its height after `n` cycles.

**Idea.** Simulate: odd cycles (spring) double, even cycles (summer) add one.

**Steps.**
1. `height = 1`.
2. For cycle `1..n`: if odd, `height *= 2`; else `height += 1`.

```python
import os


def utopianTree(n):
    height = 1
    for cycle in range(1, n + 1):
        height = height * 2 if cycle % 2 else height + 1
    return height


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n = int(input().strip())
        fptr.write(str(utopianTree(n)) + '\n')
    fptr.close()
```

**Watch out.** Closed form: `2 ** ((n + 1) // 2 + 1) - 1 - (n % 2)`. The loop is clearer and n ≤ 60.

```stdin
3
0
1
4
```

```stdout
1
2
7
```

### Angry Professor

**Problem.** Class is cancelled if fewer than `k` students arrive on time (arrival time `<= 0`). Return `YES` if cancelled.

**Idea.** Count the on-time students and compare with `k`.

**Steps.**
1. `on_time = number of a[i] <= 0`.
2. Return `YES` if `on_time < k`, else `NO`.

```python
import os


def angryProfessor(k, a):
    on_time = sum(t <= 0 for t in a)
    return "YES" if on_time < k else "NO"


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n, k = map(int, input().split())
        a = list(map(int, input().rstrip().split()))
        fptr.write(angryProfessor(k, a) + '\n')
    fptr.close()
```

**Watch out.** Arriving at time `0` counts as on time. `YES` means "cancelled".

```stdin
2
4 3
-1 -3 4 2
4 2
0 -1 2 1
```

```stdout
YES
NO
```

### Beautiful Days at the Movies

**Problem.** A day `d` in `[i, j]` is beautiful if `|d - reverse(d)|` is divisible by `k`. Count them.

**Idea.** Reverse each number with string slicing and test the condition.

**Steps.**
1. For each `d` in the range: `rev = int(str(d)[::-1])`.
2. Count days with `abs(d - rev) % k == 0`.

```python
import os


def beautifulDays(i, j, k):
    return sum(abs(d - int(str(d)[::-1])) % k == 0 for d in range(i, j + 1))


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    i, j, k = map(int, input().split())
    result = beautifulDays(i, j, k)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** `int("021")` is `21`, so trailing zeros disappear correctly when reversed.

```stdin
20 23 6
```

```stdout
2
```

### Viral Advertising

**Problem.** Day 1: 5 people see an ad. Each day, half of the viewers (rounded down) like it and each shares it with 3 friends, who see it the next day. Return the total likes after `n` days.

**Idea.** Simulate day by day: `liked = shared // 2`, `shared = liked * 3`.

**Steps.**
1. `shared = 5`, `total = 0`.
2. Repeat `n` times: `liked = shared // 2`; `total += liked`; `shared = liked * 3`.

```python
import os


def viralAdvertising(n):
    shared, total = 5, 0
    for _ in range(n):
        liked = shared // 2
        total += liked
        shared = liked * 3
    return total


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    result = viralAdvertising(n)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** The answer is the **cumulative** likes, not the likes on day `n`.

```stdin
3
```

```stdout
9
```

### Save the Prisoner!

**Problem.** `n` prisoners sit in a circle; `m` sweets are handed out one by one starting at chair `s`. Which chair gets the last sweet?

**Idea.** The last sweet goes `m - 1` seats after `s`, wrapping around. Convert to 0-based, take the modulo, convert back.

**Steps.**
1. Return `(s - 1 + m - 1) % n + 1`.

```python
import os


def saveThePrisoner(n, m, s):
    return (s + m - 2) % n + 1


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n, m, s = map(int, input().split())
        fptr.write(str(saveThePrisoner(n, m, s)) + '\n')
    fptr.close()
```

**Watch out.** `(s + m - 1) % n` gives `0` instead of `n` for the last chair. Shifting to 0-based first avoids that off-by-one.

```stdin
2
5 2 1
5 2 2
```

```stdout
2
3
```

### Circular Array Rotation

**Problem.** Rotate an array right `k` times, then answer queries asking for the value at given indices.

**Idea.** Don't rotate. After `k` right rotations, index `q` holds the value that was at `(q - k) mod n`.

**Steps.**
1. For each query `q`, return `a[(q - k) % n]`.

```python
import os


def circularArrayRotation(a, k, queries):
    n = len(a)
    return [a[(q - k) % n] for q in queries]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k, q = map(int, input().split())
    a = list(map(int, input().rstrip().split()))
    queries = [int(input().strip()) for _ in range(q)]
    result = circularArrayRotation(a, k, queries)
    fptr.write('\n'.join(map(str, result)))
    fptr.write('\n')
    fptr.close()
```

**Watch out.** Python's `%` is always non-negative for a positive `n`, so `(q - k) % n` works even when `k > q`.

```stdin
3 2 3
1 2 3
0
1
2
```

```stdout
2
3
1
```

### Sequence Equation

**Problem.** `p` is a permutation of `1..n`. For each `x` from 1 to `n`, find `y` with `p(p(y)) = x`.

**Idea.** Build the inverse permutation `pos[v]` = index where `v` sits. Then `y = pos[pos[x]]`.

**Steps.**
1. `pos[p[i]] = i + 1` for every index.
2. Return `[pos[pos[x]] for x in 1..n]`.

```python
import os


def permutationEquation(p):
    pos = {v: i + 1 for i, v in enumerate(p)}
    return [pos[pos[x]] for x in range(1, len(p) + 1)]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    p = list(map(int, input().rstrip().split()))
    result = permutationEquation(p)
    fptr.write('\n'.join(map(str, result)))
    fptr.write('\n')
    fptr.close()
```

**Watch out.** The problem is 1-based; keep the `+ 1` when storing positions.

```stdin
3
2 3 1
```

```stdout
2
3
1
```

### Jumping on the Clouds: Revisited

**Problem.** Starting at cloud 0 with energy 100, jump `k` clouds at a time (circularly) until back at cloud 0. Each jump costs 1, plus 2 more when landing on a thundercloud (`1`). Return the final energy.

**Idea.** Simulate the jumps; the loop ends when the position returns to 0.

**Steps.**
1. `energy = 100`, `i = 0`.
2. Repeat: `i = (i + k) % n`; `energy -= 1 + 2 * c[i]`; stop when `i == 0`.

```python
import os


def jumpingOnClouds(c, k):
    n, energy, i = len(c), 100, 0
    while True:
        i = (i + k) % n
        energy -= 1 + 2 * c[i]
        if i == 0:
            return energy


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    c = list(map(int, input().rstrip().split()))
    result = jumpingOnClouds(c, k)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** The landing on cloud 0 at the end also costs energy (and the thundercloud penalty if `c[0]` were 1).

```stdin
8 2
0 0 1 0 0 1 1 0
```

```stdout
92
```

### Find Digits

**Problem.** Count the digits of `n` that divide `n` evenly.

**Idea.** Go through the digits as characters; skip `0` (division by zero).

**Steps.**
1. Count digits `d` with `d != 0` and `n % d == 0`.

```python
import os


def findDigits(n):
    return sum(1 for ch in str(n) if ch != "0" and n % int(ch) == 0)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n = int(input().strip())
        fptr.write(str(findDigits(n)) + '\n')
    fptr.close()
```

**Watch out.** Repeated digits count each time (`111` → 3).

```stdin
2
12
1012
```

```stdout
2
3
```

### Extra Long Factorials

**Problem.** Print `n!` for `n` up to 100 (far beyond 64-bit integers).

**Idea.** Python integers grow without limit, so the factorial is exact.

**Steps.**
1. Print `math.factorial(n)`.

```python
import math


def extraLongFactorials(n):
    print(math.factorial(n))


if __name__ == '__main__':
    n = int(input().strip())
    extraLongFactorials(n)
```

**Watch out.** In Java/C++ you'd need `BigInteger` or digit-by-digit multiplication on an array; that's what this problem tests in those languages.

```stdin
25
```

```stdout
15511210043330985984000000
```

### Append and Delete

**Problem.** Using exactly `k` operations (append a letter, or delete the last letter; deleting from an empty string is allowed and does nothing), can `s` become `t`?

**Idea.** Keep the common prefix; delete the rest of `s` and append the rest of `t`: `need` operations. Extra operations can be wasted in pairs (append + delete), or freely once the string is empty.

**Steps.**
1. `common` = length of the common prefix; `need = len(s) + len(t) - 2 * common`.
2. If `k >= len(s) + len(t)`: `Yes` (delete everything, waste moves on the empty string, then type `t`).
3. Else `Yes` if `k >= need` and `(k - need)` is even; otherwise `No`.

```python
import os


def appendAndDelete(s, t, k):
    common = 0
    while common < min(len(s), len(t)) and s[common] == t[common]:
        common += 1
    need = len(s) + len(t) - 2 * common
    if k >= len(s) + len(t):
        return "Yes"
    return "Yes" if k >= need and (k - need) % 2 == 0 else "No"


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    s = input()
    t = input()
    k = int(input().strip())
    result = appendAndDelete(s, t, k)
    fptr.write(result + '\n')
    fptr.close()
```

**Watch out.** Exactly `k` operations, not "at most". Parity matters unless you can burn moves on the empty string.

```stdin
hackerhappy
hackerrank
9
```

```stdout
Yes
```

### Sherlock and Squares

**Problem.** Count the perfect squares in `[a, b]`.

**Idea.** The squares up to `x` are `1², 2², ..., isqrt(x)²`. So the count in `[a, b]` is `isqrt(b) - isqrt(a - 1)`.

**Steps.**
1. Return `isqrt(b) - isqrt(a - 1)`.

```python
import os
from math import isqrt


def squares(a, b):
    return isqrt(b) - isqrt(a - 1)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        a, b = map(int, input().split())
        fptr.write(str(squares(a, b)) + '\n')
    fptr.close()
```

**Watch out.** `math.isqrt` is exact; `int(math.sqrt(x))` can be off by one for large `x` because of floating-point rounding.

```stdin
2
3 9
17 24
```

```stdout
2
0
```

### Library Fine

**Problem.** Compute a library fine: 15 per day late in the same month, 500 per month late in the same year, 10000 flat if returned in a later year, 0 if on time.

**Idea.** Compare year, then month, then day, in that order.

**Steps.**
1. Later year → 10000.
2. Same year, later month → `500 * (m1 - m2)`.
3. Same month, later day → `15 * (d1 - d2)`.
4. Otherwise 0.

```python
import os


def libraryFine(d1, m1, y1, d2, m2, y2):
    if y1 > y2:
        return 10000
    if y1 == y2 and m1 > m2:
        return 500 * (m1 - m2)
    if y1 == y2 and m1 == m2 and d1 > d2:
        return 15 * (d1 - d2)
    return 0


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    d1, m1, y1 = map(int, input().split())
    d2, m2, y2 = map(int, input().split())
    result = libraryFine(d1, m1, y1, d2, m2, y2)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Returning early in an earlier year (but a "later" month or day) is still on time: always check the year first.

```stdin
9 6 2015
6 6 2015
```

```stdout
45
```
