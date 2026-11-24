## Sorting

### Big Sorting

**Problem.** Sort numeric strings (up to 10⁶ digits each) by their integer value.

**Idea.** Without leading zeros, a longer number is always bigger; numbers of equal length compare like strings. So sort by `(length, string)`, with no conversion to `int`.

**Steps.**
1. Return `sorted(unsorted, key=lambda s: (len(s), s))`.

```python
import os


def bigSorting(unsorted):
    return sorted(unsorted, key=lambda s: (len(s), s))


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    unsorted = [input() for _ in range(n)]
    result = bigSorting(unsorted)
    fptr.write('\n'.join(result))
    fptr.write('\n')
    fptr.close()
```

**Watch out.** Converting million-digit strings with `int()` is very slow (and capped by Python's digit limit since 3.11). Plain string sorting is wrong: `"10" < "3"`.

```stdin
6
31415926535897932384626433832795
1
3
10
3
5
```

```stdout
1
3
3
5
10
31415926535897932384626433832795
```

### Intro to Tutorial Challenges

**Problem.** Return the index of value `V` in a sorted array.

**Idea.** The array is sorted, so binary search finds it in O(log n). `bisect_left` does exactly that.

**Steps.**
1. Return `bisect_left(arr, V)`.

```python
import os
from bisect import bisect_left


def introTutorial(V, arr):
    return bisect_left(arr, V)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    V = int(input().strip())
    n = int(input().strip())
    arr = list(map(int, input().rstrip().split()))
    result = introTutorial(V, arr)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** `arr.index(V)` also works (O(n)); mention binary search because the array is sorted.

```stdin
4
6
1 4 5 7 9 12
```

```stdout
1
```

### Insertion Sort - Part 1

**Problem.** The array is sorted except for its last element `e`. Insert `e` by shifting larger elements right one at a time, printing the array after every shift and after the final insertion.

**Idea.** Walk left from the end; while the element is bigger than `e`, copy it one cell right (and print). Then place `e` (and print).

**Steps.**
1. `e = arr[-1]`, `i = n - 2`.
2. While `i >= 0` and `arr[i] > e`: `arr[i + 1] = arr[i]`, print, `i -= 1`.
3. `arr[i + 1] = e`, print.

```python
def insertionSort1(n, arr):
    e = arr[-1]
    i = n - 2
    while i >= 0 and arr[i] > e:
        arr[i + 1] = arr[i]
        print(*arr)
        i -= 1
    arr[i + 1] = e
    print(*arr)


if __name__ == '__main__':
    n = int(input().strip())
    arr = list(map(int, input().rstrip().split()))
    insertionSort1(n, arr)
```

**Watch out.** When `e` is smaller than everything, the loop ends at `i = -1` and `e` goes to index 0.

```stdin
5
2 4 6 8 3
```

```stdout
2 4 6 8 8
2 4 6 6 8
2 4 4 6 8
2 3 4 6 8
```

### Insertion Sort - Part 2

**Problem.** Run a full insertion sort and print the array after each element (from the second one) has been inserted.

**Idea.** For `i = 1 .. n-1`, insert `arr[i]` into the sorted prefix `arr[:i]` by shifting, then print.

**Steps.**
1. For each `i` from 1: save `key = arr[i]`, shift bigger elements of the prefix right, put `key` in place.
2. Print the array.

```python
def insertionSort2(n, arr):
    for i in range(1, n):
        key, j = arr[i], i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
        print(*arr)


if __name__ == '__main__':
    n = int(input().strip())
    arr = list(map(int, input().rstrip().split()))
    insertionSort2(n, arr)
```

**Watch out.** Print once per outer iteration, even when nothing moved.

```stdin
6
1 4 3 5 6 2
```

```stdout
1 4 3 5 6 2
1 3 4 5 6 2
1 3 4 5 6 2
1 3 4 5 6 2
1 2 3 4 5 6
```

### Correctness and the Loop Invariant

**Problem.** The given insertion sort has a bug. Fix it.

**Idea.** The inner loop condition `j > 0` never compares with index 0, so the first element can't move. The invariant "`l[0..i-1]` is sorted" needs the loop to go down to `j >= 0`.

**Steps.**
1. Change `while (j > 0)` to `while (j >= 0)`.

```python
def insertion_sort(l):
    for i in range(1, len(l)):
        j = i - 1
        key = l[i]
        while (j >= 0) and (l[j] > key):
            l[j + 1] = l[j]
            j -= 1
        l[j + 1] = key


m = int(input().strip())
ar = [int(i) for i in input().strip().split()]
insertion_sort(ar)
print(" ".join(map(str, ar)))
```

**Watch out.** Loop invariants are how you prove sorting code correct: true before the loop (initialization), kept by each iteration (maintenance), and useful at the end (termination).

```stdin
6
7 4 3 5 6 2
```

```stdout
2 3 4 5 6 7
```

### Running Time of Algorithms

**Problem.** Count the number of shifts insertion sort makes on the array.

**Idea.** Each shift moves one bigger element past a smaller one, so the number of shifts equals the number of **inversions**. With `n ≤ 1001`, simulating is fine.

**Steps.**
1. Run insertion sort and count every shift.

```python
import os


def runningTime(arr):
    arr = arr[:]
    shifts = 0
    for i in range(1, len(arr)):
        key, j = arr[i], i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
            shifts += 1
        arr[j + 1] = key
    return shifts


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    arr = list(map(int, input().rstrip().split()))
    result = runningTime(arr)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Equal elements don't shift (`>`, not `>=`), which keeps insertion sort stable.

```stdin
5
2 1 3 1 2
```

```stdout
4
```

### Quicksort 1 - Partition

**Problem.** Partition the array around its first element `p`: elements smaller than `p`, then `p`, then larger ones, each group keeping its original order.

**Idea.** One pass that sends each element to `left`, `equal` or `right`.

**Steps.**
1. Return `[x < p] + [x == p] + [x > p]` in order.

```python
import os


def quickSort(arr):
    p = arr[0]
    return [x for x in arr if x < p] + [x for x in arr if x == p] + [x for x in arr if x > p]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    arr = list(map(int, input().rstrip().split()))
    result = quickSort(arr)
    fptr.write(' '.join(map(str, result)))
    fptr.write('\n')
    fptr.close()
```

**Watch out.** This version is stable but uses extra memory. The in-place (Lomuto/Hoare) partition uses O(1) extra space but reorders the groups.

```stdin
5
4 5 3 7 2
```

```stdout
3 2 4 5 7
```

### Counting Sort 1

**Problem.** Values are in `0..99`. Return how many times each value appears.

**Idea.** A list of 100 counters indexed by value.

**Steps.**
1. `counts = [0] * 100`; increment `counts[x]` for each `x`.

```python
import os


def countingSort(arr):
    counts = [0] * 100
    for x in arr:
        counts[x] += 1
    return counts


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    arr = list(map(int, input().rstrip().split()))
    result = countingSort(arr)
    fptr.write(' '.join(map(str, result)))
    fptr.write('\n')
    fptr.close()
```

**Watch out.** The output always has 100 numbers, including zeros for values that never appear.

```stdin
100
63 25 73 1 98 73 56 84 86 57 16 83 8 25 81 56 9 53 98 67 99 12 83 89 80 91 39 86 76 85 74 39 25 90 59 10 94 32 44 3 89 30 27 79 46 96 27 32 18 21 92 69 81 40 40 34 68 78 24 87 42 69 23 41 78 22 6 90 99 89 50 30 20 1 43 3 70 95 33 46 44 9 69 48 33 60 65 16 82 67 61 32 21 79 75 75 13 87 70 33
```

```stdout
0 2 0 2 0 0 1 0 1 2 1 0 1 1 0 0 2 0 1 0 1 2 1 1 1 3 0 2 0 0 2 0 3 3 1 0 0 0 0 2 2 1 1 1 2 0 2 0 1 0 1 0 0 1 0 0 2 1 0 1 1 1 0 1 0 1 0 2 1 3 2 0 0 2 1 2 1 0 2 2 1 2 1 2 1 1 2 2 0 3 2 1 1 0 1 1 1 0 2 2
```

### Counting Sort 2

**Problem.** Sort integers in `0..99` with counting sort.

**Idea.** Count each value, then output each value as many times as it was counted, in increasing order. O(n + 100), no comparisons.

**Steps.**
1. Count occurrences.
2. Return `[v] * counts[v]` for `v = 0..99`, concatenated.

```python
import os


def countingSort(arr):
    counts = [0] * 100
    for x in arr:
        counts[x] += 1
    return [v for v in range(100) for _ in range(counts[v])]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    arr = list(map(int, input().rstrip().split()))
    result = countingSort(arr)
    fptr.write(' '.join(map(str, result)))
    fptr.write('\n')
    fptr.close()
```

**Watch out.** Counting sort beats the O(n log n) comparison-sort bound because it uses the small value range instead of comparisons.

```stdin
100
63 25 73 1 98 73 56 84 86 57 16 83 8 25 81 56 9 53 98 67 99 12 83 89 80 91 39 86 76 85 74 39 25 90 59 10 94 32 44 3 89 30 27 79 46 96 27 32 18 21 92 69 81 40 40 34 68 78 24 87 42 69 23 41 78 22 6 90 99 89 50 30 20 1 43 3 70 95 33 46 44 9 69 48 33 60 65 16 82 67 61 32 21 79 75 75 13 87 70 33
```

```stdout
1 1 3 3 6 8 9 9 10 12 13 16 16 18 20 21 21 22 23 24 25 25 25 27 27 30 30 32 32 32 33 33 33 34 39 39 40 40 41 42 43 44 44 46 46 48 50 53 56 56 57 59 60 61 63 65 67 67 68 69 69 69 70 70 73 73 74 75 75 76 78 78 79 79 80 81 81 82 83 83 84 85 86 86 87 87 89 89 89 90 90 91 92 94 95 96 98 98 99 99
```

### The Full Counting Sort

**Problem.** Stable-sort `(key, string)` pairs by key (`0..99`), replacing the strings in the first half of the input with `-`. Print all strings on one line.

**Idea.** One bucket (list) per key. Appending in input order keeps the sort stable.

**Steps.**
1. For each pair `i`, append `-` (if `i < n/2`) or the string to `buckets[key]`.
2. Print all buckets in key order, joined by spaces.

```python
def countSort(arr):
    half = len(arr) // 2
    buckets = [[] for _ in range(100)]
    for i, (key, text) in enumerate(arr):
        buckets[int(key)].append("-" if i < half else text)
    print(" ".join(word for bucket in buckets for word in bucket))


if __name__ == '__main__':
    n = int(input().strip())
    arr = [input().rstrip().split() for _ in range(n)]
    countSort(arr)
```

**Watch out.** With up to 10⁶ lines, build the output with one `join` and a single `print`; printing word by word is too slow.

```stdin
20
0 ab
6 cd
0 ef
6 gh
4 ij
0 ab
6 cd
0 ef
6 gh
0 ij
4 that
3 be
0 to
1 be
5 question
1 or
2 not
4 is
2 to
4 the
```

```stdout
- - - - - to be or not to be - that is the question - - - -
```

### Closest Numbers

**Problem.** Return all pairs of elements with the smallest absolute difference (flattened, in sorted order).

**Idea.** After sorting, the closest pair is always between neighbours. Find the minimum neighbour gap, then output every neighbour pair with that gap.

**Steps.**
1. Sort.
2. `best = min(b - a)` over neighbours.
3. Return the pairs with `b - a == best`, flattened.

```python
import os


def closestNumbers(arr):
    arr = sorted(arr)
    best = min(b - a for a, b in zip(arr, arr[1:]))
    return [x for a, b in zip(arr, arr[1:]) if b - a == best for x in (a, b)]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    arr = list(map(int, input().rstrip().split()))
    result = closestNumbers(arr)
    fptr.write(' '.join(map(str, result)))
    fptr.write('\n')
    fptr.close()
```

**Watch out.** Comparing all pairs is O(n²) for n = 200,000; the sort-then-neighbours idea is O(n log n).

```stdin
10
-20 -3916237 -357920 -3620601 7374819 -7330761 30 6246457 -6461594 266854
```

```stdout
-20 30
```

### Find the Median

**Problem.** Return the median of an odd-length array.

**Idea.** Sort and take the middle element.

**Steps.**
1. Return `sorted(arr)[len(arr) // 2]`.

```python
import os


def findMedian(arr):
    return sorted(arr)[len(arr) // 2]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    arr = list(map(int, input().rstrip().split()))
    result = findMedian(arr)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Quickselect finds the median in expected O(n) without fully sorting; worth mentioning in an interview.

```stdin
7
0 1 2 4 6 5 3
```

```stdout
3
```

### Insertion Sort Advanced Analysis

**Problem.** Count the shifts insertion sort would make, for arrays up to 10⁵ elements.

**Idea.** Shifts = inversions (pairs `i < j` with `a[i] > a[j]`). Count them in O(n log n) with a Fenwick tree: process elements left to right and count how many earlier elements are strictly greater.

**Steps.**
1. Compress values to ranks `1..m`.
2. For each element: inversions += (elements seen so far) − (seen elements `<=` it); then add it to the tree.

```python
import os


def insertionSort(arr):
    ranks = {v: i + 1 for i, v in enumerate(sorted(set(arr)))}
    tree = [0] * (len(ranks) + 1)
    inversions = 0
    for seen, v in enumerate(arr):
        r = ranks[v]
        not_greater, i = 0, r
        while i > 0:
            not_greater += tree[i]
            i -= i & -i
        inversions += seen - not_greater
        while r < len(tree):
            tree[r] += 1
            r += r & -r
    return inversions


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n = int(input().strip())
        arr = list(map(int, input().rstrip().split()))
        fptr.write(str(insertionSort(arr)) + '\n')
    fptr.close()
```

**Watch out.** Equal values are not inversions, so count only strictly greater earlier elements. A merge-sort count is the other standard O(n log n) approach.

```stdin
2
5
1 1 1 2 2
5
2 1 3 1 2
```

```stdout
0
4
```

### Fraudulent Activity Notifications

**Problem.** On each day after the first `d`, send a notice if spending is at least twice the median of the previous `d` days. Count the notices.

**Idea.** Spending is in `0..200`, so keep a count array for the sliding window. The median is found by walking the cumulative counts (at most 201 steps), and updating the window is O(1).

**Steps.**
1. Count the first `d` values.
2. For each later day: find the median (one or two middle values) from the counts; compare `spend >= 2 * median`.
3. Add today's value and remove the value leaving the window.

```python
import os


def activityNotifications(expenditure, d):
    counts = [0] * 201
    for x in expenditure[:d]:
        counts[x] += 1

    def kth(k):
        total = 0
        for v, c in enumerate(counts):
            total += c
            if total >= k:
                return v

    notices = 0
    for i in range(d, len(expenditure)):
        if d % 2:
            double_median = 2 * kth(d // 2 + 1)
        else:
            double_median = kth(d // 2) + kth(d // 2 + 1)
        if expenditure[i] >= double_median:
            notices += 1
        counts[expenditure[i]] += 1
        counts[expenditure[i - d]] -= 1
    return notices


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, d = map(int, input().split())
    expenditure = list(map(int, input().rstrip().split()))
    result = activityNotifications(expenditure, d)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Compare with **twice** the median as an integer (`kth(a) + kth(b)` for even `d`) to avoid float halves.

```stdin
9 5
2 3 4 2 3 6 8 4 5
```

```stdout
2
```

### Lily's Homework

**Problem.** The sum of `|a[i] - a[i-1]|` is minimal when the array is sorted (ascending or descending). Return the minimum number of swaps to reach either.

**Idea.** Minimum swaps to reach a target order = `n − (number of cycles)` in the permutation that maps each element to its target position. Compute it for ascending and descending order and take the smaller.

**Steps.**
1. `pos[v]` = target index of `v` in the sorted order.
2. Count cycles of `i → pos[arr[i]]`; swaps = `n − cycles`.
3. Do it for both orders; return the minimum.

```python
import os


def lilysHomework(arr):
    def swaps(target):
        pos = {v: i for i, v in enumerate(target)}
        seen = [False] * len(arr)
        cycles = 0
        for i in range(len(arr)):
            if not seen[i]:
                cycles += 1
                j = i
                while not seen[j]:
                    seen[j] = True
                    j = pos[arr[j]]
        return len(arr) - cycles

    ascending = sorted(arr)
    return min(swaps(ascending), swaps(ascending[::-1]))


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    arr = list(map(int, input().rstrip().split()))
    result = lilysHomework(arr)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Don't forget the descending order; it can need fewer swaps (`[3, 4, 2, 5, 1]`).

```stdin
4
2 5 3 1
```

```stdout
2
```
