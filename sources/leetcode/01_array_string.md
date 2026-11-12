# Array / String

### 88. Merge Sorted Array
difficulty: Easy

**Problem.** `nums1` has length `m + n`: its first `m` values are sorted, the last `n` slots are zeros (empty space). `nums2` has `n` sorted values. Merge `nums2` into `nums1` **in place** so `nums1` is fully sorted.

**Example.** `nums1 = [1,2,3,0,0,0], m = 3, nums2 = [2,5,6], n = 3` → `nums1 = [1,2,2,3,5,6]`.

**Idea.** Fill `nums1` **from the back**. The largest remaining value of the two arrays goes into the last free slot. Working backward means you never overwrite a value of `nums1` you still need, because the free space is at the end.

**Steps.**
1. `i` points at the last real value of `nums1` (`m - 1`), `j` at the last value of `nums2` (`n - 1`), `k` at the last slot (`m + n - 1`).
2. While `nums2` still has values: put the bigger of `nums1[i]` and `nums2[j]` at `k`, move that pointer and `k` left.
3. If `nums1` runs out first, the loop just copies the rest of `nums2`. If `nums2` runs out first, the rest of `nums1` is already in place.

```python
class Solution:
    def merge(self, nums1: List[int], m: int, nums2: List[int], n: int) -> None:
        i, j, k = m - 1, n - 1, m + n - 1

        while j >= 0:
            if i >= 0 and nums1[i] > nums2[j]:
                nums1[k] = nums1[i]
                i -= 1
            else:
                nums1[k] = nums2[j]
                j -= 1
            k -= 1
```

**Complexity.** Time O(m + n), space O(1).

**Watch out.**
- Loop on `j >= 0` (values left in `nums2`), not on `i`. Leftover `nums1` values are already in the right place.
- The function returns nothing: LeetCode checks `nums1` itself.
- Shortcut (O((m+n) log(m+n))): `nums1[m:] = nums2; nums1.sort()`. Fine to mention, but the two-pointer version is what interviewers want.

```test
a = [1,2,3,0,0,0]; Solution().merge(a, 3, [2,5,6], 3); assert a == [1,2,2,3,5,6]
a = [0]; Solution().merge(a, 0, [1], 1); assert a == [1]
a = [4,5,6,0,0,0]; Solution().merge(a, 3, [1,2,3], 3); assert a == [1,2,3,4,5,6]
```

### 27. Remove Element
difficulty: Easy

**Problem.** Remove every occurrence of `val` from `nums` **in place**, and return `k`, the number of remaining elements. The first `k` slots must hold the kept values (any order); what's after doesn't matter.

**Example.** `nums = [3,2,2,3], val = 3` → `k = 2`, `nums` starts with `[2,2]`.

**Idea.** Two pointers: one **reads** every element, one (`k`) marks where the next **kept** element is **written**.

**Steps.**
1. Start `k = 0`.
2. For each `x` in `nums`: if `x != val`, write it at `nums[k]` and increase `k`.
3. Return `k`.

```python
class Solution:
    def removeElement(self, nums: List[int], val: int) -> int:
        k = 0
        for x in nums:
            if x != val:
                nums[k] = x
                k += 1
        return k
```

**Complexity.** Time O(n), space O(1).

**Watch out.**
- Writing into `nums` while reading it is safe: `k` is never ahead of the read position.
- Variant with fewer writes when `val` is rare: when `nums[i] == val`, copy the last element into slot `i` and shrink the length, **without** moving `i` (the copied value might also be `val`).

```py
i, n = 0, len(nums)
while i < n:
    if nums[i] == val:
        nums[i] = nums[n - 1]
        n -= 1
    else:
        i += 1
return n
```

```test
a = [3,2,2,3]; k = Solution().removeElement(a, 3); assert k == 2 and sorted(a[:k]) == [2,2]
a = [0,1,2,2,3,0,4,2]; k = Solution().removeElement(a, 2); assert k == 5 and sorted(a[:k]) == [0,0,1,3,4]
a = []; assert Solution().removeElement(a, 1) == 0
```

### 26. Remove Duplicates from Sorted Array
difficulty: Easy

**Problem.** `nums` is sorted. Remove duplicates **in place** so each value appears once, keeping the order, and return the number of unique values `k`.

**Example.** `[0,0,1,1,1,2,2,3,3,4]` → `k = 5`, `nums` starts with `[0,1,2,3,4]`.

**Idea.** Because the array is sorted, duplicates sit next to each other. A value is new exactly when it differs from the **last kept** value. Keep a write pointer `i` on the last unique value.

**Steps.**
1. `i = 0` (the first element is always kept).
2. For `j` from 1 to the end: if `nums[j] != nums[i]`, move `i` forward and copy `nums[j]` there.
3. Return `i + 1`.

```python
class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        i = 0
        for j in range(1, len(nums)):
            if nums[j] != nums[i]:
                i += 1
                nums[i] = nums[j]
        return i + 1
```

**Complexity.** Time O(n), space O(1).

**Watch out.** Increase `i` **before** writing. Writing first would overwrite the last unique value. (In C, that's `nums[++i]`, not `nums[i++]`.)

```test
a = [1,1,2]; k = Solution().removeDuplicates(a); assert k == 2 and a[:k] == [1,2]
a = [0,0,1,1,1,2,2,3,3,4]; k = Solution().removeDuplicates(a); assert k == 5 and a[:k] == [0,1,2,3,4]
```

### 80. Remove Duplicates from Sorted Array II
difficulty: Medium

**Problem.** Like #26, but each value may appear **at most twice**. In place, O(1) extra memory. Return `k`.

**Example.** `[1,1,1,2,2,3]` → `k = 5`, `nums` starts with `[1,1,2,2,3]`.

**Idea.** Keep a write pointer `k`. A new value may be kept if it differs from the element **two places back in the kept part** (`nums[k - 2]`). Since the array is sorted, if `nums[k - 2]` equals it, `nums[k - 1]` does too, so it would be a third copy.

**Steps.**
1. `k = 0`.
2. For each `x`: if `k < 2` or `x != nums[k - 2]`, write `nums[k] = x` and increase `k`.
3. Return `k`.

```python
class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        k = 0
        for x in nums:
            if k < 2 or x != nums[k - 2]:
                nums[k] = x
                k += 1
        return k
```

**Complexity.** Time O(n), space O(1).

**Watch out.**
- Compare with the **kept** part (`nums[k - 2]`), not with `nums[i - 2]` of the original array.
- General rule: to allow at most `m` copies, replace both 2s with `m`. With `m = 1` this is problem #26.

```test
a = [1,1,1,2,2,3]; k = Solution().removeDuplicates(a); assert k == 5 and a[:k] == [1,1,2,2,3]
a = [0,0,1,1,1,1,2,3,3]; k = Solution().removeDuplicates(a); assert k == 7 and a[:k] == [0,0,1,1,2,3,3]
```

### 169. Majority Element
difficulty: Easy

**Problem.** Return the element that appears **more than n/2 times** (it always exists). Follow-up: O(n) time and O(1) space.

**Example.** `[2,2,1,1,1,2,2]` → `2`.

**Idea: Boyer–Moore voting.** Keep a `candidate` and a `count`. Equal numbers vote +1, different numbers vote −1. When the count drops to 0, the next number becomes the candidate. The majority has more copies than all other values combined, so it can't be fully cancelled out and is the candidate at the end.

**Steps.**
1. `candidate = None`, `count = 0`.
2. For each `x`: if `count == 0`, set `candidate = x`. Then `count += 1` if `x == candidate`, else `count -= 1`.
3. Return `candidate`.

```python
class Solution:
    def majorityElement(self, nums: List[int]) -> int:
        candidate, count = None, 0
        for x in nums:
            if count == 0:
                candidate = x
            count += 1 if x == candidate else -1
        return candidate
```

**Complexity.** Time O(n), space O(1).

**Watch out.**
- Only correct because a majority is **guaranteed**. Without that guarantee, do a second pass to confirm the candidate's count.
- Simpler alternatives: `Counter(nums).most_common(1)[0][0]` (O(n) space) or `sorted(nums)[len(nums) // 2]` (the majority always covers the middle, O(n log n)).

```test
assert Solution().majorityElement([3,2,3]) == 3
assert Solution().majorityElement([2,2,1,1,1,2,2]) == 2
assert Solution().majorityElement([1]) == 1
```

### 189. Rotate Array
difficulty: Medium

**Problem.** Rotate `nums` to the right by `k` steps, in place.

**Example.** `[1,2,3,4,5,6,7], k = 3` → `[5,6,7,1,2,3,4]`.

**Idea: three reversals.** Rotating right by `k` moves the last `k` elements to the front. Reverse the whole array (the last `k` are now at the front, but backwards), then reverse the first `k` and the rest separately to fix their order.

**Steps.**
1. `k %= n` (rotating by `n` changes nothing).
2. Reverse all of `nums`.
3. Reverse `nums[0:k]`, then reverse `nums[k:n]`.

```python
class Solution:
    def rotate(self, nums: List[int], k: int) -> None:
        n = len(nums)
        k %= n

        def reverse(l, r):
            while l < r:
                nums[l], nums[r] = nums[r], nums[l]
                l += 1
                r -= 1

        reverse(0, n - 1)
        reverse(0, k - 1)
        reverse(k, n - 1)
```

**Complexity.** Time O(n), space O(1).

**Watch out.**
- Always do `k %= n` first: `k` can be larger than the array.
- Pythonic version (O(n) extra space): `nums[:] = nums[-k:] + nums[:-k]` after `k %= n`. Note `nums[:] =` changes the list in place; `nums =` would only rebind the local name and LeetCode would see no change.
- Trace: `[1..7]` → reversed `[7,6,5,4,3,2,1]` → first 3 reversed `[5,6,7,4,3,2,1]` → rest reversed `[5,6,7,1,2,3,4]`.

```test
a = [1,2,3,4,5,6,7]; Solution().rotate(a, 3); assert a == [5,6,7,1,2,3,4]
a = [-1,-100,3,99]; Solution().rotate(a, 2); assert a == [3,99,-1,-100]
a = [1,2]; Solution().rotate(a, 5); assert a == [2,1]
```

### 121. Best Time to Buy and Sell Stock
difficulty: Easy

**Problem.** `prices[i]` is the price on day `i`. Buy once and sell once later. Return the maximum profit (0 if no profit is possible).

**Example.** `[7,1,5,3,6,4]` → `5` (buy at 1, sell at 6).

**Idea.** For each day, the best sale that day is `price - (lowest price seen before it)`. Track the minimum so far and the best profit so far in one pass.

**Steps.**
1. `min_price = infinity`, `best = 0`.
2. For each price: update `min_price`, then update `best = max(best, price - min_price)`.
3. Return `best`.

```python
class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        min_price = float('inf')
        best = 0
        for p in prices:
            min_price = min(min_price, p)
            best = max(best, p - min_price)
        return best
```

**Complexity.** Time O(n), space O(1).

**Watch out.** You can't sell before buying, which is why you only compare with the minimum **so far**, not the global minimum.

```test
assert Solution().maxProfit([7,1,5,3,6,4]) == 5
assert Solution().maxProfit([7,6,4,3,1]) == 0
```

### 122. Best Time to Buy and Sell Stock II
difficulty: Medium

**Problem.** Same prices, but you may buy and sell **as many times as you want** (hold at most one share at a time). Return the maximum profit.

**Example.** `[7,1,5,3,6,4]` → `7` (1→5 gives 4, 3→6 gives 3).

**Idea: greedy.** Any rise from one day to the next can be captured. A long climb from 1 to 6 earns the same as all the small daily rises added together. So add every positive day-to-day difference.

**Steps.**
1. `profit = 0`.
2. For each day `i ≥ 1`: if `prices[i] > prices[i-1]`, add the difference.
3. Return `profit`.

```python
class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        profit = 0
        for i in range(1, len(prices)):
            if prices[i] > prices[i - 1]:
                profit += prices[i] - prices[i - 1]
        return profit
```

**Complexity.** Time O(n), space O(1).

**Watch out.** The greedy sum doesn't mean you actually trade every day; it equals the profit of buying at each valley and selling at each peak.

```test
assert Solution().maxProfit([7,1,5,3,6,4]) == 7
assert Solution().maxProfit([1,2,3,4,5]) == 4
assert Solution().maxProfit([7,6,4,3,1]) == 0
```

### 55. Jump Game
difficulty: Medium

**Problem.** `nums[i]` is the maximum jump length from index `i`. Starting at index 0, can you reach the last index?

**Example.** `[2,3,1,1,4]` → `true`; `[3,2,1,0,4]` → `false` (every path gets stuck on the 0).

**Idea: greedy reach.** Track `reach`, the farthest index reachable so far. Walk left to right; if you ever stand at an index beyond `reach`, you're stuck.

**Steps.**
1. `reach = 0`.
2. For each index `i`: if `i > reach`, return false. Otherwise `reach = max(reach, i + nums[i])`.
3. If the loop finishes, return true.

```python
class Solution:
    def canJump(self, nums: List[int]) -> bool:
        reach = 0
        for i, step in enumerate(nums):
            if i > reach:
                return False
            reach = max(reach, i + step)
        return True
```

**Complexity.** Time O(n), space O(1).

**Watch out.** You don't need to know the actual path, only how far you can get. Can also stop early once `reach >= len(nums) - 1`.

```test
assert Solution().canJump([2,3,1,1,4]) is True
assert Solution().canJump([3,2,1,0,4]) is False
assert Solution().canJump([0]) is True
```

### 45. Jump Game II
difficulty: Medium

**Problem.** Same jumps as #55, but the end is always reachable. Return the **minimum number of jumps** to reach the last index.

**Example.** `[2,3,1,1,4]` → `2` (0 → 1 → 4).

**Idea: BFS by levels, done greedily.** All indexes reachable with `j` jumps form a range. While scanning that range, compute the farthest point reachable with one more jump. When you reach the end of the current range, you must jump: count it and the next range ends at that farthest point.

**Steps.**
1. `jumps = 0`, `end = 0` (end of the current range), `farthest = 0`.
2. For `i` from 0 to `n - 2`: `farthest = max(farthest, i + nums[i])`. If `i == end`: `jumps += 1`, `end = farthest`.
3. Return `jumps`.

```python
class Solution:
    def jump(self, nums: List[int]) -> int:
        jumps = end = farthest = 0
        for i in range(len(nums) - 1):
            farthest = max(farthest, i + nums[i])
            if i == end:
                jumps += 1
                end = farthest
        return jumps
```

**Complexity.** Time O(n), space O(1).

**Watch out.** Loop only to `n - 2`: once you're at the last index you don't jump again. Looping to `n - 1` would add one extra jump when the last range ends exactly at the last index.

```test
assert Solution().jump([2,3,1,1,4]) == 2
assert Solution().jump([2,3,0,1,4]) == 2
assert Solution().jump([0]) == 0
assert Solution().jump([1,2]) == 1
```

### 274. H-Index
difficulty: Medium

**Problem.** `citations[i]` is the number of citations of paper `i`. The h-index is the largest `h` such that at least `h` papers have at least `h` citations each.

**Example.** `[3,0,6,1,5]` → `3` (three papers have ≥ 3 citations).

**Idea.** Sort citations in **descending** order. The paper at position `i` (0-based) is the `(i+1)`-th most cited. As long as `citations[i] >= i + 1`, there are `i + 1` papers with at least `i + 1` citations.

**Steps.**
1. Sort descending.
2. Walk `i` from 0; while `citations[i] >= i + 1`, `h = i + 1`.
3. Return `h`.

```python
class Solution:
    def hIndex(self, citations: List[int]) -> int:
        citations.sort(reverse=True)
        h = 0
        for i, c in enumerate(citations):
            if c >= i + 1:
                h = i + 1
            else:
                break
        return h
```

**Complexity.** Time O(n log n), space O(1) extra (besides the sort).

**Watch out.** O(n) version with counting: the answer is at most `n`, so count papers per citation value (capping at `n`), then walk from `n` down, adding counts until the total reaches the current value.

```py
n = len(citations)
count = [0] * (n + 1)
for c in citations:
    count[min(c, n)] += 1
total = 0
for h in range(n, -1, -1):
    total += count[h]
    if total >= h:
        return h
```

```test
assert Solution().hIndex([3,0,6,1,5]) == 3
assert Solution().hIndex([1,3,1]) == 1
assert Solution().hIndex([0]) == 0
assert Solution().hIndex([100]) == 1
```

### 380. Insert Delete GetRandom O(1)
difficulty: Medium

**Problem.** Design `RandomizedSet` with `insert(val)`, `remove(val)` (each returning whether it changed the set) and `getRandom()` (each element equally likely), all in **average O(1)**.

**Idea.** A list gives O(1) random access (`random.choice`), and a dict gives O(1) lookup. Store the values in a list and map each value to its index in a dict. To remove in O(1), **swap** the value with the last element, then pop the end.

**Steps.**
1. `insert`: if present, return false. Else append to the list and record its index.
2. `remove`: if absent, return false. Else move the last value into the removed value's slot, update its index, pop the list, delete the key.
3. `getRandom`: `random.choice(list)`.

```python
import random

class RandomizedSet:
    def __init__(self):
        self.vals = []
        self.pos = {}           # value -> index in self.vals

    def insert(self, val: int) -> bool:
        if val in self.pos:
            return False
        self.pos[val] = len(self.vals)
        self.vals.append(val)
        return True

    def remove(self, val: int) -> bool:
        if val not in self.pos:
            return False
        i = self.pos[val]
        last = self.vals[-1]
        self.vals[i] = last         # move the last value into the hole
        self.pos[last] = i
        self.vals.pop()
        del self.pos[val]
        return True

    def getRandom(self) -> int:
        return random.choice(self.vals)
```

**Complexity.** Each operation is O(1) on average; space O(n).

**Watch out.** Update `pos[last]` **before** deleting `pos[val]`. When `val` is itself the last element, the order matters: setting then deleting the same key leaves it correctly removed.

```test
s = RandomizedSet()
assert s.insert(1) is True and s.remove(2) is False and s.insert(2) is True
assert s.getRandom() in (1, 2)
assert s.remove(1) is True and s.insert(2) is False and s.getRandom() == 2
s2 = RandomizedSet(); s2.insert(5); assert s2.remove(5) is True and s2.vals == [] and s2.pos == {}
```

### 238. Product of Array Except Self
difficulty: Medium

**Problem.** Return `answer` where `answer[i]` is the product of all elements except `nums[i]`, in O(n) **without using division**.

**Example.** `[1,2,3,4]` → `[24,12,8,6]`.

**Idea.** The product of everything except `i` = (product of everything **left** of `i`) × (product of everything **right** of `i`). Compute left products in one pass, then multiply by right products in a second pass going backward.

**Steps.**
1. `answer[i] =` product of `nums[0..i-1]` (start with 1).
2. Walk backward keeping `right` = product of `nums[i+1..]`; multiply `answer[i] *= right`, then `right *= nums[i]`.

```python
class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        n = len(nums)
        answer = [1] * n

        left = 1
        for i in range(n):
            answer[i] = left
            left *= nums[i]

        right = 1
        for i in range(n - 1, -1, -1):
            answer[i] *= right
            right *= nums[i]

        return answer
```

**Complexity.** Time O(n), space O(1) extra (the output array doesn't count).

**Watch out.** Division (`total // nums[i]`) is forbidden and also breaks when there's a 0 in the array.

```test
assert Solution().productExceptSelf([1,2,3,4]) == [24,12,8,6]
assert Solution().productExceptSelf([-1,1,0,-3,3]) == [0,0,9,0,0]
```

### 134. Gas Station
difficulty: Medium

**Problem.** Stations in a circle: `gas[i]` fuel available at station `i`, `cost[i]` fuel needed to drive to station `i+1`. Return the starting station from which you can travel around once, or `-1`. The answer is unique if it exists.

**Example.** `gas = [1,2,3,4,5], cost = [3,4,5,1,2]` → `3`.

**Idea.**
1. If total gas < total cost, it's impossible.
2. Otherwise, drive from station 0 keeping a running `tank`. If the tank goes negative at station `i`, **no station between the current start and `i`** can be the start either (they'd arrive at `i` with even less fuel). So restart at `i + 1` with an empty tank.

**Steps.**
1. If `sum(gas) < sum(cost)`, return -1.
2. `start = 0`, `tank = 0`. For each `i`: `tank += gas[i] - cost[i]`; if `tank < 0`, set `start = i + 1` and `tank = 0`.
3. Return `start`.

```python
class Solution:
    def canCompleteCircuit(self, gas: List[int], cost: List[int]) -> int:
        if sum(gas) < sum(cost):
            return -1

        start = tank = 0
        for i in range(len(gas)):
            tank += gas[i] - cost[i]
            if tank < 0:
                start = i + 1
                tank = 0
        return start
```

**Complexity.** Time O(n), space O(1).

**Watch out.** You don't need to check the wrap-around part: if the total is enough and no earlier start works, the last restart point is guaranteed to work.

```test
assert Solution().canCompleteCircuit([1,2,3,4,5], [3,4,5,1,2]) == 3
assert Solution().canCompleteCircuit([2,3,4], [3,4,3]) == -1
assert Solution().canCompleteCircuit([5,1,2,3,4], [4,4,1,5,1]) == 4
```

### 135. Candy
difficulty: Hard

**Problem.** Children in a line have ratings. Each child gets at least 1 candy, and a child with a **higher** rating than a neighbour must get **more** candy than that neighbour. Return the minimum total.

**Example.** `[1,0,2]` → `5` (candies `[2,1,2]`).

**Idea: two passes.** Handle each neighbour rule separately:
- Left pass: if `ratings[i] > ratings[i-1]`, give `candies[i-1] + 1`.
- Right pass: if `ratings[i] > ratings[i+1]`, make sure `candies[i] >= candies[i+1] + 1` (use `max` so the left rule isn't broken).

**Steps.**
1. `candies = [1] * n`.
2. Left to right: apply the left-neighbour rule.
3. Right to left: apply the right-neighbour rule with `max`.
4. Return the sum.

```python
class Solution:
    def candy(self, ratings: List[int]) -> int:
        n = len(ratings)
        candies = [1] * n

        for i in range(1, n):
            if ratings[i] > ratings[i - 1]:
                candies[i] = candies[i - 1] + 1

        for i in range(n - 2, -1, -1):
            if ratings[i] > ratings[i + 1]:
                candies[i] = max(candies[i], candies[i + 1] + 1)

        return sum(candies)
```

**Complexity.** Time O(n), space O(n).

**Watch out.** Equal ratings have **no** constraint, so a child next to an equal neighbour can get just 1. Without `max` in the second pass, you'd overwrite a bigger value set by the first pass.

```test
assert Solution().candy([1,0,2]) == 5
assert Solution().candy([1,2,2]) == 4
assert Solution().candy([1,3,2,2,1]) == 7
```

### 42. Trapping Rain Water
difficulty: Hard

**Problem.** Bars of width 1 with heights `height[i]`. How much rain water is trapped between them?

**Example.** `[0,1,0,2,1,0,1,3,2,1,2,1]` → `6`.

**Idea.** Water above bar `i` = `min(tallest bar on its left, tallest on its right) - height[i]`. With two pointers from both ends, you always know which side is the limiting one: move the side with the **smaller max**, because its water level is decided by that smaller max (the other side is guaranteed to be at least as tall).

**Steps.**
1. `l = 0`, `r = n - 1`, `left_max = right_max = 0`, `water = 0`.
2. While `l < r`: if `height[l] < height[r]`, update `left_max`, add `left_max - height[l]`, move `l` right. Else do the same on the right side.
3. Return `water`.

```python
class Solution:
    def trap(self, height: List[int]) -> int:
        l, r = 0, len(height) - 1
        left_max = right_max = 0
        water = 0

        while l < r:
            if height[l] < height[r]:
                left_max = max(left_max, height[l])
                water += left_max - height[l]
                l += 1
            else:
                right_max = max(right_max, height[r])
                water += right_max - height[r]
                r -= 1

        return water
```

**Complexity.** Time O(n), space O(1).

**Watch out.** Easier-to-explain version (O(n) space): precompute `left_max[i]` and `right_max[i]` arrays, then sum `min(left_max[i], right_max[i]) - height[i]`. Start with that in an interview, then improve to two pointers.

```test
assert Solution().trap([0,1,0,2,1,0,1,3,2,1,2,1]) == 6
assert Solution().trap([4,2,0,3,2,5]) == 9
assert Solution().trap([1]) == 0
```

### 13. Roman to Integer
difficulty: Easy

**Problem.** Convert a Roman numeral string (I, V, X, L, C, D, M) to an integer.

**Example.** `"MCMXCIV"` → `1994`.

**Idea.** Add each symbol's value, except when a symbol is **smaller than the next one** (like the I in IV, or the C in CM), in which case subtract it.

**Steps.**
1. Map symbols to values.
2. For each index `i`: if the next symbol is bigger, subtract this value; otherwise add it.

```python
class Solution:
    def romanToInt(self, s: str) -> int:
        val = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        total = 0
        for i, ch in enumerate(s):
            if i + 1 < len(s) and val[ch] < val[s[i + 1]]:
                total -= val[ch]
            else:
                total += val[ch]
        return total
```

**Complexity.** Time O(n), space O(1).

**Watch out.** Trace `"MCMXCIV"`: M +1000, C −100 (before M), M +1000, X −10, C +100, I −1, V +5 → 1994.

```test
assert Solution().romanToInt("III") == 3
assert Solution().romanToInt("LVIII") == 58
assert Solution().romanToInt("MCMXCIV") == 1994
```

### 12. Integer to Roman
difficulty: Medium

**Problem.** Convert an integer (1 to 3999) to a Roman numeral.

**Example.** `1994` → `"MCMXCIV"`.

**Idea: greedy with a table.** List the values from largest to smallest, **including the subtractive pairs** (900 = CM, 400 = CD, 90, 40, 9, 4). Repeatedly take the largest value that still fits.

**Steps.**
1. Table of 13 (value, symbol) pairs, largest first.
2. For each pair: while `num >= value`, append the symbol and subtract.

```python
class Solution:
    def intToRoman(self, num: int) -> str:
        table = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
                 (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
                 (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]
        out = []
        for value, sym in table:
            while num >= value:
                out.append(sym)
                num -= value
        return ''.join(out)
```

**Complexity.** O(1): the number is bounded (at most 15 symbols).

**Watch out.** Including the six subtractive pairs in the table is what makes greedy correct; without them, 4 would become `IIII`.

```test
assert Solution().intToRoman(3749) == "MMMDCCXLIX"
assert Solution().intToRoman(58) == "LVIII"
assert Solution().intToRoman(1994) == "MCMXCIV"
```

### 58. Length of Last Word
difficulty: Easy

**Problem.** Return the length of the last word in a string of words and spaces (there may be extra spaces, including at the end).

**Example.** `"   fly me   to   the moon  "` → `4`.

**Idea.** Scan from the end: skip trailing spaces, then count characters until a space or the start.

**Steps.**
1. `i = len(s) - 1`; move left while `s[i] == ' '`.
2. Count while `i >= 0` and `s[i] != ' '`.

```python
class Solution:
    def lengthOfLastWord(self, s: str) -> int:
        i = len(s) - 1
        while i >= 0 and s[i] == ' ':
            i -= 1
        length = 0
        while i >= 0 and s[i] != ' ':
            length += 1
            i -= 1
        return length
```

**Complexity.** Time O(n) worst case (only reads the end of the string), space O(1).

**Watch out.**
- One-liner: `len(s.split()[-1])`. Use `split()` (any whitespace, drops empties), **not** `split(' ')`, which leaves empty strings at the end.
- Check `i >= 0` before `s[i]`: in Python `s[-1]` silently reads the last character.

```test
assert Solution().lengthOfLastWord("Hello World") == 5
assert Solution().lengthOfLastWord("   fly me   to   the moon  ") == 4
assert Solution().lengthOfLastWord("luffy is still joyboy") == 6
assert Solution().lengthOfLastWord("a") == 1
```

### 14. Longest Common Prefix
difficulty: Easy

**Problem.** Return the longest prefix shared by all strings (or `""`).

**Example.** `["flower","flow","flight"]` → `"fl"`.

**Idea: vertical scan.** Use the first string as reference and compare column by column; stop at the first column where some string is too short or has a different character.

**Steps.**
1. For each index `i` and character `ch` of `strs[0]`:
2. For every other string `s`: if `i == len(s)` or `s[i] != ch`, return `strs[0][:i]`.
3. If the loop ends, the whole first string is the prefix.

```python
class Solution:
    def longestCommonPrefix(self, strs: List[str]) -> str:
        first = strs[0]
        for i, ch in enumerate(first):
            for s in strs[1:]:
                if i == len(s) or s[i] != ch:
                    return first[:i]
        return first
```

**Complexity.** Time O(total characters), space O(1).

**Watch out.**
- Check `i == len(s)` **before** `s[i]`.
- Pythonic alternative: `zip(*strs)` gives the columns; stop at the first column whose `set` has more than one character.

```test
assert Solution().longestCommonPrefix(["flower","flow","flight"]) == "fl"
assert Solution().longestCommonPrefix(["dog","racecar","car"]) == ""
assert Solution().longestCommonPrefix(["ab", "a"]) == "a"
assert Solution().longestCommonPrefix([""]) == ""
```

### 151. Reverse Words in a String
difficulty: Medium

**Problem.** Reverse the order of the words. The input may have leading, trailing, or multiple spaces; the output must have single spaces only.

**Example.** `"  hello world  "` → `"world hello"`.

**Idea.** `split()` with no argument splits on runs of whitespace and drops empty pieces, so it cleans all the extra spaces. Reverse the list and join with one space.

**Steps.**
1. `s.split()` (no argument) splits on any run of spaces and drops empty pieces, so leading, trailing and repeated spaces disappear.
2. `reversed(...)` walks the list of words from last to first.
3. `' '.join(...)` puts exactly one space between the words. Return it.

```python
class Solution:
    def reverseWords(self, s: str) -> str:
        return ' '.join(reversed(s.split()))
```

**Steps (manual version, if built-ins aren't allowed).**
1. Walk from the end, skipping spaces.
2. When you find a word's last character, walk left to its start and copy the word.
3. Join the collected words with single spaces.

```python
class Solution:
    def reverseWords(self, s: str) -> str:
        words = []
        i = len(s) - 1
        while i >= 0:
            while i >= 0 and s[i] == ' ':
                i -= 1
            if i < 0:
                break
            j = i
            while j >= 0 and s[j] != ' ':
                j -= 1
            words.append(s[j + 1:i + 1])
            i = j
        return ' '.join(words)
```

**Complexity.** Time O(n), space O(n).

**Watch out.** `split(' ')` would keep empty strings for repeated spaces and give extra spaces in the output.

```test
assert Solution().reverseWords("the sky is blue") == "blue is sky the"
assert Solution().reverseWords("  hello world  ") == "world hello"
assert Solution().reverseWords("a good   example") == "example good a"
```

### 6. Zigzag Conversion
difficulty: Medium

**Problem.** Write `s` in a zigzag over `numRows` rows (down, then diagonally up, repeat) and read the rows line by line.

**Example.** `"PAYPALISHIRING", numRows = 3` → `"PAHNAPLSIIGYIR"`.
```
P   A   H   N
A P L S I I G
Y   I   R
```

**Idea.** Simulate: keep one string per row and a current row that moves down then up. Flip direction at the top and bottom rows.

**Steps.**
1. If `numRows == 1`, return `s` (no zigzag).
2. `rows = [''] * numRows`, `row = 0`, `step = 1`.
3. For each character: add it to `rows[row]`; if `row` is 0 set `step = 1`, if it's the last row set `step = -1`; `row += step`.
4. Join the rows.

```python
class Solution:
    def convert(self, s: str, numRows: int) -> str:
        if numRows == 1 or numRows >= len(s):
            return s
        rows = [''] * numRows
        row, step = 0, 1
        for ch in s:
            rows[row] += ch
            if row == 0:
                step = 1
            elif row == numRows - 1:
                step = -1
            row += step
        return ''.join(rows)
```

**Complexity.** Time O(n), space O(n).

**Watch out.** `numRows == 1` must be handled first, otherwise `step` flips every character and `row` goes out of range.

```test
assert Solution().convert("PAYPALISHIRING", 3) == "PAHNAPLSIIGYIR"
assert Solution().convert("PAYPALISHIRING", 4) == "PINALSIGYAHRPI"
assert Solution().convert("A", 1) == "A"
assert Solution().convert("AB", 1) == "AB"
```

### 28. Find the Index of the First Occurrence in a String
difficulty: Easy

**Problem.** Return the index of the first occurrence of `needle` in `haystack`, or `-1`.

**Example.** `haystack = "sadbutsad", needle = "sad"` → `0`.

**Idea.** Try every starting position where the needle still fits, and compare the window with the needle.

**Steps.**
1. `m = len(needle)`.
2. For `i` in `range(len(haystack) - m + 1)`: if `haystack[i:i+m] == needle`, return `i`.
3. Return -1.

```python
class Solution:
    def strStr(self, haystack: str, needle: str) -> int:
        m = len(needle)
        for i in range(len(haystack) - m + 1):
            if haystack[i:i + m] == needle:
                return i
        return -1
```

**Complexity.** Time O(n·m) worst case, space O(m) for the slice.

**Watch out.**
- The `+ 1` in the range is because `range` excludes its end; `len(haystack) - m` is the last start where the needle fits.
- Built-in: `haystack.find(needle)` returns exactly this.
- Guaranteed O(n + m): KMP. Precompute `lps[i]` (longest proper prefix of `needle[:i+1]` that's also a suffix) and never move backward in `haystack`.

```py
lps = [0] * m
length = 0
for i in range(1, m):
    while length and needle[i] != needle[length]:
        length = lps[length - 1]
    if needle[i] == needle[length]:
        length += 1
    lps[i] = length
j = 0
for i, ch in enumerate(haystack):
    while j and ch != needle[j]:
        j = lps[j - 1]
    if ch == needle[j]:
        j += 1
    if j == m:
        return i - m + 1
return -1
```

```test
assert Solution().strStr("sadbutsad", "sad") == 0
assert Solution().strStr("leetcode", "leeto") == -1
assert Solution().strStr("hello", "ll") == 2
assert Solution().strStr("a", "aa") == -1
```

### 68. Text Justification
difficulty: Hard

**Problem.** Format `words` into lines of exactly `maxWidth` characters, fully justified: put as many words as fit on each line, spread spaces as evenly as possible (extra spaces go to the **left** gaps first). The **last line** and lines with a **single word** are left-justified (padded with spaces on the right).

**Example.** `["This","is","an","example","of","text","justification."], 16` →
```
"This    is    an"
"example  of text"
"justification.  "
```

**Idea.** Greedily take words while they fit (the words' letters plus at least one space between each). Then build the line: total spaces = `maxWidth - letters`, divided among `gaps = words - 1`; each gap gets `spaces // gaps`, and the first `spaces % gaps` gaps get one extra.

**Steps.**
1. `i = 0`. Collect words `i..j-1` while `letters + (count of words) + len(next word) <= maxWidth`.
2. If it's the last line or there's one word: join with single spaces and pad the right.
3. Otherwise distribute spaces as above.
4. Continue from `j`.

```python
class Solution:
    def fullJustify(self, words: List[str], maxWidth: int) -> List[str]:
        res = []
        i = 0
        while i < len(words):
            j = i
            letters = 0
            # take words while: letters + one space per gap + new word fits
            while j < len(words) and letters + len(words[j]) + (j - i) <= maxWidth:
                letters += len(words[j])
                j += 1

            line_words = words[i:j]
            gaps = j - i - 1
            if j == len(words) or gaps == 0:
                line = ' '.join(line_words)
                line += ' ' * (maxWidth - len(line))
            else:
                spaces = maxWidth - letters
                base, extra = divmod(spaces, gaps)
                line = ''
                for k, w in enumerate(line_words[:-1]):
                    line += w + ' ' * (base + (1 if k < extra else 0))
                line += line_words[-1]
            res.append(line)
            i = j
        return res
```

**Complexity.** Time O(total characters), space O(maxWidth) per line.

**Watch out.** The fit check `letters + len(words[j]) + (j - i)` counts one space for each gap that would exist if `words[j]` is added (there are `j - i` gaps then).

```test
assert Solution().fullJustify(["This","is","an","example","of","text","justification."], 16) == ["This    is    an","example  of text","justification.  "]
assert Solution().fullJustify(["What","must","be","acknowledgment","shall","be"], 16) == ["What   must   be","acknowledgment  ","shall be        "]
```
