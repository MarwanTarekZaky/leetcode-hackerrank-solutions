# Heap

### 215. Kth Largest Element in an Array
difficulty: Medium

**Problem.** Return the `k`-th largest element (in sorted order, not the k-th distinct). Can you avoid sorting?

**Example.** `[3,2,1,5,6,4], k = 2` → `5`.

**Idea: min-heap of size k.** Keep the `k` largest values seen so far in a **min-heap**. Its top (the smallest of those `k`) is the `k`-th largest. A new number only enters if it beats the top.

**Steps.**
1. `heap = nums[:k]`, `heapify`.
2. For each remaining `x`: if `x > heap[0]`, `heapreplace(heap, x)`.
3. Return `heap[0]`.

```python
class Solution:
    def findKthLargest(self, nums: List[int], k: int) -> int:
        heap = nums[:k]
        heapq.heapify(heap)
        for x in nums[k:]:
            if x > heap[0]:
                heapq.heapreplace(heap, x)
        return heap[0]
```

**Complexity.** Time O(n log k), space O(k).

**Watch out.**
- The heap type is the **opposite** of what you want: kth largest → min-heap; kth smallest → max-heap (push negatives in Python).
- Quickselect is O(n) on average: partition around a random pivot into `<`, `==`, `>` and continue only in the part containing index `n - k`.

```py
import random
target = len(nums) - k
l, r = 0, len(nums) - 1
while True:
    pivot = nums[random.randint(l, r)]
    lt, i, gt = l, l, r
    while i <= gt:
        if nums[i] < pivot:
            nums[lt], nums[i] = nums[i], nums[lt]; lt += 1; i += 1
        elif nums[i] > pivot:
            nums[i], nums[gt] = nums[gt], nums[i]; gt -= 1
        else:
            i += 1
    if target < lt:
        r = lt - 1
    elif target > gt:
        l = gt + 1
    else:
        return pivot
```

```test
assert Solution().findKthLargest([3,2,1,5,6,4], 2) == 5
assert Solution().findKthLargest([3,2,3,1,2,4,5,5,6], 4) == 4
assert Solution().findKthLargest([1], 1) == 1
```

### 502. IPO
difficulty: Hard

**Problem.** You have capital `w` and may finish at most `k` projects. Project `i` needs `capital[i]` to start and adds `profits[i]` to your capital when done. Maximize the final capital.

**Example.** `k = 2, w = 0, profits = [1,2,3], capital = [0,1,1]` → `4`.

**Idea: greedy with two structures.** Sort projects by required capital. Each round, move every project you can now afford into a **max-heap of profits**, then take the most profitable one. Doing the best affordable project first is always optimal because capital only grows.

**Steps.**
1. Sort `(capital, profit)` pairs; pointer `i`.
2. Repeat `k` times: push profits of all projects with `capital <= w`; if the heap is empty, stop; else `w += pop max`.

```python
class Solution:
    def findMaximizedCapital(self, k: int, w: int, profits: List[int], capital: List[int]) -> int:
        projects = sorted(zip(capital, profits))
        heap = []                    # max-heap of profits (stored as negatives)
        i = 0
        for _ in range(k):
            while i < len(projects) and projects[i][0] <= w:
                heapq.heappush(heap, -projects[i][1])
                i += 1
            if not heap:
                break
            w -= heapq.heappop(heap)
        return w
```

**Complexity.** Time O(n log n + k log n), space O(n).

**Watch out.** Stop early when nothing is affordable; the loop would otherwise waste rounds.

```test
assert Solution().findMaximizedCapital(2, 0, [1,2,3], [0,1,1]) == 4
assert Solution().findMaximizedCapital(3, 0, [1,2,3], [0,1,2]) == 6
assert Solution().findMaximizedCapital(1, 0, [1], [1]) == 0
```

### 373. Find K Pairs with Smallest Sums
difficulty: Medium

**Problem.** Two sorted arrays. Return the `k` pairs `(u, v)` (one from each) with the smallest sums.

**Example.** `[1,7,11], [2,4,6], k = 3` → `[[1,2],[1,4],[1,6]]`.

**Idea.** Think of a grid where cell `(i, j)` has sum `nums1[i] + nums2[j]`; rows and columns are sorted. Start the heap with `(i, 0)` for the first `k` rows. Each time you pop `(i, j)`, push its right neighbour `(i, j + 1)`. It's like merging `k` sorted lists.

**Steps.**
1. Picture a grid where cell `(i, j)` has sum `nums1[i] + nums2[j]`; it grows to the right and downward.
2. Put `(sum, i, 0)` for the first `min(k, len(nums1))` rows in a min-heap.
3. Pop the smallest sum and add the pair `[nums1[i], nums2[j]]` to the result.
4. Push its right neighbour `(i, j + 1)` if it exists.
5. Repeat until you have `k` pairs or the heap is empty.

```python
class Solution:
    def kSmallestPairs(self, nums1: List[int], nums2: List[int], k: int) -> List[List[int]]:
        heap = [(nums1[i] + nums2[0], i, 0) for i in range(min(k, len(nums1)))]
        heapq.heapify(heap)
        res = []
        while heap and len(res) < k:
            _, i, j = heapq.heappop(heap)
            res.append([nums1[i], nums2[j]])
            if j + 1 < len(nums2):
                heapq.heappush(heap, (nums1[i] + nums2[j + 1], i, j + 1))
        return res
```

**Complexity.** Time O(k log k), space O(k).

**Watch out.** Seeding only the first column and moving right avoids pushing the same cell twice (no visited set needed).

```test
assert Solution().kSmallestPairs([1,7,11], [2,4,6], 3) == [[1,2],[1,4],[1,6]]
assert Solution().kSmallestPairs([1,1,2], [1,2,3], 2) == [[1,1],[1,1]]
```

### 295. Find Median from Data Stream
difficulty: Hard

**Problem.** Support `addNum(num)` and `findMedian()` over a stream of numbers.

**Idea: two heaps.** A **max-heap** `low` holds the smaller half, a **min-heap** `high` the larger half. Keep `len(low) == len(high)` or one more in `low`. The median is the top of `low` (odd count) or the average of both tops.

**Steps.**
1. `addNum`: push into `low`, then move `low`'s largest into `high` (keeps order between halves); if `high` became bigger, move its smallest back to `low`.
2. `findMedian`: as described.

```python
class MedianFinder:
    def __init__(self):
        self.low = []    # max-heap via negatives
        self.high = []   # min-heap

    def addNum(self, num: int) -> None:
        heapq.heappush(self.low, -num)
        heapq.heappush(self.high, -heapq.heappop(self.low))
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def findMedian(self) -> float:
        if len(self.low) > len(self.high):
            return float(-self.low[0])
        return (-self.low[0] + self.high[0]) / 2
```

**Complexity.** `addNum` O(log n), `findMedian` O(1).

**Watch out.** Always passing the new number through `low` then `high` guarantees every value in `low` ≤ every value in `high`.

```test
m = MedianFinder(); m.addNum(1); m.addNum(2); assert m.findMedian() == 1.5
m.addNum(3); assert m.findMedian() == 2.0
```

# Bit Manipulation

### 67. Add Binary
difficulty: Easy

**Problem.** Add two binary strings and return the sum as a binary string.

**Example.** `"11" + "1"` → `"100"`.

**Idea.** Add from the right with a carry, like decimal addition: `total` is 0–3, the digit is `total % 2`, the carry is `total // 2`.

**Steps.**
1. Start `i` and `j` at the last characters of `a` and `b`, `carry = 0`.
2. While there are digits left or a carry: `total = carry + digit of a + digit of b` (missing digits count as 0).
3. The output digit is `total % 2` and the new carry is `total // 2`.
4. The digits come out right to left, so reverse them and join.

```python
class Solution:
    def addBinary(self, a: str, b: str) -> str:
        i, j, carry = len(a) - 1, len(b) - 1, 0
        res = []
        while i >= 0 or j >= 0 or carry:
            total = carry
            if i >= 0:
                total += ord(a[i]) - ord('0')
                i -= 1
            if j >= 0:
                total += ord(b[j]) - ord('0')
                j -= 1
            res.append('1' if total % 2 else '0')
            carry = total // 2
        return ''.join(reversed(res))
```

**Complexity.** Time O(max(m, n)), space O(max(m, n)).

**Watch out.** `or carry` writes the final carry. Python shortcut: `f"{int(a, 2) + int(b, 2):b}"` (fine in real code; interviewers want the loop).

```test
assert Solution().addBinary("11", "1") == "100"
assert Solution().addBinary("1010", "1011") == "10101"
assert Solution().addBinary("0", "0") == "0"
```

### 190. Reverse Bits
difficulty: Easy

**Problem.** Reverse the bits of a 32-bit integer.

**Idea.** 32 times: shift the result left to make room, copy the last bit of `n` into it, shift `n` right. The first bit taken ends up furthest left.

**Steps.**
1. Start with `res = 0`.
2. Repeat 32 times: shift `res` left by one to make room (`res << 1`).
3. Put the last bit of `n` in that free spot: `| (n & 1)`.
4. Shift `n` right to drop the bit you just used.
5. The first bit read ends up as the highest bit. Return `res`.

```python
class Solution:
    def reverseBits(self, n: int) -> int:
        res = 0
        for _ in range(32):
            res = (res << 1) | (n & 1)
            n >>= 1
        return res
```

**Complexity.** O(32) = O(1).

**Watch out.**
- Always run exactly 32 times: leading zeros of `n` must become trailing zeros of the result.
- Negative input: `n &= 0xFFFFFFFF` first; for a signed result, `if res >= 2**31: res -= 2**32`.
- "Called many times" follow-up: precompute reversed values for all 256 bytes and combine 4 lookups:

```py
TABLE = [int(f"{i:08b}"[::-1], 2) for i in range(256)]
def reverse_bits(n):
    n &= 0xFFFFFFFF
    return (TABLE[n & 0xFF] << 24) | (TABLE[(n >> 8) & 0xFF] << 16) | \
           (TABLE[(n >> 16) & 0xFF] << 8) | TABLE[(n >> 24) & 0xFF]
```

```test
assert Solution().reverseBits(43261596) == 964176192
assert Solution().reverseBits(2147483644) == 1073741822
```

### 191. Number of 1 Bits
difficulty: Easy

**Problem.** Return the number of set bits (the Hamming weight) of a positive integer.

**Idea.** `n & (n - 1)` clears the lowest set bit. Count how many times you can do it before `n` becomes 0: one step per set bit.

**Steps.**
1. Start `count = 0`.
2. While `n` isn't 0: `n &= n - 1`. This turns off the lowest 1 bit.
3. Add 1 to `count` each time.
4. The loop runs once per 1 bit; return `count`.

```python
class Solution:
    def hammingWeight(self, n: int) -> int:
        count = 0
        while n:
            n &= n - 1
            count += 1
        return count
```

**Complexity.** O(number of set bits).

**Watch out.** Why it works: `n - 1` flips the lowest 1 to 0 and all zeros below it to 1, so the AND removes exactly that bit. Built-ins: `bin(n).count('1')` or `n.bit_count()` (Python 3.10+).

```test
assert Solution().hammingWeight(11) == 3
assert Solution().hammingWeight(128) == 1
assert Solution().hammingWeight(2147483645) == 30
```

### 136. Single Number
difficulty: Easy

**Problem.** Every element appears twice except one. Find it in O(n) time and O(1) space.

**Idea.** XOR all numbers: `a ^ a = 0`, `a ^ 0 = a`, and order doesn't matter, so pairs cancel and the single number remains.

**Steps.**
1. Start `res = 0`.
2. XOR every number into it: `res ^= x`.
3. Each pair cancels out (`a ^ a = 0`), and `0 ^ a = a`, so only the single number is left. Return `res`.

```python
class Solution:
    def singleNumber(self, nums: List[int]) -> int:
        res = 0
        for x in nums:
            res ^= x
        return res
```

**Complexity.** Time O(n), space O(1).

**Watch out.** Works with negative numbers too. Alternatives using O(n) space: `Counter`, a set, or `2 * sum(set(nums)) - sum(nums)`.

```test
assert Solution().singleNumber([2,2,1]) == 1
assert Solution().singleNumber([4,1,2,1,2]) == 4
assert Solution().singleNumber([-3,5,-3]) == 5
```

### 137. Single Number II
difficulty: Medium

**Problem.** Every element appears **three** times except one, which appears once. Find it in O(n) time, O(1) space.

**Idea.** Count each of the 32 bit positions across all numbers. Bits from the triples add up to multiples of 3, so `count % 3` gives the single number's bit.

**Steps.**
1. For each bit `b` in 0..31: count numbers with that bit set; if `count % 3`, set bit `b` in the result.
2. Convert from 32-bit two's complement: if bit 31 is set, subtract `2**32`.

```python
class Solution:
    def singleNumber(self, nums: List[int]) -> int:
        res = 0
        for b in range(32):
            count = sum((x >> b) & 1 for x in nums)
            if count % 3:
                res |= 1 << b
        if res >= 1 << 31:
            res -= 1 << 32
        return res
```

**Complexity.** Time O(32n), space O(1).

**Watch out.** Python's `>>` on negatives keeps the sign (infinite 1s), so bit 31 is set for negative numbers and the final adjustment gives the correct negative result. Bit-trick version: `ones = (ones ^ x) & ~twos; twos = (twos ^ x) & ~ones`, answer `ones`.

```test
assert Solution().singleNumber([2,2,3,2]) == 3
assert Solution().singleNumber([0,1,0,1,0,1,99]) == 99
assert Solution().singleNumber([-2,-2,1,1,4,1,4,4,-4,-2]) == -4
```

### 201. Bitwise AND of Numbers Range
difficulty: Medium

**Problem.** Return the AND of all numbers from `left` to `right` inclusive.

**Example.** `5..7` → `4` (`101 & 110 & 111 = 100`).

**Idea.** Any bit below the highest differing bit flips somewhere in the range, so it becomes 0. The answer is the **common binary prefix** of `left` and `right`, followed by zeros. Shift both right until they're equal, then shift back.

**Steps.**
1. Every bit below the highest bit where `left` and `right` differ becomes 0 somewhere in the range.
2. Shift both numbers right, counting the shifts, until they're equal. What remains is their common prefix.
3. Shift the prefix back left by that count (zeros fill the low bits) and return it.

```python
class Solution:
    def rangeBitwiseAnd(self, left: int, right: int) -> int:
        shift = 0
        while left != right:
            left >>= 1
            right >>= 1
            shift += 1
        return left << shift
```

**Complexity.** O(32) = O(1).

**Watch out.** Looping from `left` to `right` is too slow (up to 2³¹ numbers). Alternative: `while right > left: right &= right - 1; return right`.

```test
assert Solution().rangeBitwiseAnd(5, 7) == 4
assert Solution().rangeBitwiseAnd(0, 0) == 0
assert Solution().rangeBitwiseAnd(1, 2147483647) == 0
```

# Math

### 9. Palindrome Number
difficulty: Easy

**Problem.** Is the integer a palindrome? Follow-up: without converting to a string.

**Idea.** Negative numbers and numbers ending in 0 (except 0) can't be palindromes. Otherwise reverse **half** of the digits and compare with the other half.

**Steps.**
1. Reject `x < 0` and `x % 10 == 0 and x != 0`.
2. While `x > rev`: move the last digit of `x` onto `rev`.
3. Even length: `x == rev`. Odd length: `x == rev // 10` (drop the middle digit).

```python
class Solution:
    def isPalindrome(self, x: int) -> bool:
        if x < 0 or (x % 10 == 0 and x != 0):
            return False
        rev = 0
        while x > rev:
            rev = rev * 10 + x % 10
            x //= 10
        return x == rev or x == rev // 10
```

**Complexity.** Time O(log x), space O(1).

**Watch out.** Without the trailing-zero check, `10` would wrongly pass (`x = 0`, `rev = 1`, `0 == 1 // 10`). String version: `s = str(x); return s == s[::-1]`.

```test
assert Solution().isPalindrome(121) is True
assert Solution().isPalindrome(-121) is False
assert Solution().isPalindrome(10) is False
assert Solution().isPalindrome(0) is True
assert Solution().isPalindrome(1221) is True
```

### 66. Plus One
difficulty: Easy

**Problem.** A big integer is given as a list of digits (most significant first). Add one.

**Example.** `[1,2,9]` → `[1,3,0]`; `[9,9]` → `[1,0,0]`.

**Idea.** From the right: a digit below 9 just increases and you're done; a 9 becomes 0 and the carry moves left. If every digit was 9, put a 1 in front.

**Steps.**
1. Walk the digits from right to left.
2. If the digit is less than 9, add 1 and return the list: no carry left.
3. If it's 9, it becomes 0 and the carry moves one place left.
4. If the loop finishes, every digit was 9: return `[1] + digits` (e.g. `999 → 1000`).

```python
class Solution:
    def plusOne(self, digits: List[int]) -> List[int]:
        for i in range(len(digits) - 1, -1, -1):
            if digits[i] < 9:
                digits[i] += 1
                return digits
            digits[i] = 0
        return [1] + digits
```

**Complexity.** Time O(n) worst case, usually O(1); space O(1) except the all-9s case.

**Watch out.** Converting to int and back works in Python but skips the point of the exercise.

```test
assert Solution().plusOne([1,2,3]) == [1,2,4]
assert Solution().plusOne([4,3,2,1]) == [4,3,2,2]
assert Solution().plusOne([9]) == [1,0]
assert Solution().plusOne([9,9]) == [1,0,0]
```

### 172. Factorial Trailing Zeroes
difficulty: Medium

**Problem.** How many trailing zeros does `n!` have? O(log n).

**Idea.** Each trailing zero comes from a factor 10 = 2 × 5. There are always more 2s than 5s, so count the factors of 5: numbers divisible by 5 give one, by 25 one more, by 125 one more, and so on.

**Steps.**
1. Each trailing zero needs a factor 5 (there are always more factors 2).
2. `n // 5` numbers up to `n` contain one 5, `n // 25` contain a second one, `n // 125` a third, and so on.
3. Loop: `n //= 5`, add `n` to `count`, until `n` is 0. Return `count`.

```python
class Solution:
    def trailingZeroes(self, n: int) -> int:
        count = 0
        while n:
            n //= 5
            count += n
        return count
```

**Complexity.** O(log₅ n).

**Watch out.** Don't compute `n!`; it's astronomically large.

```test
assert Solution().trailingZeroes(3) == 0
assert Solution().trailingZeroes(5) == 1
assert Solution().trailingZeroes(25) == 6
assert Solution().trailingZeroes(0) == 0
```

### 69. Sqrt(x)
difficulty: Easy

**Problem.** Return `floor(sqrt(x))` without using an exponent function or operator.

**Idea.** Binary search for the largest `m` with `m * m <= x`.

**Steps.**
1. Binary search `mid` in `0 .. x`.
2. If `mid * mid <= x`, `mid` is a valid answer: save it as `ans` and try bigger (`l = mid + 1`).
3. Otherwise `mid` is too big: `r = mid - 1`.
4. Return `ans`, the largest `mid` whose square fits.

```python
class Solution:
    def mySqrt(self, x: int) -> int:
        l, r, ans = 0, x, 0
        while l <= r:
            mid = (l + r) // 2
            if mid * mid <= x:
                ans = mid
                l = mid + 1
            else:
                r = mid - 1
        return ans
```

**Complexity.** Time O(log x), space O(1).

**Watch out.** In Java/C++ `mid * mid` overflows; use `long` or compare `mid <= x / mid`. Newton's method: `r = x; while r * r > x: r = (r + x // r) // 2`.

```test
assert Solution().mySqrt(4) == 2
assert Solution().mySqrt(8) == 2
assert Solution().mySqrt(0) == 0
assert Solution().mySqrt(2147395599) == 46339
```

### 50. Pow(x, n)
difficulty: Medium

**Problem.** Compute `x` to the power `n` (n can be negative and up to ±2³¹).

**Idea: fast exponentiation.** Read the bits of `n`: square `x` each step (`x, x², x⁴, ...`) and multiply it into the result when the current bit of `n` is 1. Handle negative `n` by dividing **once at the end**.

**Steps.**
1. `negative = n < 0`, `n = abs(n)`, `result = 1.0`.
2. While `n`: if `n & 1`, `result *= x`; `x *= x`; `n >>= 1`.
3. Return `1 / result` if negative, else `result`.

```python
class Solution:
    def myPow(self, x: float, n: int) -> float:
        negative = n < 0
        n = abs(n)
        result = 1.0
        while n:
            if n & 1:
                result *= x
            x *= x
            n >>= 1
        return 1 / result if negative else result
```

**Complexity.** Time O(log n), space O(1).

**Watch out.**
- Invert at the **end**, not the start. `x = 1 / x` first creates a tiny rounding error that gets multiplied by `n` (billions), and fails cases like `x = -0.9999999968539456, n = -1669585506` (191.06373 instead of 191.06370).
- In Java/C++, `-n` overflows for `n = -2³¹`; use a `long`.

```test
assert abs(Solution().myPow(2.0, 10) - 1024.0) < 1e-9
assert abs(Solution().myPow(2.1, 3) - 9.261) < 1e-9
assert abs(Solution().myPow(2.0, -2) - 0.25) < 1e-12
assert f"{Solution().myPow(-0.9999999968539456, -1669585506):.5f}" == "191.06370"
```

### 149. Max Points on a Line
difficulty: Hard

**Problem.** Given points, return the maximum number that lie on one straight line.

**Idea.** For each point `p`, group every other point by the **slope** from `p`. Points with the same slope from `p` are on the same line through `p`. Store the slope as a reduced fraction `(dy, dx)` (divide by the gcd, fix the sign) to avoid floating-point errors.

**Steps.**
1. For each `i`: `count = Counter()`.
2. For each `j > i`: `dx, dy`; divide both by `gcd`; normalize the sign (make `dx > 0`, or `dy > 0` when `dx == 0`); count it.
3. Answer = `max(best, 1 + max(count.values()))`.

```python
class Solution:
    def maxPoints(self, points: List[List[int]]) -> int:
        n = len(points)
        if n <= 2:
            return n
        best = 0
        for i in range(n):
            count = Counter()
            x1, y1 = points[i]
            for j in range(i + 1, n):
                dx = points[j][0] - x1
                dy = points[j][1] - y1
                g = math.gcd(dx, dy)
                dx //= g
                dy //= g
                if dx < 0 or (dx == 0 and dy < 0):
                    dx, dy = -dx, -dy
                count[(dy, dx)] += 1
            if count:
                best = max(best, 1 + max(count.values()))
        return best
```

**Complexity.** Time O(n²), space O(n).

**Watch out.** All points are distinct in this problem, so `dx` and `dy` are never both 0. Using float slopes can merge different lines because of rounding.

```test
assert Solution().maxPoints([[1,1],[2,2],[3,3]]) == 3
assert Solution().maxPoints([[1,1],[3,2],[5,3],[4,1],[2,3],[1,4]]) == 4
assert Solution().maxPoints([[0,0]]) == 1
```

# 1D DP

### 70. Climbing Stairs
difficulty: Easy

**Problem.** You climb 1 or 2 steps at a time. How many distinct ways to reach step `n`?

**Idea.** Your last move was a 1-step from `n-1` or a 2-step from `n-2`, and those groups don't overlap: `ways(n) = ways(n-1) + ways(n-2)` (Fibonacci). Keep only the last two values.

**Steps.**
1. For 1 or 2 stairs the answer is `n`.
2. `ways(i) = ways(i - 1) + ways(i - 2)`: the last move was 1 step or 2 steps.
3. Keep only the last two values: `prev2 = 1` (1 stair), `prev1 = 2` (2 stairs).
4. For `i` from 3 to `n`: `prev2, prev1 = prev1, prev1 + prev2`. Return `prev1`.

```python
class Solution:
    def climbStairs(self, n: int) -> int:
        if n <= 2:
            return n
        prev2, prev1 = 1, 2
        for _ in range(3, n + 1):
            prev2, prev1 = prev1, prev1 + prev2
        return prev1
```

**Complexity.** Time O(n), space O(1).

**Watch out.**
- Plain recursion without memoization is O(2ⁿ).
- With steps 1, 2 or 3 (or any set of step sizes), the same idea: `dp[i] = sum(dp[i - s] for s in steps if i >= s)` with `dp[0] = 1`.

```test
assert Solution().climbStairs(2) == 2
assert Solution().climbStairs(3) == 3
assert Solution().climbStairs(5) == 8
assert Solution().climbStairs(1) == 1
```

### 198. House Robber
difficulty: Medium

**Problem.** Rob houses along a street without robbing two adjacent ones. Maximize the total.

**Example.** `[2,7,9,3,1]` → `12` (2 + 9 + 1).

**Idea.** At each house: **skip** it (keep the best so far) or **rob** it (its money + the best from two houses back). `best(i) = max(best(i-1), best(i-2) + nums[i])`.

**Steps.**
1. Keep `prev1` = best total up to the previous house, `prev2` = best up to two houses back (both start at 0).
2. For each house with money `x`, choose: skip it (`prev1`) or rob it (`prev2 + x`).
3. Shift: `prev2, prev1 = prev1, max(prev1, prev2 + x)`.
4. Return `prev1`.

```python
class Solution:
    def rob(self, nums: List[int]) -> int:
        prev2 = prev1 = 0
        for x in nums:
            prev2, prev1 = prev1, max(prev1, prev2 + x)
        return prev1
```

**Complexity.** Time O(n), space O(1).

**Watch out.** "Take every other house" fails (`[2,1,1,2]` → best is 4 from the first and last). Houses in a circle (House Robber II): run this twice, without the first and without the last house.

```test
assert Solution().rob([1,2,3,1]) == 4
assert Solution().rob([2,7,9,3,1]) == 12
assert Solution().rob([2,1,1,2]) == 4
```

### 139. Word Break
difficulty: Medium

**Problem.** Can `s` be split into a sequence of dictionary words (words can be reused)?

**Example.** `"leetcode", ["leet","code"]` → `true`; `"catsandog", ["cats","dog","sand","and","cat"]` → `false`.

**Idea.** `dp[i]` = "the prefix `s[:i]` can be split". `dp[i]` is true if some `j < i` has `dp[j]` true and `s[j:i]` is a word. `dp[0] = True` (empty prefix).

**Steps.**
1. `words = set(wordDict)`, `max_len` = longest word.
2. For each `i` from 1 to n, try `j` from `i - max_len` to `i - 1`.
3. Return `dp[n]`.

```python
class Solution:
    def wordBreak(self, s: str, wordDict: List[str]) -> bool:
        words = set(wordDict)
        max_len = max(len(w) for w in words)
        n = len(s)
        dp = [False] * (n + 1)
        dp[0] = True
        for i in range(1, n + 1):
            for j in range(max(0, i - max_len), i):
                if dp[j] and s[j:i] in words:
                    dp[i] = True
                    break
        return dp[n]
```

**Complexity.** Time O(n · L²) with L = longest word, space O(n).

**Watch out.**
- `dp = [False] * (n + 1)` needs the brackets; `False * (n + 1)` is just the integer 0.
- Top-down alternative: `can(i)` = some word matches at `i` and `can(i + len(word))`, cached with `lru_cache`.

```py
from functools import lru_cache
@lru_cache(None)
def can(i):
    if i == len(s):
        return True
    return any(s.startswith(w, i) and can(i + len(w)) for w in wordDict)
return can(0)
```

```test
assert Solution().wordBreak("leetcode", ["leet","code"]) is True
assert Solution().wordBreak("applepenapple", ["apple","pen"]) is True
assert Solution().wordBreak("catsandog", ["cats","dog","sand","and","cat"]) is False
```

### 322. Coin Change
difficulty: Medium

**Problem.** Fewest coins (unlimited supply of each denomination) that make up `amount`, or -1.

**Example.** `[1,2,5], 11` → `3` (5 + 5 + 1).

**Idea.** `dp[a]` = fewest coins for amount `a`. The last coin used is some `c`, so `dp[a] = 1 + min(dp[a - c])`. `dp[0] = 0`.

**Steps.**
1. `dp[a]` = fewest coins to make amount `a`. Set `dp[0] = 0` and everything else to `amount + 1` (impossible).
2. For each amount `a` from 1 to `amount`, try every coin `c <= a` as the last coin: `dp[a] = min(dp[a], dp[a - c] + 1)`.
3. If `dp[amount]` is still `amount + 1`, it can't be made → `-1`. Otherwise return it.

```python
class Solution:
    def coinChange(self, coins: List[int], amount: int) -> int:
        INF = amount + 1
        dp = [0] + [INF] * amount
        for a in range(1, amount + 1):
            for c in coins:
                if c <= a and dp[a - c] + 1 < dp[a]:
                    dp[a] = dp[a - c] + 1
        return dp[amount] if dp[amount] != INF else -1
```

**Complexity.** Time O(amount · coins), space O(amount).

**Watch out.** Greedy (always take the largest coin) is wrong in general: coins `[1,3,4]`, amount 6 → greedy gives 4+1+1 (3 coins), best is 3+3 (2 coins).

```test
assert Solution().coinChange([1,2,5], 11) == 3
assert Solution().coinChange([2], 3) == -1
assert Solution().coinChange([1], 0) == 0
assert Solution().coinChange([1,3,4], 6) == 2
```

### 300. Longest Increasing Subsequence
difficulty: Medium

**Problem.** Length of the longest strictly increasing subsequence. Follow-up: O(n log n).

**Example.** `[10,9,2,5,3,7,101,18]` → `4` (`2,3,7,101`).

**Idea (patience sorting).** Keep `tails[k]` = the smallest possible tail of an increasing subsequence of length `k + 1`. `tails` stays sorted. For each number, replace the first tail that is `>= x` (binary search), or append if `x` is bigger than all tails. The length of `tails` is the answer.

**Steps.**
1. `tails[k]` = the smallest possible last number of an increasing subsequence of length `k + 1`.
2. For each `x`, find with `bisect_left` the first tail `>= x`.
3. If there isn't one, `x` extends the longest subsequence: append it.
4. Otherwise replace that tail with `x` (a smaller ending leaves more room to grow).
5. The length of `tails` is the answer.

```python
from bisect import bisect_left

class Solution:
    def lengthOfLIS(self, nums: List[int]) -> int:
        tails = []
        for x in nums:
            i = bisect_left(tails, x)
            if i == len(tails):
                tails.append(x)
            else:
                tails[i] = x
        return len(tails)
```

**Complexity.** Time O(n log n), space O(n).

**Watch out.**
- `tails` is not the actual subsequence, only the right length.
- `bisect_left` keeps it **strictly** increasing (for non-decreasing, use `bisect_right`).
- O(n²) DP to explain first: `dp[i] = 1 + max(dp[j] for j < i if nums[j] < nums[i])`.

```test
assert Solution().lengthOfLIS([10,9,2,5,3,7,101,18]) == 4
assert Solution().lengthOfLIS([0,1,0,3,2,3]) == 4
assert Solution().lengthOfLIS([7,7,7,7]) == 1
```

# Multidimensional DP

### 120. Triangle
difficulty: Medium

**Problem.** Minimum path sum from top to bottom of a triangle, moving to an adjacent number on the row below (index `i` or `i + 1`).

**Example.** `[[2],[3,4],[6,5,7],[4,1,8,3]]` → `11` (2 + 3 + 5 + 1).

**Idea: bottom-up.** Start from the last row. Each cell's best = its value + the smaller of the two cells below it. The top cell ends with the answer.

**Steps.**
1. Copy the bottom row into `dp`.
2. Go up the rows from the second-to-last to the top.
3. For each position `i`: `dp[i] = triangle[row][i] + min(dp[i], dp[i + 1])`, the cheaper of the two cells below.
4. After the top row, `dp[0]` is the minimum path sum.

```python
class Solution:
    def minimumTotal(self, triangle: List[List[int]]) -> int:
        dp = triangle[-1][:]
        for row in range(len(triangle) - 2, -1, -1):
            for i in range(row + 1):
                dp[i] = triangle[row][i] + min(dp[i], dp[i + 1])
        return dp[0]
```

**Complexity.** Time O(n²), space O(n).

**Watch out.** Bottom-up avoids edge cases at both ends of each row that a top-down version must handle.

```test
assert Solution().minimumTotal([[2],[3,4],[6,5,7],[4,1,8,3]]) == 11
assert Solution().minimumTotal([[-10]]) == -10
```

### 64. Minimum Path Sum
difficulty: Medium

**Problem.** Grid of non-negative numbers; move only right or down from top-left to bottom-right. Minimize the sum.

**Idea.** `dp[r][c] = grid[r][c] + min(from top, from left)`. One row of memory is enough.

**Steps.**
1. Keep one row `dp`; `dp[c]` is the best sum to reach column `c` in the current row.
2. Start with `dp[0] = 0` and the rest infinity.
3. For each cell: `dp[c]` (still the value from the row above) is the way from the top; `dp[c - 1]` (already updated) is the way from the left.
4. Set `dp[c] = grid[r][c] + min(top, left)`.
5. Return `dp[-1]`, the bottom-right cell.

```python
class Solution:
    def minPathSum(self, grid: List[List[int]]) -> int:
        m, n = len(grid), len(grid[0])
        dp = [float('inf')] * n
        dp[0] = 0
        for r in range(m):
            for c in range(n):
                left = dp[c - 1] if c > 0 else float('inf')
                dp[c] = grid[r][c] + min(dp[c], left)
        return dp[-1]
```

**Complexity.** Time O(m·n), space O(n).

**Watch out.** Starting with `dp[0] = 0` and the rest infinity handles the first row and column without special cases.

```test
assert Solution().minPathSum([[1,3,1],[1,5,1],[4,2,1]]) == 7
assert Solution().minPathSum([[1,2,3],[4,5,6]]) == 12
```

### 63. Unique Paths II
difficulty: Medium

**Problem.** Count right/down paths from top-left to bottom-right when some cells are obstacles (`1`).

**Idea.** `dp[c]` = number of ways to reach the current cell = ways from above + ways from the left; an obstacle has 0 ways.

**Steps.**
1. `dp[c]` = number of ways to reach column `c` in the current row. Start `dp[0] = 1`.
2. For each row and each column: an obstacle sets `dp[c] = 0`.
3. Otherwise add the ways from the left: `dp[c] += dp[c - 1]` (the old `dp[c]` already counts the ways from above).
4. Return `dp[-1]`.

```python
class Solution:
    def uniquePathsWithObstacles(self, obstacleGrid: List[List[int]]) -> int:
        n = len(obstacleGrid[0])
        dp = [0] * n
        dp[0] = 1
        for row in obstacleGrid:
            for c in range(n):
                if row[c] == 1:
                    dp[c] = 0
                elif c > 0:
                    dp[c] += dp[c - 1]
        return dp[-1]
```

**Complexity.** Time O(m·n), space O(n).

**Watch out.** If the start cell is an obstacle, the first iteration sets `dp[0] = 0` and the answer becomes 0 automatically.

```test
assert Solution().uniquePathsWithObstacles([[0,0,0],[0,1,0],[0,0,0]]) == 2
assert Solution().uniquePathsWithObstacles([[0,1],[0,0]]) == 1
assert Solution().uniquePathsWithObstacles([[1]]) == 0
```

### 5. Longest Palindromic Substring
difficulty: Medium

**Problem.** Return the longest palindromic substring.

**Example.** `"babad"` → `"bab"` (or `"aba"`); `"cbbd"` → `"bb"`.

**Idea: expand around centers.** Every palindrome has a center: a character (odd length) or the gap between two characters (even length). Try all `2n - 1` centers and expand while both sides match.

**Steps.**
1. Every palindrome has a center: one character (odd length) or between two characters (even length).
2. `expand(l, r)`: while both ends are in range and equal, move them outward; return the palindrome's bounds.
3. For each index `i`, expand from `(i, i)` and from `(i, i + 1)`.
4. Keep the longest one found and return that substring.

```python
class Solution:
    def longestPalindrome(self, s: str) -> str:
        def expand(l, r):
            while l >= 0 and r < len(s) and s[l] == s[r]:
                l -= 1
                r += 1
            return l + 1, r            # the palindrome is s[l+1:r]

        start, end = 0, 0
        for i in range(len(s)):
            for l, r in (expand(i, i), expand(i, i + 1)):
                if r - l > end - start:
                    start, end = l, r
        return s[start:end]
```

**Complexity.** Time O(n²), space O(1).

**Watch out.** The DP table version (`dp[i][j] = s[i] == s[j] and dp[i+1][j-1]`) is also O(n²) but uses O(n²) memory. Manacher's algorithm is O(n) but rarely expected.

```test
assert Solution().longestPalindrome("babad") in ("bab", "aba")
assert Solution().longestPalindrome("cbbd") == "bb"
assert Solution().longestPalindrome("a") == "a"
```

### 97. Interleaving String
difficulty: Medium

**Problem.** Is `s3` formed by interleaving `s1` and `s2` (keeping the order of each)?

**Example.** `s1 = "aabcc", s2 = "dbbca", s3 = "aadbbcbcac"` → `true`.

**Idea.** `dp[i][j]` = can `s1[:i]` and `s2[:j]` form `s3[:i+j]`. The last character of `s3[:i+j]` came from `s1` (needs `dp[i-1][j]` and `s1[i-1] == s3[i+j-1]`) or from `s2` (needs `dp[i][j-1]` and `s2[j-1] == s3[i+j-1]`).

**Steps.**
1. If `len(s1) + len(s2) != len(s3)`, return `False`.
2. `dp[j]` (for the current `i`) = can `s1[:i]` and `s2[:j]` interleave into `s3[:i + j]`.
3. Start `dp[0] = True` for empty strings.
4. From `s1`: `dp[j]` (the row above) was True and `s1[i-1] == s3[i+j-1]`. From `s2`: `dp[j-1]` was True and `s2[j-1] == s3[i+j-1]`.
5. `dp[j] = from_s1 or from_s2`. Return `dp[n]`.

```python
class Solution:
    def isInterleave(self, s1: str, s2: str, s3: str) -> bool:
        m, n = len(s1), len(s2)
        if m + n != len(s3):
            return False
        dp = [False] * (n + 1)
        for i in range(m + 1):
            for j in range(n + 1):
                if i == 0 and j == 0:
                    dp[j] = True
                else:
                    from_s1 = i > 0 and dp[j] and s1[i - 1] == s3[i + j - 1]
                    from_s2 = j > 0 and dp[j - 1] and s2[j - 1] == s3[i + j - 1]
                    dp[j] = from_s1 or from_s2
        return dp[n]
```

**Complexity.** Time O(m·n), space O(n).

**Watch out.** A greedy "take from whichever string matches" fails when both match; the DP explores both options.

```test
assert Solution().isInterleave("aabcc", "dbbca", "aadbbcbcac") is True
assert Solution().isInterleave("aabcc", "dbbca", "aadbbbaccc") is False
assert Solution().isInterleave("", "", "") is True
```

### 72. Edit Distance
difficulty: Medium

**Problem.** Minimum insertions, deletions, and replacements to turn `word1` into `word2`.

**Example.** `"horse" → "ros"` → `3`.

**Idea.** `dp[i][j]` = distance between `word1[:i]` and `word2[:j]`. If the last characters match, `dp[i-1][j-1]`. Otherwise 1 + the minimum of replace (`dp[i-1][j-1]`), delete (`dp[i-1][j]`), insert (`dp[i][j-1]`). Base cases: `dp[i][0] = i`, `dp[0][j] = j`.

**Steps.**
1. Table `dp[i][j]` = edits to turn `word1[:i]` into `word2[:j]`.
2. First column `dp[i][0] = i` (delete everything); first row `dp[0][j] = j` (insert everything).
3. If `word1[i-1] == word2[j-1]`, no edit is needed: `dp[i][j] = dp[i-1][j-1]`.
4. Otherwise `1 + min(replace dp[i-1][j-1], delete dp[i-1][j], insert dp[i][j-1])`.
5. Return `dp[m][n]`.

```python
class Solution:
    def minDistance(self, word1: str, word2: str) -> int:
        m, n = len(word1), len(word2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if word1[i - 1] == word2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(dp[i - 1][j - 1], dp[i - 1][j], dp[i][j - 1])
        return dp[m][n]
```

**Complexity.** Time O(m·n), space O(m·n) (can be reduced to one row).

**Watch out.** Off-by-one: `dp` has size `(m+1) × (n+1)`, and position `i` refers to character `word1[i-1]`.

```test
assert Solution().minDistance("horse", "ros") == 3
assert Solution().minDistance("intention", "execution") == 5
assert Solution().minDistance("", "abc") == 3
```

### 123. Best Time to Buy and Sell Stock III
difficulty: Hard

**Problem.** At most **two** transactions (buy then sell, no overlap). Maximize the profit.

**Example.** `[3,3,5,0,0,3,1,4]` → `6`.

**Idea: state machine.** Track the best balance after each stage: `buy1` (bought the first share), `sell1` (sold it), `buy2`, `sell2`. Each day, every state either stays or makes its transition.

**Steps.**
1. Track four values: `buy1` (best balance after the first buy), `sell1`, `buy2`, `sell2`.
2. Each day with price `p`: `buy1 = max(buy1, -p)`.
3. `sell1 = max(sell1, buy1 + p)`.
4. `buy2 = max(buy2, sell1 - p)`: the second buy uses the profit from the first sale.
5. `sell2 = max(sell2, buy2 + p)`. Return `sell2`.

```python
class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        buy1 = buy2 = float('-inf')
        sell1 = sell2 = 0
        for p in prices:
            buy1 = max(buy1, -p)
            sell1 = max(sell1, buy1 + p)
            buy2 = max(buy2, sell1 - p)
            sell2 = max(sell2, buy2 + p)
        return sell2
```

**Complexity.** Time O(n), space O(1).

**Watch out.** Updating in this order within one day is fine: it's like buying and selling on the same day, which adds 0 profit and doesn't break anything.

```test
assert Solution().maxProfit([3,3,5,0,0,3,1,4]) == 6
assert Solution().maxProfit([1,2,3,4,5]) == 4
assert Solution().maxProfit([7,6,4,3,1]) == 0
```

### 188. Best Time to Buy and Sell Stock IV
difficulty: Hard

**Problem.** At most `k` transactions. Maximize the profit.

**Idea.** Generalize #123: arrays `buy[t]` and `sell[t]` for transaction `t = 1..k`. `buy[t] = max(buy[t], sell[t-1] - p)`, `sell[t] = max(sell[t], buy[t] + p)`. If `k >= n // 2`, it's unlimited trades (#122).

**Steps.**
1. If `k >= n // 2`, the limit doesn't matter: add every price increase, like #122.
2. Otherwise keep `buy[t]` and `sell[t]` for each transaction `t = 1..k`.
3. Each day, for `t` from 1 to `k`: `buy[t] = max(buy[t], sell[t-1] - p)`.
4. `sell[t] = max(sell[t], buy[t] + p)`.
5. Return `sell[k]`.

```python
class Solution:
    def maxProfit(self, k: int, prices: List[int]) -> int:
        n = len(prices)
        if k >= n // 2:
            return sum(max(0, prices[i] - prices[i - 1]) for i in range(1, n))
        buy = [float('-inf')] * (k + 1)
        sell = [0] * (k + 1)
        for p in prices:
            for t in range(1, k + 1):
                buy[t] = max(buy[t], sell[t - 1] - p)
                sell[t] = max(sell[t], buy[t] + p)
        return sell[k]
```

**Complexity.** Time O(n·k), space O(k).

**Watch out.** `sell[0] = 0` represents "no transaction yet", the starting balance for the first buy.

```test
assert Solution().maxProfit(2, [2,4,1]) == 2
assert Solution().maxProfit(2, [3,2,6,5,0,3]) == 7
assert Solution().maxProfit(1, [1]) == 0
```

### 221. Maximal Square
difficulty: Medium

**Problem.** In a 0/1 matrix (strings), return the area of the largest square of `'1'`s.

**Idea.** `dp[r][c]` = side of the largest square whose **bottom-right** corner is `(r, c)`. If the cell is `'1'`: `1 + min(top, left, top-left)`, because the square is limited by the smallest of its three neighbour squares.

**Steps.**
1. `dp[c]` = side of the largest all-`'1'` square whose bottom-right corner is in column `c` of the current row.
2. Keep `prev` = the top-left diagonal value (the old `dp[c - 1]` from the row above).
3. For a `'1'` cell: `dp[c] = 1 + min(top dp[c], left dp[c-1], diagonal prev)`. For a `'0'`: `dp[c] = 0`.
4. Track the largest side; return `best * best` (the area).

```python
class Solution:
    def maximalSquare(self, matrix: List[List[str]]) -> int:
        n = len(matrix[0])
        dp = [0] * (n + 1)
        best = 0
        for row in matrix:
            prev = 0                       # dp value top-left of the current cell
            for c in range(1, n + 1):
                tmp = dp[c]
                if row[c - 1] == '1':
                    dp[c] = 1 + min(dp[c], dp[c - 1], prev)
                    best = max(best, dp[c])
                else:
                    dp[c] = 0
                prev = tmp
        return best * best
```

**Complexity.** Time O(m·n), space O(n).

**Watch out.** Return the **area** (`side²`), and compare with the string `'1'`.

```test
assert Solution().maximalSquare([["1","0","1","0","0"],["1","0","1","1","1"],["1","1","1","1","1"],["1","0","0","1","0"]]) == 4
assert Solution().maximalSquare([["0","1"],["1","0"]]) == 1
assert Solution().maximalSquare([["0"]]) == 0
```
