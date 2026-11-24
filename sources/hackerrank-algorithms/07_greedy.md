## Greedy

### Minimum Absolute Difference in an Array

**Problem.** Find the smallest absolute difference between any two elements.

**Idea.** After sorting, the closest pair is always adjacent, so only `n − 1` differences need checking.

**Steps.**
1. Sort and return the minimum of `a[i+1] − a[i]`.

```python
import os


def minimumAbsoluteDifference(arr):
    arr = sorted(arr)
    return min(b - a for a, b in zip(arr, arr[1:]))


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    arr = list(map(int, input().split()))
    fptr.write(str(minimumAbsoluteDifference(arr)) + '\n')
    fptr.close()
```

**Watch out.** Checking all pairs is O(n²), which times out at n = 10⁵. Negative numbers need no special care once the array is sorted.

```stdin
3
3 -7 0
```

```stdout
3
```

### Marc's Cakewalk

**Problem.** After eating `j` cupcakes, Marc must walk `2^j · c` miles for the next cupcake of `c` calories. Minimise the total miles.

**Idea.** The multipliers `1, 2, 4, …` grow, so the biggest cupcakes should take the smallest multipliers (the rearrangement inequality). Eat them in descending order.

**Steps.**
1. Sort descending and return `Σ c_i · 2^i`.

```python
import os


def marcsCakewalk(calorie):
    return sum(c << i for i, c in enumerate(sorted(calorie, reverse=True)))


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    calorie = list(map(int, input().split()))
    fptr.write(str(marcsCakewalk(calorie)) + '\n')
    fptr.close()
```

**Watch out.** With 40 cupcakes the total exceeds 2³²; Python integers handle it, but other languages need 64-bit values.

```stdin
3
1 3 2
```

```stdout
11
```

### Grid Challenge

**Problem.** Sort each row of a letter grid. Then report whether every column is sorted top to bottom.

**Idea.** Sorting each row is the only freedom we have, and it is forced. After that, just check the columns.

**Steps.**
1. Sort every row.
2. Return `YES` if `rows[i][j] ≤ rows[i+1][j]` everywhere, else `NO`.

```python
import os


def gridChallenge(grid):
    rows = [sorted(r) for r in grid]
    ok = all(rows[i][j] <= rows[i + 1][j] for i in range(len(rows) - 1) for j in range(len(rows[0])))
    return 'YES' if ok else 'NO'


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n = int(input().strip())
        grid = [input() for _ in range(n)]
        fptr.write(gridChallenge(grid) + '\n')
    fptr.close()
```

**Watch out.** The grid need not be square: rows have length `m`, not `n`.

```stdin
1
5
ebacd
fghij
olmkn
trpqs
xywuv
```

```stdout
YES
```

### Luck Balance

**Problem.** Winning a contest costs its luck and losing it gains its luck. At most `k` important contests may be lost. Maximise the final luck.

**Idea.** Lose every unimportant contest. Among the important ones, lose the `k` with the most luck and win the rest.

**Steps.**
1. Add all the unimportant luck.
2. Sort the important luck values descending; add the first `k` and subtract the rest.

```python
import os


def luckBalance(k, contests):
    important = sorted((l for l, t in contests if t == 1), reverse=True)
    return sum(l for l, t in contests if t == 0) + sum(important[:k]) - sum(important[k:])


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    contests = [list(map(int, input().split())) for _ in range(n)]
    fptr.write(str(luckBalance(k, contests)) + '\n')
    fptr.close()
```

**Watch out.** Winning *subtracts* luck. It is a common slip to just skip the won contests.

```stdin
6 3
5 1
2 1
1 1
8 1
10 0
5 0
```

```stdout
29
```

### Maximum Perimeter Triangle

**Problem.** Choose three sticks that form a non-degenerate triangle with the largest perimeter. Break ties by the longest side, then by the shortest. Print them ascending, or `-1`.

**Idea.** Sort descending. For three consecutive sticks `a ≥ b ≥ c`, if `a < b + c` they form a triangle. If they fail, `a` can't pair with anything smaller, so move on. The first success has the biggest perimeter and, being found earliest, also the largest longest side.

**Steps.**
1. Sort descending and scan triples `(s[i], s[i+1], s[i+2])`.
2. Return the first valid one, reversed into ascending order.

```python
import os


def maximumPerimeterTriangle(sticks):
    s = sorted(sticks, reverse=True)
    for i in range(len(s) - 2):
        if s[i] < s[i + 1] + s[i + 2]:
            return [s[i + 2], s[i + 1], s[i]]
    return [-1]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    sticks = list(map(int, input().split()))
    fptr.write(' '.join(map(str, maximumPerimeterTriangle(sticks))) + '\n')
    fptr.close()
```

**Watch out.** "Non-degenerate" means a strict inequality: `1 2 3` is not a triangle.

```stdin
5
1 1 1 3 3
```

```stdout
1 3 3
```

### Candies

**Problem.** Every child gets at least one candy, and a child rated higher than a neighbour gets more than that neighbour. Minimise the total.

**Idea.** Make two passes. Left to right: each child must beat a lower-rated left neighbour. Right to left: each child must beat a lower-rated right neighbour. Taking the max of the two requirements satisfies both sides with the fewest candies.

**Steps.**
1. `left[i] = left[i−1] + 1` if `r[i] > r[i−1]`, else 1.
2. `right[i] = right[i+1] + 1` if `r[i] > r[i+1]`, else 1.
3. Return `Σ max(left[i], right[i])`.

```python
import os


def candies(n, arr):
    left = [1] * n
    for i in range(1, n):
        if arr[i] > arr[i - 1]:
            left[i] = left[i - 1] + 1
    total, right = 0, 1
    for i in range(n - 1, -1, -1):
        if i < n - 1 and arr[i] > arr[i + 1]:
            right += 1
        elif i < n - 1:
            right = 1
        total += max(left[i], right)
    return total


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    arr = [int(input().strip()) for _ in range(n)]
    fptr.write(str(candies(n, arr)) + '\n')
    fptr.close()
```

**Watch out.** Equal ratings put no constraint between the two children, so the count resets to 1. The total can reach about 5·10⁹.

```stdin
3
1
2
2
```

```stdout
4
```

### Beautiful Pairs

**Problem.** Pair positions with equal values `A[i] = B[j]`, using each index at most once. You **must** change exactly one element of `B` first. Maximise the number of pairs.

**Idea.** Without the change, the answer is the size of the multiset intersection. If some element is left unmatched, changing a spare `B` element to it gains one pair. If everything already matches, the forced change breaks one pair.

**Steps.**
1. `m = Σ min(countA[v], countB[v])`.
2. Return `m + 1` if `m < n`, else `n − 1`.

```python
import os
from collections import Counter


def beautifulPairs(A, B):
    ca, cb = Counter(A), Counter(B)
    m = sum(min(c, cb[v]) for v, c in ca.items())
    return m + 1 if m < len(A) else m - 1


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    A = list(map(int, input().split()))
    B = list(map(int, input().split()))
    fptr.write(str(beautifulPairs(A, B)) + '\n')
    fptr.close()
```

**Watch out.** The change is mandatory. Forgetting it gives `n` instead of `n − 1` when the arrays already match.

```stdin
4
1 2 3 4
1 2 3 3
```

```stdout
4
```

### Sherlock and The Beast

**Problem.** Print the largest `n`-digit number made of 5s and 3s where the number of 5s is divisible by 3 and the number of 3s is divisible by 5, or `-1`.

**Idea.** More leading 5s means a larger number. Try the largest count of 5s first: the biggest multiple of 3 that leaves a multiple of 5 for the 3s.

**Steps.**
1. For `fives` from the largest multiple of 3 that is ≤ `n` down to 0 (step 3): if `(n − fives) % 5 == 0`, print `'5'·fives + '3'·(n − fives)`.
2. If nothing fits, print -1.

```python
def decentNumber(n):
    for fives in range(n - n % 3, -1, -3):
        if (n - fives) % 5 == 0:
            print('5' * fives + '3' * (n - fives))
            return
    print(-1)


if __name__ == '__main__':
    t = int(input().strip())
    for _ in range(t):
        decentNumber(int(input().strip()))
```

**Watch out.** The function prints rather than returns. The loop takes at most 2 steps to hit a valid count once `n ≥ 8`, so it is effectively O(1).

```stdin
4
1
3
5
11
```

```stdout
-1
555
33333
55555533333
```

### Priyanka and Toys

**Problem.** One purchase of a toy weighing `w` gets every toy with weight in `[w, w + 4]` for free. Find the minimum number of purchases needed to get all toys.

**Idea.** Sort the weights. The lightest unbought toy must be bought by someone, and buying it covers the most possible after it. So repeatedly buy the lightest remaining toy and skip everything within 4 of it.

**Steps.**
1. Sort, then walk with `limit = w + 4`, counting a new purchase whenever a weight exceeds the limit.

```python
import os


def toys(w):
    count, limit = 0, -1
    for x in sorted(w):
        if x > limit:
            count += 1
            limit = x + 4
    return count


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    w = list(map(int, input().split()))
    fptr.write(str(toys(w)) + '\n')
    fptr.close()
```

**Watch out.** The range is inclusive: a toy weighing exactly `w + 4` is free.

```stdin
8
1 2 3 21 7 12 14 21
```

```stdout
4
```

### Largest Permutation

**Problem.** With at most `k` swaps, make the lexicographically largest permutation of `1..n`.

**Idea.** Fill positions from the left with the largest values `n, n−1, …`. When a value is already in place, it costs nothing. Otherwise swap it in using a value → index map, which costs one swap.

**Steps.**
1. `pos[v]` = index of `v`.
2. For `i = 0..`, while `k > 0`: `want = n − i`. If `arr[i] ≠ want`, swap `arr[i]` with `arr[pos[want]]`, fix both positions and decrease `k`.

```python
import os


def largestPermutation(k, arr):
    n = len(arr)
    pos = {v: i for i, v in enumerate(arr)}
    for i in range(n):
        if k == 0:
            break
        want = n - i
        if arr[i] != want:
            j = pos[want]
            pos[arr[i]], pos[want] = j, i
            arr[i], arr[j] = want, arr[i]
            k -= 1
    return arr


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    arr = list(map(int, input().split()))
    fptr.write(' '.join(map(str, largestPermutation(k, arr))) + '\n')
    fptr.close()
```

**Watch out.** Searching for `want` with `arr.index` each time makes it O(n²); keep the position map up to date instead. `k` can exceed `n`, which simply means the array ends up fully sorted descending.

```stdin
5 1
4 2 3 5 1
```

```stdout
5 2 3 4 1
```

### Mark and Toys

**Problem.** With budget `k`, buy as many distinct toys as possible.

**Idea.** To maximise the count, always buy the cheapest toys first.

**Steps.**
1. Sort the prices and keep adding them while the running sum stays ≤ `k`.

```python
import os


def maximumToys(prices, k):
    count = 0
    for p in sorted(prices):
        if p > k:
            break
        k -= p
        count += 1
    return count


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    prices = list(map(int, input().split()))
    fptr.write(str(maximumToys(prices, k)) + '\n')
    fptr.close()
```

**Watch out.** You can stop at the first toy you can't afford, because every later one costs at least as much.

```stdin
7 50
1 12 5 111 200 1000 10
```

```stdout
4
```

### Greedy Florist

**Problem.** `k` friends buy all the flowers. A friend's `j`-th purchase (counting from 0) of a flower priced `c` costs `(j + 1)·c`. Minimise the total.

**Idea.** Expensive flowers should get the smallest multipliers. Sort prices descending: the first `k` are bought at ×1, the next `k` at ×2, and so on.

**Steps.**
1. Return `Σ (i // k + 1) · c_i` over the prices sorted descending.

```python
import os


def getMinimumCost(k, c):
    return sum((i // k + 1) * x for i, x in enumerate(sorted(c, reverse=True)))


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    c = list(map(int, input().split()))
    fptr.write(str(getMinimumCost(k, c)) + '\n')
    fptr.close()
```

**Watch out.** The multiplier depends on how many flowers *that friend* has already bought, not on the overall count. That is why it rises only once every `k` purchases.

```stdin
3 3
2 5 6
```

```stdout
13
```

### Max Min

**Problem.** Choose `k` numbers so that `max − min` is as small as possible.

**Idea.** In sorted order, an optimal choice is always a contiguous window, because skipping a middle value only widens the range. So check every window of `k` consecutive values.

**Steps.**
1. Sort and return `min(a[i + k − 1] − a[i])`.

```python
import os


def maxMin(k, arr):
    arr = sorted(arr)
    return min(arr[i + k - 1] - arr[i] for i in range(len(arr) - k + 1))


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    k = int(input().strip())
    arr = [int(input().strip()) for _ in range(n)]
    fptr.write(str(maxMin(k, arr)) + '\n')
    fptr.close()
```

**Watch out.** The input gives one number per line, after separate lines for `n` and `k`.

```stdin
7
3
10
100
300
200
1000
20
30
```

```stdout
20
```

### Jim and the Orders

**Problem.** Order `i` is placed at time `t` and takes `d` to prepare. Print the customer numbers in the order they get their food, with ties going to the smaller number.

**Idea.** Each order is served at `t + d`. Sort by `(t + d, customer number)`.

**Steps.**
1. Return the indices (1-based) sorted by `(t + d, i)`.

```python
import os


def jimOrders(orders):
    return sorted(range(1, len(orders) + 1), key=lambda i: (sum(orders[i - 1]), i))


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    orders = [list(map(int, input().split())) for _ in range(n)]
    fptr.write(' '.join(map(str, jimOrders(orders))) + '\n')
    fptr.close()
```

**Watch out.** Python's sort is stable, but spelling out the index in the key makes the tie rule explicit.

```stdin
3
1 3
2 3
3 3
```

```stdout
1 2 3
```

### Permuting Two Arrays

**Problem.** Can `A` and `B` be permuted so that `A[i] + B[i] ≥ k` for every `i`?

**Idea.** Pair the smallest `A` with the largest `B`, and so on. If even that pairing fails at some position, any other pairing fails too (an exchange argument).

**Steps.**
1. Sort `A` ascending and `B` descending; check every sum.

```python
import os


def twoArrays(k, A, B):
    return 'YES' if all(a + b >= k for a, b in zip(sorted(A), sorted(B, reverse=True))) else 'NO'


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        n, k = map(int, input().split())
        A = list(map(int, input().split()))
        B = list(map(int, input().split()))
        fptr.write(twoArrays(k, A, B) + '\n')
    fptr.close()
```

**Watch out.** Sorting both arrays the same way is the classic mistake; the pairing must be opposite.

```stdin
2
3 10
2 1 3
7 8 9
4 5
1 2 2 1
3 3 3 4
```

```stdout
YES
NO
```

### Cutting Boards

**Problem.** Cut an `m × n` board into unit squares. Each cut line has a cost that is multiplied by the number of pieces it crosses. Minimise the total modulo 10⁹+7.

**Idea.** A cut is multiplied by `1 + (number of cuts already made in the other direction)`. So expensive cuts should be made early, while the multipliers are small. Sort all cuts by cost, descending. A horizontal cut costs `cost × (vertical cuts so far + 1)`, and vice versa.

**Steps.**
1. Merge both cost lists, tagged by direction, sorted descending.
2. Keep counters of cuts made in each direction. Accumulate the cost and reduce modulo at the end.

```python
import os

MOD = 10 ** 9 + 7


def boardCutting(cost_y, cost_x):
    cuts = sorted([(c, 0) for c in cost_y] + [(c, 1) for c in cost_x], reverse=True)
    made = [0, 0]
    total = 0
    for c, d in cuts:
        total += c * (made[1 - d] + 1)
        made[d] += 1
    return total % MOD


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        m, n = map(int, input().split())
        cost_y = list(map(int, input().split()))
        cost_x = list(map(int, input().split()))
        fptr.write(str(boardCutting(cost_y, cost_x)) + '\n')
    fptr.close()
```

**Watch out.** Compare the exact totals and take the modulo only at the end; with Python integers the greedy order never compares reduced values. Tied costs can be cut in any order.

```stdin
1
2 2
2
1
```

```stdout
4
```

### Reverse Shuffle Merge

**Problem.** `s` was formed by merging `reverse(A)` with a shuffle of `A`. Find the lexicographically smallest possible `A`.

**Idea.** `A` uses exactly half of each letter's count, and `reverse(A)` is a subsequence of `s`. Equivalently, `A` is a subsequence of `reverse(s)`. So pick the smallest subsequence of `reverse(s)` with the required counts. Use a monotonic stack: pop a larger letter on top if enough copies of it still remain later to re-add it.

**Steps.**
1. `need[c] = count[c] / 2` and `left[c] = count[c]`.
2. For each `ch` in `reversed(s)`: decrement `left[ch]`. If `ch` is still needed: while the top of the stack is greater than `ch` and `left[top] > need[top]`, pop it (and increase `need[top]`). Push `ch` and decrement `need[ch]`.

```python
import os
from collections import Counter


def reverseShuffleMerge(s):
    count = Counter(s)
    need = {c: v // 2 for c, v in count.items()}
    left = dict(count)
    stack = []
    for ch in reversed(s):
        left[ch] -= 1
        if need[ch] == 0:
            continue
        while stack and stack[-1] > ch and left[stack[-1]] > need[stack[-1]]:
            need[stack.pop()] += 1
        stack.append(ch)
        need[ch] -= 1
    return ''.join(stack)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    s = input()
    fptr.write(reverseShuffleMerge(s) + '\n')
    fptr.close()
```

**Watch out.** The pop test needs strictly more remaining copies than still needed, counted *after* the current position, because a popped letter must be re-added later.

```stdin
eggegg
```

```stdout
egg
```

### Goodland Electricity

**Problem.** Cities marked 1 can host a plant that powers cities within distance `k − 1`. Find the minimum number of plants that power every city, or -1.

**Idea.** Standing at the leftmost unpowered city `pos`, build the plant **farthest to the right** that still reaches `pos` (index ≤ `pos + k − 1`). That leaves the most coverage for later cities. Then jump to `plant + k`.

**Steps.**
1. Let `pos = 0`. Search `j` from `min(n−1, pos+k−1)` down to `max(0, pos−k+1)` for a 1.
2. If none exists, return -1. Otherwise count a plant and set `pos = j + k`.

```python
import os


def pylons(k, arr):
    n = len(arr)
    pos, plants = 0, 0
    while pos < n:
        j = min(n - 1, pos + k - 1)
        while j >= max(0, pos - k + 1) and arr[j] == 0:
            j -= 1
        if j < max(0, pos - k + 1):
            return -1
        plants += 1
        pos = j + k
    return plants


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    arr = list(map(int, input().split()))
    fptr.write(str(pylons(k, arr)) + '\n')
    fptr.close()
```

**Watch out.** The plant may sit to the *left* of `pos` (down to `pos − k + 1`). Forgetting that wrongly reports -1.

```stdin
6 2
0 1 1 1 1 0
```

```stdout
2
```

### Cloudy Day

**Problem.** Towns lie on a line with populations; each cloud covers `[y − r, y + r]`. Remove exactly one cloud so that as many people as possible live in sunny towns (covered by no cloud).

**Idea.** A town covered by two or more clouds stays dark whatever we do. So the answer is `(towns covered by no cloud) + max over clouds of (towns covered by that cloud only)`. Sweep in sorted order:
- **Active clouds.** Process cloud starts and ends, keeping the active count and the **sum of active cloud ids**.
- **Who covers a town.** When exactly one cloud is active, that sum *is* its id.

**Steps.**
1. Build events: cloud start at `y − r`, cloud end just after `y + r`, town at `x`. Sort so that at equal coordinates starts come before towns and ends come after them.
2. Sweep. For each town: if 0 clouds are active, add to `free`; if 1, add to `only[id]`.
3. Return `free + max(only)`.

```python
import os


def maximumPeople(p, x, y, r):
    events = []
    for i, (yy, rr) in enumerate(zip(y, r)):
        events.append((yy - rr, 0, i))       # start
        events.append((yy + rr, 2, i))       # end (after towns at the same point)
    for pp, xx in zip(p, x):
        events.append((xx, 1, pp))
    events.sort()
    active = idsum = 0
    free = 0
    only = [0] * len(y)
    for _, kind, v in events:
        if kind == 0:
            active += 1
            idsum += v
        elif kind == 2:
            active -= 1
            idsum -= v
        elif active == 0:
            free += v
        elif active == 1:
            only[idsum] += v
    return free + (max(only) if only else 0)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    p = list(map(int, input().split()))
    x = list(map(int, input().split()))
    m = int(input().strip())
    y = list(map(int, input().split()))
    r = list(map(int, input().split()))
    fptr.write(str(maximumPeople(p, x, y, r)) + '\n')
    fptr.close()
```

**Watch out.**
- **Inclusive ends.** Cloud ranges include their ends, so at equal coordinates starts sort before towns and ends after them.
- **Identifying the cloud.** The id-sum trick identifies the single active cloud without a set.

```stdin
2
10 100
5 100
1
4
1
```

```stdout
110
```

### Chief Hopper

**Problem.** A bot with energy `e` jumps across buildings of heights `h_i`: if `h > e` it loses `h − e`, otherwise it gains `e − h`. Both cases mean `e → 2e − h`. Find the minimum starting energy so that `e` never goes negative.

**Idea.** Work backwards. At the end the bot needs at least 0. Before a jump over `h`, it needs `e` such that `2e − h ≥ need`, i.e. `e = ⌈(need + h) / 2⌉`.

**Steps.**
1. `need = 0`. For `h` in reverse, `need = (need + h + 1) // 2`. Return `need`.

```python
import os


def chiefHopper(arr):
    need = 0
    for h in reversed(arr):
        need = (need + h + 1) // 2
    return need


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    arr = list(map(int, input().split()))
    fptr.write(str(chiefHopper(arr)) + '\n')
    fptr.close()
```

**Watch out.** Simulating forward with binary search also works, but the energy doubles each step and quickly becomes astronomically large. The backward pass stays small.

```stdin
5
3 4 3 2 4
```

```stdout
4
```

### Sherlock and MiniMax

**Problem.** Find the `M` in `[p, q]` that maximises `min |a_i − M|`, returning the smallest such `M` on ties.

**Idea.** The distance to the nearest element is a "tent" function: it peaks halfway between two neighbouring elements and grows toward the range ends. So the best `M` is `p`, `q`, or a midpoint `⌊(a_i + a_{i+1}) / 2⌋` of adjacent sorted elements that lies inside the range. Evaluate those candidates directly.

**Steps.**
1. Collect the candidates and evaluate `f(M) = min |a − M|` for each.
2. Return the candidate with the largest `f`, then the smallest `M`.

```python
import os


def sherlockAndMinimax(arr, p, q):
    a = sorted(arr)
    cands = {p, q}
    for u, v in zip(a, a[1:]):
        mid = (u + v) // 2
        if p <= mid <= q:
            cands.add(mid)
    return min(cands, key=lambda m: (-min(abs(x - m) for x in a), m))


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    arr = list(map(int, input().split()))
    p, q = map(int, input().split())
    fptr.write(str(sherlockAndMinimax(arr, p, q)) + '\n')
    fptr.close()
```

**Watch out.** Scanning every `M` in a range of 10⁹ is far too slow. The floor of the midpoint already gives the smaller `M` when the two middle values tie.

```stdin
3
5 8 14
4 9
```

```stdout
4
```

### Accessory Collection

**Problem.** Buy `L` items from types priced `1..A` so that every `N`-item subset contains at least `D` distinct types. Maximise the spend, or print `SAD`.

**Idea.**
- **Restating the rule.** The worst subset takes as many items as possible from just `D − 1` types. So the rule says the `D − 1` largest counts sum to at most `N − 1`.
- **Shape of the counts.** Give larger counts to more expensive types. Let `y` be the count of the `(D−1)`-th type. Every later type is capped at `y`, and types 2..`D−1` should sit at exactly `y`, with all the rest of the `N − 1` budget on the most expensive type. That gives `c_1 = N − 1 − (D−2)·y`, which must be ≥ `y`.
- **The tail.** The remaining `L − (N − 1)` items fill the cheaper types greedily, at most `y` each.

Try every valid `y` and keep the best spend.

**Steps.**
1. If `D = 1`, every purchase works, so the answer is `L·A`. If `A < D`, print `SAD`.
2. For `y = 1..(N−1)/(D−1)` (for `D = 2`, only `y = N − 1`): the top part is worth `A(N−1) − y·(D−2)(D−1)/2`. The tail fills `rem` items into types priced `A−D+1, A−D, …`, `y` per type. Skip `y` if the tail doesn't fit.
3. Print the best value, or `SAD` if no `y` works.

```python
import os


def acessoryCollection(L, A, N, D):
    if D == 1:
        return str(L * A)
    if A < D:
        return 'SAD'
    rem = L - (N - 1)
    types_left = A - D + 1
    top_price = A - D + 1
    best = None
    ys = [N - 1] if D == 2 else range(1, (N - 1) // (D - 1) + 1)
    for y in ys:
        if y == 0 or y * types_left < rem:
            continue
        top = A * (N - 1) - y * (D - 2) * (D - 1) // 2
        q, part = divmod(rem, y)
        tail = y * (q * top_price - q * (q - 1) // 2) + part * (top_price - q)
        if best is None or top + tail > best:
            best = top + tail
    return 'SAD' if best is None else str(best)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    T = int(input())
    for _ in range(T):
        L, A, N, D = map(int, input().split())
        fptr.write(acessoryCollection(L, A, N, D) + '\n')
    fptr.close()
```

**Watch out.**
- **Tail capacity.** The tail must fit: `y · (A − D + 1) ≥ L − (N − 1)`. With `A` up to 10⁹ the prices themselves stay huge, and Python integers keep the sums exact.
- **How this was checked.** Against an exhaustive search over all count vectors for small inputs.

```stdin
2
6 5 3 2
2 1 2 2
```

```stdout
24
SAD
```

### Team Formation

**Problem.** Split contestants into teams of distinct, consecutive skill levels so that the smallest team is as large as possible.

**Idea.** Go through the skill values in increasing order. The `c` people with skill `v` extend teams that currently end at `v − 1`, and the **shortest** teams should be extended first. Leftover people start new teams; teams that aren't extended are finished for good. A min-heap of the open team sizes makes "shortest first" cheap.

**Steps.**
1. Count the skills. For each distinct `v` in order: if `v` isn't `prev + 1`, close every open team.
2. Pop up to `c` smallest open teams and extend them. Push `c − popped` new teams of size 1. Close the rest.
3. The answer is the minimum closed size (0 when nobody registered).

```python
import sys
from collections import Counter
from heapq import heappop, heappush


def team_formation(skills):
    if not skills:
        return 0
    cnt = Counter(skills)
    best = float('inf')
    open_teams = []
    prev = None
    for v in sorted(cnt):
        c = cnt[v]
        if prev is None or v != prev + 1:
            if open_teams:
                best = min(best, min(open_teams))
            open_teams = []
        new = []
        while open_teams and c > 0:
            new.append(heappop(open_teams) + 1)
            c -= 1
        if open_teams:
            best = min(best, open_teams[0])
        new.extend([1] * c)
        open_teams = []
        for s in new:
            heappush(open_teams, s)
        prev = v
    if open_teams:
        best = min(best, open_teams[0])
    return best


def main():
    lines = sys.stdin.read().strip().split('\n')
    t = int(lines[0])
    out = []
    for line in lines[1:1 + t]:
        nums = list(map(int, line.split()))
        out.append(team_formation(nums[1:1 + nums[0]]))
    print('\n'.join(map(str, out)))


main()
```

**Watch out.** Extending the *longest* teams first looks natural but leaves tiny teams behind. A test with `n = 0` is allowed and must print 0.

```stdin
4
7 4 5 2 3 -4 -3 -5
1 -4
4 3 2 3 1
7 1 -2 -3 -4 2 0 -1
```

```stdout
3
1
1
7
```

### Fighting Pits

**Problem.** Teams of fighters fight in alternating turns. A fighter of strength `s` kills up to `s` enemies. Support adding a fighter (whose strength is at least the team's current maximum) and querying who wins when `x` attacks first.

**Idea.** Optimal play is greedy on both sides: always attack with your strongest living fighter and kill the enemy's strongest ones. Keep each team sorted. Then the living fighters are always a prefix of the sorted list, so a fight is a short loop on two counters: `b -= X[a−1]`, then `a -= Y[b−1]`. The added fighters are guaranteed to be the strongest, so adding is just an append.

**Steps.**
1. Store each team's strengths in sorted order.
2. For a query, set `a = len(X)` and `b = len(Y)`, then alternate the two subtractions until one side reaches ≤ 0.

```python
import sys


def main():
    data = sys.stdin.buffer.read().split()
    n, k, q = int(data[0]), int(data[1]), int(data[2])
    teams = [[] for _ in range(k + 1)]
    pos = 3
    for _ in range(n):
        s, t = int(data[pos]), int(data[pos + 1])
        pos += 2
        teams[t].append(s)
    for t in teams:
        t.sort()
    out = []
    for _ in range(q):
        kind, u, v = int(data[pos]), int(data[pos + 1]), int(data[pos + 2])
        pos += 3
        if kind == 1:
            teams[v].append(u)
            continue
        X, Y = teams[u], teams[v]
        a, b = len(X), len(Y)
        while True:
            b -= X[a - 1]
            if b <= 0:
                out.append(u)
                break
            a -= Y[b - 1]
            if a <= 0:
                out.append(v)
                break
    print('\n'.join(map(str, out)))


main()
```

**Watch out.** Each round removes at least one fighter, so a fight takes O(team size) rounds when strengths are tiny. Fast enough in practice, but the binary-scoring worst case needs the official square-root trick: precompute answers for big teams.

```stdin
7 2 6
1 1
2 1
1 1
1 2
1 2
1 2
2 2
2 1 2
2 2 1
1 2 1
1 2 1
2 1 2
2 2 1
```

```stdout
1
2
1
1
```
