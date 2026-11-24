## Heap

### QHEAP1

**Problem.** Support insert, delete a given value, and print the minimum.

**Idea.** Use a binary heap with **lazy deletion**. A delete only records the value in a "to delete" counter. When the minimum is asked for, pop the heap top while it is marked deleted. Each value is pushed and popped once, so this is O(log n) amortised.

**Steps.**
1. Type 1: push. Type 2: `dead[v] += 1`. Type 3: clean the top, then print it.

```python
import heapq
import sys


def main():
    data = sys.stdin.read().split()
    q = int(data[0])
    heap = []
    dead = {}
    out = []
    pos = 1
    for _ in range(q):
        t = data[pos]
        if t == '3':
            pos += 1
            while dead.get(heap[0], 0):
                dead[heap[0]] -= 1
                heapq.heappop(heap)
            out.append(heap[0])
        else:
            v = int(data[pos + 1])
            pos += 2
            if t == '1':
                heapq.heappush(heap, v)
            else:
                dead[v] = dead.get(v, 0) + 1
    print('\n'.join(map(str, out)))


main()
```

**Watch out.** `list.remove` followed by `heapify` is O(n) per delete. Lazy deletion keeps deletes O(1) and pays only when the dead value reaches the top.

```stdin
5
1 4
1 9
3
2 4
3
```

```stdout
4
9
```

### Jesse and Cookies

**Problem.** Repeatedly combine the two least sweet cookies into `least + 2·second` until every cookie is at least `k`. Print the number of operations, or `-1`.

**Idea.** A min-heap gives the two smallest cookies in O(log n). Stop when the smallest is `≥ k`, or report `-1` when fewer than two cookies remain and the last one is still too small.

**Steps.**
1. Heapify; while `heap[0] < k`: if only one cookie is left, return `-1`; otherwise pop two, push the mix, and count.

```python
import heapq
import os


def cookies(k, A):
    heapq.heapify(A)
    ops = 0
    while A[0] < k:
        if len(A) < 2:
            return -1
        a = heapq.heappop(A)
        b = heapq.heappop(A)
        heapq.heappush(A, a + 2 * b)
        ops += 1
    return ops


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    A = list(map(int, input().rstrip().split()))
    fptr.write(str(cookies(k, A)) + '\n')
    fptr.close()
```

**Watch out.** Re-sorting the list after every operation is O(n log n) each time; the heap is O(log n).

```stdin
6 7
1 2 3 9 10 12
```

```stdout
2
```

### Find the Running Median

**Problem.** After each number arrives, print the median of the numbers so far (one decimal place).

**Idea.** Use **two heaps**: a max-heap `low` holding the smaller half (stored negated) and a min-heap `high` holding the larger half. Keep `len(low)` equal to `len(high)` or one more. The median is then `low`'s top, or the average of both tops.

**Steps.**
1. Push into `low`, move `low`'s top into `high`, and rebalance if `high` became bigger.
2. Print with one decimal.

```python
import heapq
import sys


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    low, high = [], []
    out = []
    for x in map(int, data[1:1 + n]):
        heapq.heappush(low, -x)
        heapq.heappush(high, -heapq.heappop(low))
        if len(high) > len(low):
            heapq.heappush(low, -heapq.heappop(high))
        if len(low) > len(high):
            out.append(f"{-low[0]:.1f}")
        else:
            out.append(f"{(-low[0] + high[0]) / 2:.1f}")
    print('\n'.join(out))


main()
```

**Watch out.** Passing every element through `high` before possibly moving it back guarantees that every value in `low` is `≤` every value in `high`, with no extra comparisons.

```stdin
6
12
4
5
3
8
7
```

```stdout
12.0
8.0
5.0
4.5
5.0
6.0
```

### Minimum Average Waiting Time

**Problem.** One cook serves pizza orders that arrive at given times with given cooking times, without preemption. Minimise the average waiting time (completion time − arrival) and print its integer part.

**Idea.** **Shortest job first among the arrived orders.**
- Sort the orders by arrival time.
- When the cook is free, push every arrived order into a min-heap keyed by cooking time and serve the shortest.
- If nothing has arrived, jump the clock to the next arrival.

**Steps.**
1. Sort; loop: move the arrivals up to the current time into the heap; pop the shortest; advance the time; add the wait.

```python
import heapq
import os


def minimumAverage(customers):
    customers.sort()
    heap = []
    t = 0
    i = 0
    n = len(customers)
    total = 0
    while i < n or heap:
        if not heap and customers[i][0] > t:
            t = customers[i][0]
        while i < n and customers[i][0] <= t:
            heapq.heappush(heap, (customers[i][1], customers[i][0]))
            i += 1
        cook, arrive = heapq.heappop(heap)
        t += cook
        total += t - arrive
    return total // n


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    customers = [list(map(int, input().rstrip().split())) for _ in range(n)]
    fptr.write(str(minimumAverage(customers)) + '\n')
    fptr.close()
```

**Watch out.** Use integer floor division for the average; float division can round up on huge totals. The clock jump avoids waiting step by step during idle gaps.

```stdin
3
0 3
1 9
2 6
```

```stdout
9
```
