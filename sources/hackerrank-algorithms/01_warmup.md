## Warmup

### Solve Me First

**Problem.** Read two integers `a` and `b` (one per line) and print their sum.

**Idea.** Complete the given function so it returns `a + b`; the starter code already reads the input and prints the result.

**Steps.**
1. Return `a + b` from `solveMeFirst`.
2. The provided code reads both numbers and prints the result.

```python
def solveMeFirst(a, b):
    return a + b


num1 = int(input())
num2 = int(input())
res = solveMeFirst(num1, num2)
print(res)
```

**Watch out.** `input()` returns a string. Without `int()`, `"2" + "3"` would be `"23"`.

```stdin
2
3
```

```stdout
5
```

### Simple Array Sum

**Problem.** Given `n` and an array of `n` integers, return the sum of the elements.

**Idea.** Python's built-in `sum` adds up a list.

**Steps.**
1. Return `sum(ar)`.

```python
import os


def simpleArraySum(ar):
    return sum(ar)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    ar_count = int(input().strip())
    ar = list(map(int, input().rstrip().split()))
    result = simpleArraySum(ar)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** HackerRank function challenges write the answer to `OUTPUT_PATH`, not to the screen. Keep the starter `main` block and just return the value.

```stdin
6
1 2 3 4 10 11
```

```stdout
31
```

### Compare the Triplets

**Problem.** Alice and Bob each have three ratings. For each position, the one with the higher rating gets a point (no point on a tie). Return `[alice_points, bob_points]`.

**Idea.** Walk the two triplets in parallel with `zip` and count wins on each side.

**Steps.**
1. Alice's score = number of positions where `a[i] > b[i]`.
2. Bob's score = number of positions where `a[i] < b[i]`.
3. Return both.

```python
import os


def compareTriplets(a, b):
    alice = sum(x > y for x, y in zip(a, b))
    bob = sum(x < y for x, y in zip(a, b))
    return [alice, bob]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    a = list(map(int, input().rstrip().split()))
    b = list(map(int, input().rstrip().split()))
    result = compareTriplets(a, b)
    fptr.write(' '.join(map(str, result)))
    fptr.write('\n')
    fptr.close()
```

**Watch out.** `True` counts as `1` in `sum`, so `sum(x > y for ...)` counts the wins directly.

```stdin
17 28 30
99 16 8
```

```stdout
2 1
```

### A Very Big Sum

**Problem.** Sum `n` integers, each up to `10^10`.

**Idea.** Python integers have no fixed size, so `sum` never overflows. (In C/C++/Java you'd need a 64-bit `long`.)

**Steps.**
1. Return `sum(ar)`.

```python
import os


def aVeryBigSum(ar):
    return sum(ar)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    ar_count = int(input().strip())
    ar = list(map(int, input().rstrip().split()))
    result = aVeryBigSum(ar)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** The point of this challenge is overflow in other languages. In an interview, mention that 32-bit ints max out around 2.1 billion.

```stdin
5
1000000001 1000000002 1000000003 1000000004 1000000005
```

```stdout
5000000015
```

### Diagonal Difference

**Problem.** For an `n x n` matrix, return the absolute difference between the sums of its two diagonals.

**Idea.** The main diagonal is `arr[i][i]`; the other diagonal is `arr[i][n - 1 - i]`. One loop gets both.

**Steps.**
1. `primary = sum(arr[i][i])`, `secondary = sum(arr[i][n-1-i])` for `i` in `0..n-1`.
2. Return `abs(primary - secondary)`.

```python
import os


def diagonalDifference(arr):
    n = len(arr)
    primary = sum(arr[i][i] for i in range(n))
    secondary = sum(arr[i][n - 1 - i] for i in range(n))
    return abs(primary - secondary)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    arr = []
    for _ in range(n):
        arr.append(list(map(int, input().rstrip().split())))
    result = diagonalDifference(arr)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Return the **absolute** value. The secondary diagonal index is `n - 1 - i`, not `n - i`.

```stdin
3
11 2 4
4 5 6
10 8 -12
```

```stdout
15
```

### Plus Minus

**Problem.** Print the fraction of positive, negative and zero values in an array, each with 6 digits after the decimal point.

**Idea.** Count each group, divide by `n`, and format with `f"{x:.6f}"`.

**Steps.**
1. Count positives, negatives and zeros.
2. Print each count divided by `n` with 6 decimals.

```python
def plusMinus(arr):
    n = len(arr)
    positive = sum(x > 0 for x in arr)
    negative = sum(x < 0 for x in arr)
    zero = n - positive - negative
    for count in (positive, negative, zero):
        print(f"{count / n:.6f}")


if __name__ == '__main__':
    n = int(input().strip())
    arr = list(map(int, input().rstrip().split()))
    plusMinus(arr)
```

**Watch out.** This function **prints** (no `OUTPUT_PATH` in its starter code). `/` is true division in Python 3; in older languages, integer division would give `0`.

```stdin
6
-4 3 -9 0 4 1
```

```stdout
0.500000
0.333333
0.166667
```

### Staircase

**Problem.** Print a right-aligned staircase of `#` of height `n`.

**Idea.** Row `i` (1-based) has `n - i` spaces followed by `i` hashes. `str.rjust` does the padding.

**Steps.**
1. For `i` from 1 to `n`, print `("#" * i).rjust(n)`.

```python
def staircase(n):
    for i in range(1, n + 1):
        print(("#" * i).rjust(n))


if __name__ == '__main__':
    n = int(input().strip())
    staircase(n)
```

**Watch out.** No trailing spaces, and the last row has no leading spaces.

```stdin
6
```

```stdout
     #
    ##
   ###
  ####
 #####
######
```

### Mini-Max Sum

**Problem.** Given five positive integers, print the minimum and maximum sums of exactly four of them.

**Idea.** Leaving out the largest number gives the smallest sum; leaving out the smallest gives the largest sum.

**Steps.**
1. `total = sum(arr)`.
2. Print `total - max(arr)` and `total - min(arr)`.

```python
def miniMaxSum(arr):
    total = sum(arr)
    print(total - max(arr), total - min(arr))


if __name__ == '__main__':
    arr = list(map(int, input().rstrip().split()))
    miniMaxSum(arr)
```

**Watch out.** The sums can exceed 32-bit range (values up to `10^9`). Fine in Python; use `long` in Java/C++.

```stdin
1 2 3 4 5
```

```stdout
10 14
```

### Birthday Cake Candles

**Problem.** Count how many candles have the maximum height.

**Idea.** Find the maximum, then count how often it appears.

**Steps.**
1. `tallest = max(candles)`.
2. Return `candles.count(tallest)`.

```python
import os


def birthdayCakeCandles(candles):
    return candles.count(max(candles))


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    candles_count = int(input().strip())
    candles = list(map(int, input().rstrip().split()))
    result = birthdayCakeCandles(candles)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Two passes are still O(n). A single pass works too: reset the count when you see a new maximum.

```stdin
4
3 2 1 3
```

```stdout
2
```

### Time Conversion

**Problem.** Convert a 12-hour time like `07:05:45PM` to 24-hour time (`19:05:45`).

**Idea.** Only the hour changes: `12 AM` becomes `00`, `1–11 PM` add 12, `12 PM` stays `12`. `hour % 12` handles the 12 case for both AM and PM.

**Steps.**
1. Split into `hh`, the middle `:mm:ss`, and the `AM`/`PM` suffix.
2. `hour = int(hh) % 12`, then add 12 if it's `PM`.
3. Return the hour padded to two digits plus the rest.

```python
import os


def timeConversion(s):
    hour = int(s[:2]) % 12
    if s[-2:] == "PM":
        hour += 12
    return f"{hour:02d}{s[2:-2]}"


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    s = input()
    result = timeConversion(s)
    fptr.write(result + '\n')
    fptr.close()
```

**Watch out.** The two edge cases are `12:xx:xxAM` → `00:xx:xx` and `12:xx:xxPM` → `12:xx:xx`. `% 12` covers both.

```stdin
07:05:45PM
```

```stdout
19:05:45
```
