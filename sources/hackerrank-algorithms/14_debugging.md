## Debugging

### Prime Dates

**Problem.** Count the "lucky" dates between two dates `dd-mm-yyyy` (inclusive). A date is lucky when the number formed by writing day, month and year one after another (dropping the leading zeros) is divisible by 4 or 7.

**Idea.** The HackerRank exercise is to fix five lines of a buggy program. The underlying task is a plain walk over the calendar: step one day at a time with the Gregorian leap-year rule, build `x = int(dd + mm + yyyy)` and test it. The bugs in the original are exactly these details: the leap-year rule, the month lengths, the day roll-over, and `or` versus `and` for the divisibility.

**Steps.**
1. Parse both dates; loop from the first to the second.
2. Count the dates whose number is divisible by 4 or 7.

```python
import sys


def leap(y):
    return y % 400 == 0 or (y % 4 == 0 and y % 100 != 0)


def main():
    u, v = sys.stdin.read().split()
    d, m, y = map(int, u.split('-'))
    d2, m2, y2 = map(int, v.split('-'))
    days = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    count = 0
    while True:
        x = int(f"{d:02d}{m:02d}{y:04d}")
        if x % 4 == 0 or x % 7 == 0:
            count += 1
        if (d, m, y) == (d2, m2, y2):
            break
        limit = 29 if m == 2 and leap(y) else days[m]
        d += 1
        if d > limit:
            d = 1
            m += 1
            if m > 12:
                m = 1
                y += 1
    print(count)


main()
```

**Watch out.** "Erasing the leading zeros" only affects how the number is written; `int()` already ignores them. The month keeps its zero padding *inside* the number (`02-08-2025` → `2082025`). The range can span thousands of years, which is a few million iterations of cheap arithmetic.

```stdin
02-08-2025 04-09-2025
```

```stdout
5
```

### Zig Zag Sequence

**Problem.** Rearrange `n` (odd) distinct numbers so that the first `(n+1)/2` increase and the last `(n+1)/2` decrease, choosing the lexicographically smallest such arrangement.

**Idea.** The largest value must sit in the middle. To be lexicographically smallest, the left half takes the smallest values in increasing order, and the rest follow in decreasing order. The fixed version of the HackerRank code does exactly this:
1. Sort.
2. Swap the middle with the last element.
3. Reverse the part after the middle.

The three bugs in the original are the middle index (`(n−1)/2`), the end of the reversed range (`n−2`), and the end pointer moving the wrong way.

**Steps.**
1. Sort; `mid = (n − 1) // 2`; swap `a[mid]` and `a[n−1]`; reverse `a[mid+1 : n−1]`.

```python
def findZigZagSequence(a, n):
    a.sort()
    mid = (n - 1) // 2
    a[mid], a[n - 1] = a[n - 1], a[mid]
    st, ed = mid + 1, n - 2
    while st <= ed:
        a[st], a[ed] = a[ed], a[st]
        st += 1
        ed -= 1
    print(' '.join(map(str, a)))


test_cases = int(input())
for _ in range(test_cases):
    n = int(input())
    a = list(map(int, input().split()))
    findZigZagSequence(a, n)
```

**Watch out.** On HackerRank you may change at most three lines, so the structure of the original loop is kept on purpose. `n = 1` prints the single value.

```stdin
1
7
1 2 3 4 5 6 7
```

```stdout
1 2 3 7 6 5 4
```

### Minimum Operations

**Problem.** Boxes hold red, green and blue balls. One operation moves one ball to another box. Find the fewest operations so that no box holds two colours, or `-1`.

**Idea.** Decide which single colour each box keeps; every other ball in that box must move, and it can always be moved into a box of its own colour. So the cost is (total balls) − (balls that stay). Every colour that exists needs at least one box. A DP over the boxes tracks the **set of colours already given a box** (8 states) and the most balls kept.

**Steps.**
1. `dp[mask]` = most balls kept so far when the colours in `mask` have a box; give each box one colour.
2. `need` = the colours with a positive total. The answer is `total − max dp[mask ⊇ need]`, or `-1` if no such state exists.

```python
import sys


def main():
    data = list(map(int, sys.stdin.read().split()))
    n = data[0]
    boxes = [data[1 + 3 * i:4 + 3 * i] for i in range(n)]
    NEG = -1
    dp = [NEG] * 8
    dp[0] = 0
    for box in boxes:
        nd = [NEG] * 8
        for mask in range(8):
            if dp[mask] < 0:
                continue
            for c in range(3):
                nm = mask | (1 << c)
                nd[nm] = max(nd[nm], dp[mask] + box[c])
        dp = nd
    total = sum(map(sum, boxes))
    need = sum(1 << c for c in range(3) if sum(b[c] for b in boxes) > 0)
    best = max((dp[m] for m in range(8) if m & need == need and dp[m] >= 0), default=-1)
    print(total - best if best >= 0 else -1)


main()
```

**Watch out.** This challenge offers no Python language on HackerRank (only C, C++ and Java), so this is a study solution of the same logic. A colour with zero balls needs no box, which is why only the colours present must be covered.

```stdin
3
1 1 1
1 1 1
1 1 1
```

```stdout
6
```

### Smart Number

**Problem.** A number is "smart" if it has an odd number of divisors. Answer `YES`/`NO` for each query.

**Idea.** Divisors come in pairs `d` and `n/d`, except when `d = n/d`. So the count is odd exactly for perfect squares. The one-line bug in the original is the square test; use the exact integer square root.

**Steps.**
1. `r = isqrt(n)`; print `YES` if `r·r == n`.

```python
from math import isqrt


def is_smart_number(num):
    r = isqrt(num)
    return r * r == num


for _ in range(int(input())):
    num = int(input())
    print('YES' if is_smart_number(num) else 'NO')
```

**Watch out.** `int(math.sqrt(n))` can be off by one for large `n` because of floating-point rounding; `isqrt` is exact.

```stdin
4
1
2
7
169
```

```stdout
YES
NO
NO
YES
```

### XOR Strings

**Problem.** Print the bitwise XOR of two equal-length binary strings.

**Idea.** Characters that differ give `1`, and equal ones give `0`. The bug in the original is the comparison producing the wrong digit.

**Steps.**
1. Zip the two strings and emit `'1'` where they differ.

```python
def strings_xor(s, t):
    return ''.join('1' if a != b else '0' for a, b in zip(s, t))


s = input().strip()
t = input().strip()
print(strings_xor(s, t))
```

**Watch out.** Converting to integers and back with `bin()` would drop leading zeros. Working character by character keeps the full length.

```stdin
10101
00101
```

```stdout
10000
```
