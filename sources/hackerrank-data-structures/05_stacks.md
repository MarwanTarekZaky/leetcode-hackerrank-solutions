## Stacks

### Maximum Element

**Problem.** Support push, pop and "print the maximum" on a stack.

**Idea.** Push the **running maximum** alongside the stack: each entry stores `max(x, current max)`. Popping restores the previous maximum automatically, so every operation is O(1).

**Steps.**
1. Type 1: push `max(x, top)`. Type 2: pop. Type 3: report the top.

```python
import os


def getMax(operations):
    st = []
    out = []
    for op in operations:
        parts = op.split()
        if parts[0] == '1':
            x = int(parts[1])
            st.append(max(x, st[-1]) if st else x)
        elif parts[0] == '2':
            st.pop()
        else:
            out.append(st[-1])
    return out


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    ops = [input() for _ in range(n)]
    fptr.write('\n'.join(map(str, getMax(ops))) + '\n')
    fptr.close()
```

**Watch out.** Scanning the whole stack for each type-3 query is O(n) per query and too slow for 10⁵ operations.

```stdin
10
1 97
2
1 20
2
1 26
1 20
2
3
1 91
3
```

```stdout
26
91
```

### Balanced Brackets

**Problem.** Decide whether each string of `()[]{}` is balanced.

**Idea.** Push the opening brackets. Each closing bracket must match the most recent unmatched opening one, which is the top of the stack. At the end the stack must be empty.

**Steps.**
1. For each character: push openers; for a closer, pop and compare (an empty stack is a failure).
2. `YES` if all matched and the stack is empty.

```python
import os


def isBalanced(s):
    pairs = {')': '(', ']': '[', '}': '{'}
    st = []
    for ch in s:
        if ch in '([{':
            st.append(ch)
        elif not st or st.pop() != pairs[ch]:
            return 'NO'
    return 'YES' if not st else 'NO'


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        fptr.write(isBalanced(input().strip()) + '\n')
    fptr.close()
```

**Watch out.** Counting brackets of each type is not enough: `{[(])}` has equal counts but crosses its pairs.

```stdin
3
{[()]}
{[(])}
{{[[(())]]}}
```

```stdout
YES
NO
YES
```

### Equal Stacks

**Problem.** Remove cylinders from the tops of three stacks so that all three have the same height, as large as possible.

**Idea.** The reachable heights of a stack are its suffix sums, read from the bottom. So the answer is the largest height that appears in all three sets of suffix sums.

**Steps.**
1. Build the set of suffix sums for each stack (including 0).
2. Print the maximum of their intersection.

```python
import os
from itertools import accumulate


def equalStacks(h1, h2, h3):
    sets = [set(accumulate(reversed(h))) | {0} for h in (h1, h2, h3)]
    return max(sets[0] & sets[1] & sets[2])


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    input()
    h1 = list(map(int, input().rstrip().split()))
    h2 = list(map(int, input().rstrip().split()))
    h3 = list(map(int, input().rstrip().split()))
    fptr.write(str(equalStacks(h1, h2, h3)) + '\n')
    fptr.close()
```

**Watch out.** The first element of each list is the **top** of the stack, so the sums are built from the end of the list. Height 0 (everything removed) is always possible.

```stdin
5 3 4
3 2 1 1 1
4 3 2
1 1 4 1
```

```stdout
5
```

### Game of Two Stacks

**Problem.** Take numbers from the tops of two stacks while the running sum stays `≤ maxSum`. Maximise how many numbers are taken.

**Idea.** Any valid play takes some prefix of `a` and some prefix of `b`. Use **two pointers**:
1. Take as many from `a` as fit.
2. Add elements of `b` one at a time, dropping elements from the end of the `a`-prefix whenever the sum overflows.
3. Track the best total count.

**Steps.**
1. Greedy prefix of `a`; then extend `b`, retreating in `a` while the sum is too large.

```python
import os


def twoStacks(maxSum, a, b):
    total = 0
    i = 0
    while i < len(a) and total + a[i] <= maxSum:
        total += a[i]
        i += 1
    best = i
    j = 0
    while j < len(b):
        total += b[j]
        j += 1
        while total > maxSum and i > 0:
            i -= 1
            total -= a[i]
        if total > maxSum:
            break
        best = max(best, i + j)
    return best


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    g = int(input().strip())
    for _ in range(g):
        n, m, maxSum = map(int, input().split())
        a = list(map(int, input().rstrip().split()))
        b = list(map(int, input().rstrip().split()))
        fptr.write(str(twoStacks(maxSum, a, b)) + '\n')
    fptr.close()
```

**Watch out.** Greedily picking the smaller top each time fails. A large element at the top of one stack may hide many small ones beneath it, and only the prefix enumeration accounts for that.

```stdin
1
5 4 10
4 2 4 6 1
2 1 8 5
```

```stdout
4
```

### Largest Rectangle

**Problem.** In a histogram, find the area of the largest rectangle made of consecutive bars.

**Idea.** Keep a **monotonic stack** of increasing heights. When a lower bar arrives, every taller bar on the stack has found its right boundary. Its left boundary is the element below it on the stack, so pop it and compute its area. A sentinel bar of height 0 at the end flushes the stack.

**Steps.**
1. For `i` over the heights plus a final 0: while the top is higher than `h[i]`, pop it with width `i − (new top) − 1`.
2. Push `i`; keep the maximum area.

```python
import os


def largestRectangle(h):
    st = []
    best = 0
    for i, x in enumerate(h + [0]):
        while st and h[st[-1]] >= x:
            top = st.pop()
            left = st[-1] if st else -1
            best = max(best, h[top] * (i - left - 1))
        st.append(i)
    return best


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    h = list(map(int, input().rstrip().split()))
    fptr.write(str(largestRectangle(h)) + '\n')
    fptr.close()
```

**Watch out.** Popping on `>=` (not just `>`) is fine. An equal bar finds its area again later from the surviving index, which has the same height and a wider span.

```stdin
5
1 2 3 4 5
```

```stdout
9
```

### Simple Text Editor

**Problem.** Support append, delete the last `k` characters, print the `k`-th character, and undo of the last append or delete.

**Idea.** Keep the text as a **list of characters** (a stack) plus an undo log. An append logs how many characters it added, and a delete logs the removed characters. Undo applies the inverse. Every operation costs only the size of its own change, never a copy of the whole text.

**Steps.**
1. Type 1: extend and log `('del', len(w))`. Type 2: cut `k` characters and log `('add', removed)`.
2. Type 3: print `text[k−1]`. Type 4: pop the log and apply it.

```python
import sys


def main():
    data = sys.stdin.read().split('\n')
    q = int(data[0])
    text = []
    log = []
    out = []
    for line in data[1:1 + q]:
        parts = line.split()
        t = parts[0]
        if t == '1':
            w = parts[1]
            text.extend(w)
            log.append(('del', len(w)))
        elif t == '2':
            k = int(parts[1])
            removed = text[-k:]
            del text[-k:]
            log.append(('add', removed))
        elif t == '3':
            out.append(text[int(parts[1]) - 1])
        else:
            kind, val = log.pop()
            if kind == 'del':
                del text[-val:]
            else:
                text.extend(val)
    print('\n'.join(out))


main()
```

**Watch out.** Storing a full copy of the text for every undo is O(total length) per operation and too slow at 10⁶ operations. Undo never undoes another undo, so the log is a plain stack.

```stdin
8
1 abc
3 3
2 3
1 xy
3 2
4
4
3 1
```

```stdout
c
y
a
```

### Poisonous Plants

**Problem.** Each day, every plant with more pesticide than its left neighbour dies (all at once). After how many days do deaths stop?

**Idea.** A plant dies on day `1 + max(days of the plants between it and its nearest smaller-or-equal plant to the left)`. The plants in between die before it and "shield" it until they are gone. Use a monotonic stack of `(value, death day)`: pop while the top is `≥` the current value, tracking the largest death day popped.
- If the stack empties, the plant never dies (day 0).
- Otherwise it dies on that maximum `+ 1`.

**Steps.**
1. Sweep left to right with the stack; the answer is the largest death day.

```python
import os


def poisonousPlants(p):
    st = []                                      # (value, day it dies)
    best = 0
    for x in p:
        day = 0
        while st and st[-1][0] >= x:
            day = max(day, st.pop()[1])
        day = day + 1 if st else 0
        best = max(best, day)
        st.append((x, day))
    return best


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    p = list(map(int, input().rstrip().split()))
    fptr.write(str(poisonousPlants(p)) + '\n')
    fptr.close()
```

**Watch out.** Simulating day by day is O(n²) on inputs like a decreasing sequence followed by increases. The stack turns it into O(n).

```stdin
7
6 5 8 4 7 10 9
```

```stdout
2
```

### AND xor OR

**Problem.** For each interval, take its smallest value `M₁` and second smallest `M₂`, and evaluate `((M₁ & M₂) ⊕ (M₁ | M₂)) & (M₁ ⊕ M₂)`. Print the maximum over all intervals.

**Idea.** The expression simplifies. `(a & b) ⊕ (a | b) = a ⊕ b`, and AND-ing with `a ⊕ b` leaves `a ⊕ b`. So we need the maximum `a ⊕ b` over pairs that can be "the two smallest of some interval". Those are exactly the pairs that are adjacent in an increasing monotonic stack. When a new value pops a larger one, the pair forms; and the new value also pairs with the remaining top.

**Steps.**
1. Monotonic increasing stack. For each `x`: pop while the top is `> x`, scoring `top ⊕ x`; if the stack is still non-empty, score `top ⊕ x`; push `x`.

```python
import os


def andXorOr(a):
    st = []
    best = 0
    for x in a:
        while st and st[-1] > x:
            best = max(best, st.pop() ^ x)
        if st:
            best = max(best, st[-1] ^ x)
        st.append(x)
    return best


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    input()
    a = list(map(int, input().rstrip().split()))
    fptr.write(str(andXorOr(a)) + '\n')
    fptr.close()
```

**Watch out.** All O(n²) intervals collapse to O(n) candidate pairs. A brute force over all intervals confirms this on small arrays.

```stdin
5
9 6 3 5 2
```

```stdout
15
```

### Waiter

**Problem.** For `q` rounds, take plates from stack `A`. Those divisible by the `i`-th prime go to stack `B_i` and the rest form the new `A`. Output every `B_i` (top first), then what is left of `A`.

**Idea.** Simulate directly. Taking plates one by one from a stack reverses their order in the new stack, which is easy to get wrong.
- Keep each stack as a list whose last element is the top.
- Pop from `A`, pushing onto `B_i` or the new `A`.
- Print each `B_i` from the top, i.e. reversed.

**Steps.**
1. Generate `q` primes.
2. For each prime: pop everything from `A`, distribute, append the reversed `B` to the output; finally output `A` from the top.

```python
import os


def waiter(number, q):
    primes = []
    c = 2
    while len(primes) < q:
        if all(c % p for p in primes if p * p <= c):
            primes.append(c)
        c += 1
    out = []
    A = number[:]                                  # last element is the top
    for p in primes:
        B, nA = [], []
        while A:
            x = A.pop()
            (B if x % p == 0 else nA).append(x)
        out.extend(reversed(B))
        A = nA
    out.extend(reversed(A))
    return out


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, q = map(int, input().split())
    number = list(map(int, input().rstrip().split()))
    fptr.write('\n'.join(map(str, waiter(number, q))) + '\n')
    fptr.close()
```

**Watch out.** The input lists the plates bottom to top. Printing a stack "from the top" means reversing the Python list.

```stdin
5 1
3 4 7 6 5
```

```stdout
4
6
3
7
5
```
