## Arrays

### Arrays - DS

**Problem.** Print the array in reverse order.

**Idea.** Slicing with step `−1` builds the reversed list in one pass.

**Steps.**
1. Return `a[::-1]`.

```python
import os


def reverseArray(a):
    return a[::-1]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    arr_count = int(input().strip())
    arr = list(map(int, input().rstrip().split()))
    fptr.write(' '.join(map(str, reverseArray(arr))) + '\n')
    fptr.close()
```

**Watch out.** `a.reverse()` reverses in place and returns `None`, a classic slip when the function must *return* the list.

```stdin
4
1 4 3 2
```

```stdout
2 3 4 1
```

### 2D Array - DS

**Problem.** In a 6×6 grid, find the largest "hourglass" sum (three cells on top, the middle one, three on the bottom).

**Idea.** There are only 16 hourglasses (top-left corner at rows and columns 0..3). Sum each one directly and take the maximum.

**Steps.**
1. For each corner `(i, j)` in `0..3`, add the 7 cells; keep the maximum.

```python
import os


def hourglassSum(arr):
    best = None
    for i in range(4):
        for j in range(4):
            s = sum(arr[i][j:j + 3]) + arr[i + 1][j + 1] + sum(arr[i + 2][j:j + 3])
            if best is None or s > best:
                best = s
    return best


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    arr = [list(map(int, input().rstrip().split())) for _ in range(6)]
    fptr.write(str(hourglassSum(arr)) + '\n')
    fptr.close()
```

**Watch out.** Values can be negative (down to −9), so do not start the maximum at 0: an all-negative grid would wrongly print 0.

```stdin
1 1 1 0 0 0
0 1 0 0 0 0
1 1 1 0 0 0
0 0 2 4 4 0
0 0 0 2 0 0
0 0 1 2 4 0
```

```stdout
19
```

### Dynamic Array

**Problem.** Keep `n` lists and a value `lastAnswer = 0`. Query `1 x y` appends `y` to list `(x ⊕ lastAnswer) mod n`. Query `2 x y` sets `lastAnswer` to element `y mod size` of that list and records it.

**Idea.** A direct simulation; the only trick is to compute the list index with the current `lastAnswer` each time.

**Steps.**
1. `idx = (x ^ last) % n`; append for type 1; for type 2, read `arr[idx][y % len]`, store it and record it.

```python
import os


def dynamicArray(n, queries):
    arr = [[] for _ in range(n)]
    last = 0
    out = []
    for t, x, y in queries:
        idx = (x ^ last) % n
        if t == 1:
            arr[idx].append(y)
        else:
            last = arr[idx][y % len(arr[idx])]
            out.append(last)
    return out


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, q = map(int, input().split())
    queries = [list(map(int, input().rstrip().split())) for _ in range(q)]
    fptr.write('\n'.join(map(str, dynamicArray(n, queries))) + '\n')
    fptr.close()
```

**Watch out.** It is XOR (`^`), not exponentiation, and the index uses the *updated* `lastAnswer` from earlier type-2 queries.

```stdin
2 5
1 0 5
1 1 7
1 0 3
2 1 0
2 1 1
```

```stdout
7
3
```

### Left Rotation

**Problem.** Rotate an array left by `d` positions.

**Idea.** The rotated array is the suffix starting at `d` followed by the prefix. Take `d mod n` in case `d ≥ n`.

**Steps.**
1. `d %= n`; return `arr[d:] + arr[:d]`.

```python
import os


def rotateLeft(d, arr):
    d %= len(arr)
    return arr[d:] + arr[:d]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, d = map(int, input().split())
    arr = list(map(int, input().rstrip().split()))
    fptr.write(' '.join(map(str, rotateLeft(d, arr))) + '\n')
    fptr.close()
```

**Watch out.** Rotating one step at a time `d` times is O(n·d), which is too slow at the limits; slicing is O(n).

```stdin
5 4
1 2 3 4 5
```

```stdout
5 1 2 3 4
```

### Sparse Arrays

**Problem.** For each query string, count how many times it occurs in the input list.

**Idea.** Count the list once with a dictionary (`Counter`); each query is then an O(1) lookup that defaults to 0.

**Steps.**
1. `c = Counter(stringList)`; answer `c[q]` for each query.

```python
import os
from collections import Counter


def matchingStrings(stringList, queries):
    c = Counter(stringList)
    return [c[q] for q in queries]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    strings = [input().strip() for _ in range(int(input().strip()))]
    queries = [input().strip() for _ in range(int(input().strip()))]
    fptr.write('\n'.join(map(str, matchingStrings(strings, queries))) + '\n')
    fptr.close()
```

**Watch out.** Stripping the input lines avoids stray `\r` or spaces making equal strings look different.

```stdin
4
aba
baba
aba
xzxb
3
aba
xzxb
ab
```

```stdout
2
1
0
```

### Array Manipulation

**Problem.** Start with `n` zeros. Each of `m` operations adds `k` to positions `a..b`. Print the maximum value at the end.

**Idea.** Use a **difference array**: add `k` at `a` and subtract it at `b + 1`. The running prefix sum then reconstructs every value, so the maximum prefix sum is the answer. This is O(n + m) instead of O(n·m).

**Steps.**
1. `diff[a] += k`, `diff[b+1] −= k` for each operation.
2. Scan the prefix sums and keep the maximum.

```python
import os


def arrayManipulation(n, queries):
    diff = [0] * (n + 2)
    for a, b, k in queries:
        diff[a] += k
        diff[b + 1] -= k
    best = cur = 0
    for v in diff:
        cur += v
        if cur > best:
            best = cur
    return best


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m = map(int, input().split())
    queries = [list(map(int, input().rstrip().split())) for _ in range(m)]
    fptr.write(str(arrayManipulation(n, queries)) + '\n')
    fptr.close()
```

**Watch out.** Positions are 1-based, so the array needs `n + 2` slots for the `b + 1` update. The totals can exceed 32 bits in other languages; Python integers are unbounded.

```stdin
5 3
1 2 100
2 5 100
3 4 100
```

```stdout
200
```
