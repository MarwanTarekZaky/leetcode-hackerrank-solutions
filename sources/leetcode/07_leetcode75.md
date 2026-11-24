# LeetCode 75 (problems not in the other two lists)

### 1768. Merge Strings Alternately
difficulty: Easy

**Problem.** Merge two strings by taking letters alternately, starting with `word1`. If one string is longer, append the rest of it at the end.

**Example.** `word1 = "ab", word2 = "pqrs"` → `"apbqrs"`.

**Idea.** Walk an index `i` up to the longer length and take `word1[i]` and `word2[i]` when they exist.

**Steps.**
1. Loop `i` from 0 to `max(len(word1), len(word2)) - 1`.
2. If `i` is inside `word1`, add `word1[i]`; then the same for `word2`.
3. Join the collected letters.

```python
class Solution:
    def mergeAlternately(self, word1: str, word2: str) -> str:
        out = []
        for i in range(max(len(word1), len(word2))):
            if i < len(word1):
                out.append(word1[i])
            if i < len(word2):
                out.append(word2[i])
        return "".join(out)
```

**Complexity.** Time O(m + n), space O(m + n) for the result.

**Watch out.** Build a list and `"".join` it once. Repeated `s += ch` can be quadratic in other languages.

```test
assert Solution().mergeAlternately("abc", "pqr") == "apbqcr"
assert Solution().mergeAlternately("ab", "pqrs") == "apbqrs"
assert Solution().mergeAlternately("abcd", "pq") == "apbqcd"
```

### 1071. Greatest Common Divisor of Strings
difficulty: Easy

**Problem.** `t` divides `s` if `s` is `t` repeated one or more times. Return the longest string that divides both `str1` and `str2`.

**Example.** `str1 = "ABABAB", str2 = "ABAB"` → `"AB"`.

**Idea.** If a common divisor exists, both strings are made of the same block, so `str1 + str2 == str2 + str1`. When that holds, the answer is the prefix whose length is `gcd(len(str1), len(str2))`.

**Steps.**
1. If `str1 + str2 != str2 + str1`, no common divisor exists → return `""`.
2. Otherwise return `str1[:gcd(len(str1), len(str2))]`.

```python
from math import gcd


class Solution:
    def gcdOfStrings(self, str1: str, str2: str) -> str:
        if str1 + str2 != str2 + str1:
            return ""
        return str1[:gcd(len(str1), len(str2))]
```

**Complexity.** Time O(m + n), space O(m + n).

**Watch out.** Why the gcd length? Any common block length must divide both lengths, and the largest such length is their gcd. The concatenation check proves a common block exists.

```test
assert Solution().gcdOfStrings("ABCABC", "ABC") == "ABC"
assert Solution().gcdOfStrings("ABABAB", "ABAB") == "AB"
assert Solution().gcdOfStrings("LEET", "CODE") == ""
assert Solution().gcdOfStrings("AAAAAA", "AAAA") == "AA"
```

### 1431. Kids With the Greatest Number of Candies
difficulty: Easy

**Problem.** For each kid, return whether giving them all `extraCandies` would make their count the greatest (ties count).

**Example.** `candies = [2,3,5,1,3], extraCandies = 3` → `[true,true,true,false,true]`.

**Idea.** Only the current maximum matters: kid `i` wins exactly when `candies[i] + extra >= max(candies)`.

**Steps.**
1. Compute the maximum once.
2. Compare each kid's count plus `extraCandies` with it.

```python
class Solution:
    def kidsWithCandies(self, candies: List[int], extraCandies: int) -> List[bool]:
        best = max(candies)
        return [c + extraCandies >= best for c in candies]
```

**Complexity.** Time O(n), space O(n) for the answer.

**Watch out.** Use `>=`: being tied with the maximum also counts as "the greatest".

```test
assert Solution().kidsWithCandies([2,3,5,1,3], 3) == [True,True,True,False,True]
assert Solution().kidsWithCandies([4,2,1,1,2], 1) == [True,False,False,False,False]
assert Solution().kidsWithCandies([12,1,12], 10) == [True,False,True]
```

### 605. Can Place Flowers
difficulty: Easy

**Problem.** A flowerbed is a list of `0` (empty) and `1` (planted). Flowers can't be adjacent. Can you plant `n` new flowers?

**Example.** `flowerbed = [1,0,0,0,1], n = 1` → `true`; with `n = 2` → `false`.

**Idea.** Greedy from left to right: plant in every empty plot whose neighbours are empty (or outside the bed). Planting as early as possible never blocks a better arrangement.

**Steps.**
1. For each index `i` with `flowerbed[i] == 0`, check the left plot (or the edge) and the right plot (or the edge).
2. If both are empty, plant there (`flowerbed[i] = 1`) and decrease `n`.
3. Stop early when `n` reaches 0. Return `n <= 0`.

```python
class Solution:
    def canPlaceFlowers(self, flowerbed: List[int], n: int) -> bool:
        for i in range(len(flowerbed)):
            if n <= 0:
                break
            if flowerbed[i] == 0:
                left_empty = i == 0 or flowerbed[i - 1] == 0
                right_empty = i == len(flowerbed) - 1 or flowerbed[i + 1] == 0
                if left_empty and right_empty:
                    flowerbed[i] = 1
                    n -= 1
        return n <= 0
```

**Complexity.** Time O(n), space O(1).

**Watch out.**
- Mark the plot as planted, so the next plot sees it as taken.
- `n = 0` is always possible, even for a full bed.

```test
assert Solution().canPlaceFlowers([1,0,0,0,1], 1) is True
assert Solution().canPlaceFlowers([1,0,0,0,1], 2) is False
assert Solution().canPlaceFlowers([0], 1) is True
assert Solution().canPlaceFlowers([0,0,1,0,0], 2) is True
assert Solution().canPlaceFlowers([1,0,1], 0) is True
```

### 345. Reverse Vowels of a String
difficulty: Easy

**Problem.** Reverse only the vowels (`a e i o u`, both cases) in a string.

**Example.** `"IceCreAm"` → `"AceCreIm"`.

**Idea.** Two pointers from both ends: move each pointer until it sits on a vowel, swap, and continue inward.

**Steps.**
1. Convert the string to a list; `i = 0`, `j = len - 1`.
2. Move `i` right while it's not a vowel; move `j` left while it's not a vowel.
3. If `i < j`, swap and move both inward.

```python
class Solution:
    def reverseVowels(self, s: str) -> str:
        vowels = set("aeiouAEIOU")
        chars = list(s)
        i, j = 0, len(chars) - 1
        while i < j:
            if chars[i] not in vowels:
                i += 1
            elif chars[j] not in vowels:
                j -= 1
            else:
                chars[i], chars[j] = chars[j], chars[i]
                i += 1
                j -= 1
        return "".join(chars)
```

**Complexity.** Time O(n), space O(n) for the list.

**Watch out.** Remember uppercase vowels. Python strings are immutable, so work on a list.

```test
assert Solution().reverseVowels("IceCreAm") == "AceCreIm"
assert Solution().reverseVowels("leetcode") == "leotcede"
assert Solution().reverseVowels("a.") == "a."
```

### 334. Increasing Triplet Subsequence
difficulty: Medium

**Problem.** Is there `i < j < k` with `nums[i] < nums[j] < nums[k]`?

**Example.** `[2,1,5,0,4,6]` → `true` (`0, 4, 6`).

**Idea.** Keep the smallest value seen (`first`) and the smallest value that has something smaller before it (`second`). Any number bigger than `second` completes a triplet.

**Steps.**
1. `first = second = inf`.
2. For each `x`: if `x <= first`, update `first`; elif `x <= second`, update `second`; else return `True`.
3. Return `False` at the end.

```python
class Solution:
    def increasingTriplet(self, nums: List[int]) -> bool:
        first = second = float("inf")
        for x in nums:
            if x <= first:
                first = x
            elif x <= second:
                second = x
            else:
                return True
        return False
```

**Complexity.** Time O(n), space O(1).

**Watch out.**
- Updating `first` after `second` is set is fine: `second` still remembers that *some* smaller value came before it.
- Use `<=`, not `<`, so equal values don't count as increasing.

```test
assert Solution().increasingTriplet([1,2,3,4,5]) is True
assert Solution().increasingTriplet([5,4,3,2,1]) is False
assert Solution().increasingTriplet([2,1,5,0,4,6]) is True
assert Solution().increasingTriplet([1,1,1]) is False
assert Solution().increasingTriplet([20,100,10,12,5,13]) is True
```

### 443. String Compression
difficulty: Medium

**Problem.** Compress a list of characters in place: each run becomes the character followed by its length (only if the length is more than 1, written digit by digit). Return the new length.

**Example.** `["a","a","b","b","c","c","c"]` → `6`, list starts `["a","2","b","2","c","3"]`.

**Idea.** A read pointer scans each run; a write pointer writes the compressed form. The write pointer never passes the read pointer, because a compressed run is never longer than the run.

**Steps.**
1. `read = write = 0`.
2. While `read < n`: remember the character, advance `read` to the end of its run.
3. Write the character; if the run length is above 1, write each digit of the length.
4. Return `write`.

```python
class Solution:
    def compress(self, chars: List[str]) -> int:
        read = write = 0
        n = len(chars)
        while read < n:
            ch, start = chars[read], read
            while read < n and chars[read] == ch:
                read += 1
            chars[write] = ch
            write += 1
            if read - start > 1:
                for digit in str(read - start):
                    chars[write] = digit
                    write += 1
        return write
```

**Complexity.** Time O(n), space O(1) extra.

**Watch out.** A run of 12 becomes `"1", "2"`: two separate characters, not `"12"`.

```test
a = ["a","a","b","b","c","c","c"]; k = Solution().compress(a); assert k == 6 and a[:k] == ["a","2","b","2","c","3"]
a = ["a"]; assert Solution().compress(a) == 1 and a == ["a"]
a = ["a"] + ["b"] * 12; k = Solution().compress(a); assert a[:k] == ["a","b","1","2"]
```

### 1679. Max Number of K-Sum Pairs
difficulty: Medium

**Problem.** In one operation, remove two numbers that sum to `k`. Return the maximum number of operations.

**Example.** `nums = [3,1,3,4,3], k = 6` → `1`.

**Idea.** One pass with a counter of unmatched numbers: when `k - x` is waiting, pair `x` with it; otherwise `x` waits.

**Steps.**
1. `waiting = Counter()`, `ops = 0`.
2. For each `x`: if `waiting[k - x] > 0`, use it and count an operation; else `waiting[x] += 1`.

```python
from collections import Counter


class Solution:
    def maxOperations(self, nums: List[int], k: int) -> int:
        waiting = Counter()
        ops = 0
        for x in nums:
            if waiting[k - x] > 0:
                waiting[k - x] -= 1
                ops += 1
            else:
                waiting[x] += 1
        return ops
```

**Complexity.** Time O(n), space O(n).

**Watch out.** Alternative with sorting + two pointers (O(n log n), O(1) extra): move `i` right when the sum is too small, `j` left when too big, both when equal.

```test
assert Solution().maxOperations([1,2,3,4], 5) == 2
assert Solution().maxOperations([3,1,3,4,3], 6) == 1
assert Solution().maxOperations([2,2,2,2], 4) == 2
assert Solution().maxOperations([1], 2) == 0
```

### 643. Maximum Average Subarray I
difficulty: Easy

**Problem.** Find the contiguous subarray of length `k` with the maximum average.

**Example.** `nums = [1,12,-5,-6,50,3], k = 4` → `12.75`.

**Idea.** Fixed-size sliding window: add the new element, remove the one that left. Maximize the **sum** and divide once at the end.

**Steps.**
1. `window = sum(nums[:k])`, `best = window`.
2. For `i` from `k` to the end: `window += nums[i] - nums[i - k]`, update `best`.
3. Return `best / k`.

```python
class Solution:
    def findMaxAverage(self, nums: List[int], k: int) -> float:
        window = best = sum(nums[:k])
        for i in range(k, len(nums)):
            window += nums[i] - nums[i - k]
            best = max(best, window)
        return best / k
```

**Complexity.** Time O(n), space O(1).

**Watch out.** Start `best` from the first window, not from 0: all sums may be negative.

```test
assert abs(Solution().findMaxAverage([1,12,-5,-6,50,3], 4) - 12.75) < 1e-9
assert Solution().findMaxAverage([5], 1) == 5.0
assert Solution().findMaxAverage([-1,-2,-3], 2) == -1.5
```

### 1456. Maximum Number of Vowels in a Substring of Given Length
difficulty: Medium

**Problem.** Return the maximum number of vowels in any substring of length `k`.

**Example.** `s = "abciiidef", k = 3` → `3` (`"iii"`).

**Idea.** Fixed-size window: count the vowels in the first `k` letters, then for each step add 1 if the entering letter is a vowel and subtract 1 if the leaving letter is.

**Steps.**
1. `count` = vowels in `s[:k]`; `best = count`.
2. For `i` from `k`: `count += (s[i] is vowel) - (s[i-k] is vowel)`; update `best`.

```python
class Solution:
    def maxVowels(self, s: str, k: int) -> int:
        vowels = set("aeiou")
        count = best = sum(ch in vowels for ch in s[:k])
        for i in range(k, len(s)):
            count += (s[i] in vowels) - (s[i - k] in vowels)
            best = max(best, count)
        return best
```

**Complexity.** Time O(n), space O(1).

**Watch out.** You can stop early when `best == k`, since it can't get higher.

```test
assert Solution().maxVowels("abciiidef", 3) == 3
assert Solution().maxVowels("aeiou", 2) == 2
assert Solution().maxVowels("leetcode", 3) == 2
assert Solution().maxVowels("tryhard", 4) == 1
```

### 1004. Max Consecutive Ones III
difficulty: Medium

**Problem.** Given a binary array, you may flip at most `k` zeros. Return the longest run of 1s you can get.

**Example.** `nums = [1,1,1,0,0,0,1,1,1,1,0], k = 2` → `6`.

**Idea.** Rephrase: find the longest window containing at most `k` zeros. Grow the window to the right; when it has too many zeros, shrink it from the left.

**Steps.**
1. `left = zeros = 0`.
2. For each `right`: if `nums[right] == 0`, `zeros += 1`.
3. While `zeros > k`: if `nums[left] == 0`, `zeros -= 1`; `left += 1`.
4. Update `best = max(best, right - left + 1)`.

```python
class Solution:
    def longestOnes(self, nums: List[int], k: int) -> int:
        left = zeros = best = 0
        for right, x in enumerate(nums):
            if x == 0:
                zeros += 1
            while zeros > k:
                if nums[left] == 0:
                    zeros -= 1
                left += 1
            best = max(best, right - left + 1)
        return best
```

**Complexity.** Time O(n), space O(1).

**Watch out.** You don't actually flip anything: the count of zeros inside the window is all you need.

```test
assert Solution().longestOnes([1,1,1,0,0,0,1,1,1,1,0], 2) == 6
assert Solution().longestOnes([0,0,1,1,0,0,1,1,1,0,1,1,0,0,0,1,1,1,1], 3) == 10
assert Solution().longestOnes([0,0], 0) == 0
assert Solution().longestOnes([0,0], 5) == 2
```

### 1493. Longest Subarray of 1's After Deleting One Element
difficulty: Medium

**Problem.** Delete exactly one element from a binary array. Return the length of the longest run of 1s afterwards.

**Example.** `[0,1,1,1,0,1,1,0,1]` → `5`.

**Idea.** Same as "at most one zero in the window" (1004 with `k = 1`), but one element must be deleted, so the answer is the window length **minus 1**.

**Steps.**
1. Slide a window that contains at most one zero.
2. The best answer is `max(right - left)` (window length minus the deleted element).

```python
class Solution:
    def longestSubarray(self, nums: List[int]) -> int:
        left = zeros = best = 0
        for right, x in enumerate(nums):
            if x == 0:
                zeros += 1
            while zeros > 1:
                if nums[left] == 0:
                    zeros -= 1
                left += 1
            best = max(best, right - left)
        return best
```

**Complexity.** Time O(n), space O(1).

**Watch out.** All ones → you still must delete one: `[1,1,1]` → `2`.

```test
assert Solution().longestSubarray([1,1,0,1]) == 3
assert Solution().longestSubarray([0,1,1,1,0,1,1,0,1]) == 5
assert Solution().longestSubarray([1,1,1]) == 2
assert Solution().longestSubarray([0,0]) == 0
```

### 1732. Find the Highest Altitude
difficulty: Easy

**Problem.** A biker starts at altitude 0; `gain[i]` is the change between points `i` and `i + 1`. Return the highest altitude reached.

**Example.** `[-5,1,5,0,-7]` → altitudes `0,-5,-4,1,1,-6` → `1`.

**Idea.** The altitude is a running (prefix) sum. Track its maximum, including the start at 0.

**Steps.**
1. `altitude = best = 0`.
2. Add each gain to `altitude` and update `best`.

```python
class Solution:
    def largestAltitude(self, gain: List[int]) -> int:
        altitude = best = 0
        for g in gain:
            altitude += g
            best = max(best, altitude)
        return best
```

**Complexity.** Time O(n), space O(1).

**Watch out.** The starting point (altitude 0) counts, so the answer is never negative.

```test
assert Solution().largestAltitude([-5,1,5,0,-7]) == 1
assert Solution().largestAltitude([-4,-3,-2,-1,4,3,2]) == 0
```

### 724. Find Pivot Index
difficulty: Easy

**Problem.** Return the leftmost index where the sum of the numbers to its left equals the sum to its right (or `-1`).

**Example.** `[1,7,3,6,5,6]` → `3` (`1+7+3 = 11 = 5+6`).

**Idea.** With the total known, the right sum at `i` is `total - left - nums[i]`. One pass keeps `left` up to date.

**Steps.**
1. `total = sum(nums)`, `left = 0`.
2. For each `i`: if `left == total - left - nums[i]`, return `i`. Then `left += nums[i]`.
3. Return `-1`.

```python
class Solution:
    def pivotIndex(self, nums: List[int]) -> int:
        total, left = sum(nums), 0
        for i, x in enumerate(nums):
            if left == total - left - x:
                return i
            left += x
        return -1
```

**Complexity.** Time O(n), space O(1).

**Watch out.** The pivot itself is in neither side. Index 0 can be the pivot (left sum is 0).

```test
assert Solution().pivotIndex([1,7,3,6,5,6]) == 3
assert Solution().pivotIndex([1,2,3]) == -1
assert Solution().pivotIndex([2,1,-1]) == 0
```

### 2215. Find the Difference of Two Arrays
difficulty: Easy

**Problem.** Return `[a, b]`: `a` = distinct numbers in `nums1` not in `nums2`, `b` = distinct numbers in `nums2` not in `nums1` (any order).

**Example.** `[1,2,3], [2,4,6]` → `[[1,3],[4,6]]`.

**Idea.** Set difference does exactly this.

**Steps.**
1. Build `s1 = set(nums1)`, `s2 = set(nums2)`.
2. Return `[list(s1 - s2), list(s2 - s1)]`.

```python
class Solution:
    def findDifference(self, nums1: List[int], nums2: List[int]) -> List[List[int]]:
        s1, s2 = set(nums1), set(nums2)
        return [list(s1 - s2), list(s2 - s1)]
```

**Complexity.** Time O(m + n), space O(m + n).

**Watch out.** Sets also remove duplicates, which the problem requires ("distinct").

```test
r = Solution().findDifference([1,2,3], [2,4,6]); assert sorted(r[0]) == [1,3] and sorted(r[1]) == [4,6]
r = Solution().findDifference([1,2,3,3], [1,1,2,2]); assert r == [[3], []]
```

### 1207. Unique Number of Occurrences
difficulty: Easy

**Problem.** Return `true` if every value appears a different number of times.

**Example.** `[1,2,2,1,1,3]` → `true` (counts 3, 2, 1).

**Idea.** Count each value, then check that the counts have no duplicates.

**Steps.**
1. `counts = Counter(arr).values()`.
2. Return `len(counts) == len(set(counts))`.

```python
from collections import Counter


class Solution:
    def uniqueOccurrences(self, arr: List[int]) -> bool:
        counts = Counter(arr).values()
        return len(counts) == len(set(counts))
```

**Complexity.** Time O(n), space O(n).

**Watch out.** Compare the number of counts to the number of *distinct* counts, not to `len(arr)`.

```test
assert Solution().uniqueOccurrences([1,2,2,1,1,3]) is True
assert Solution().uniqueOccurrences([1,2]) is False
assert Solution().uniqueOccurrences([-3,0,1,-3,1,1,1,-3,10,0]) is True
```

### 1657. Determine if Two Strings Are Close
difficulty: Medium

**Problem.** Two strings are close if you can turn one into the other by (1) swapping any two characters, and (2) transforming every occurrence of one existing letter into another existing letter and vice versa.

**Example.** `"cabbba"`, `"abbccc"` → `true`.

**Idea.** Operation 1 means order doesn't matter. Operation 2 means the counts can be reassigned between letters that exist. So the strings are close exactly when they use the **same set of letters** and have the **same multiset of counts**.

**Steps.**
1. Count letters in both strings.
2. Compare the key sets, and compare the sorted lists of counts.

```python
from collections import Counter


class Solution:
    def closeStrings(self, word1: str, word2: str) -> bool:
        c1, c2 = Counter(word1), Counter(word2)
        return c1.keys() == c2.keys() and sorted(c1.values()) == sorted(c2.values())
```

**Complexity.** Time O(n) (at most 26 counts to sort), space O(1).

**Watch out.** Operation 2 can't create a letter that isn't in the word, so the letter sets must match exactly.

```test
assert Solution().closeStrings("abc", "bca") is True
assert Solution().closeStrings("a", "aa") is False
assert Solution().closeStrings("cabbba", "abbccc") is True
assert Solution().closeStrings("uau", "ssx") is False
```

### 2352. Equal Row and Column Pairs
difficulty: Medium

**Problem.** In an `n x n` grid, count pairs `(row r, column c)` where row `r` and column `c` contain the same values in the same order.

**Example.** `[[3,2,1],[1,7,6],[2,7,7]]` → `1` (row 2 = column 1 = `[2,7,7]`).

**Idea.** Count the rows as tuples in a hash map. For every column (as a tuple), add how many rows are equal to it.

**Steps.**
1. `rows = Counter(tuple(r) for r in grid)`.
2. Columns: `zip(*grid)` yields each column as a tuple.
3. Sum `rows[col]` over all columns.

```python
from collections import Counter


class Solution:
    def equalPairs(self, grid: List[List[int]]) -> int:
        rows = Counter(tuple(row) for row in grid)
        return sum(rows[col] for col in zip(*grid))
```

**Complexity.** Time O(n²), space O(n²).

**Watch out.** Lists aren't hashable. Convert rows to tuples before using them as keys.

```test
assert Solution().equalPairs([[3,2,1],[1,7,6],[2,7,7]]) == 1
assert Solution().equalPairs([[3,1,2,2],[1,4,4,5],[2,4,2,2],[2,4,2,2]]) == 3
```

### 2390. Removing Stars From a String
difficulty: Medium

**Problem.** Each `*` removes itself and the closest non-star character to its left. Return the final string.

**Example.** `"leet**cod*e"` → `"lecoe"`.

**Idea.** A stack: letters are pushed, a star pops the most recent letter.

**Steps.**
1. For each character: if it's `*`, pop; otherwise push.
2. Join the stack.

```python
class Solution:
    def removeStars(self, s: str) -> str:
        stack = []
        for ch in s:
            if ch == "*":
                stack.pop()
            else:
                stack.append(ch)
        return "".join(stack)
```

**Complexity.** Time O(n), space O(n).

**Watch out.** The problem guarantees each star has a letter to remove, so `pop()` never runs on an empty stack.

```test
assert Solution().removeStars("leet**cod*e") == "lecoe"
assert Solution().removeStars("erase*****") == ""
```

### 735. Asteroid Collision
difficulty: Medium

**Problem.** Positive asteroids move right, negative ones move left; size is the absolute value. When two meet, the smaller explodes; equal sizes both explode. Return the survivors.

**Example.** `[10,2,-5]` → `[10]`.

**Idea.** A stack of survivors. Only a **left-moving** asteroid can hit the **right-moving** ones on top of the stack. Resolve collisions until it's destroyed or nothing is left to hit.

**Steps.**
1. For each asteroid `a`, assume it survives.
2. While it survives, `a < 0`, and the top is positive: if the top is smaller, pop it and continue; if equal, pop and `a` dies; if larger, `a` dies.
3. If `a` survived, push it.

```python
class Solution:
    def asteroidCollision(self, asteroids: List[int]) -> List[int]:
        stack = []
        for a in asteroids:
            alive = True
            while alive and a < 0 and stack and stack[-1] > 0:
                if stack[-1] < -a:
                    stack.pop()
                elif stack[-1] == -a:
                    stack.pop()
                    alive = False
                else:
                    alive = False
            if alive:
                stack.append(a)
        return stack
```

**Complexity.** Time O(n) (each asteroid is pushed and popped at most once), space O(n).

**Watch out.** `[-2, 1]` don't collide: the left one moves left, the right one moves right. Only "positive on the stack, negative arriving" collides.

```test
assert Solution().asteroidCollision([5,10,-5]) == [5,10]
assert Solution().asteroidCollision([8,-8]) == []
assert Solution().asteroidCollision([10,2,-5]) == [10]
assert Solution().asteroidCollision([-2,-1,1,2]) == [-2,-1,1,2]
assert Solution().asteroidCollision([1,-2,-2,-2]) == [-2,-2,-2]
```

### 933. Number of Recent Calls
difficulty: Easy

**Problem.** `ping(t)` adds a request at time `t` (strictly increasing) and returns how many requests happened in `[t - 3000, t]`.

**Example.** pings at `1, 100, 3001, 3002` → `1, 2, 3, 3`.

**Idea.** A queue of timestamps: append the new one, and drop old ones from the front while they are older than `t - 3000`.

**Steps.**
1. Append `t`.
2. While `q[0] < t - 3000`, pop from the left.
3. Return `len(q)`.

```python
from collections import deque


class RecentCounter:
    def __init__(self):
        self.q = deque()

    def ping(self, t: int) -> int:
        self.q.append(t)
        while self.q[0] < t - 3000:
            self.q.popleft()
        return len(self.q)
```

**Complexity.** Amortized O(1) per ping, space O(window).

**Watch out.** Use `deque.popleft()` (O(1)); `list.pop(0)` is O(n).

```test
rc = RecentCounter()
assert [rc.ping(t) for t in (1, 100, 3001, 3002)] == [1, 2, 3, 3]
```

### 649. Dota2 Senate
difficulty: Medium

**Problem.** Senators from two parties (`R`, `D`) vote in order, round after round. On their turn, a senator bans one opponent. When only one party has senators left, it wins. Return `"Radiant"` or `"Dire"`.

**Example.** `"RDD"` → `"Dire"`.

**Idea.** The best move is always to ban the **next** opponent in line. Keep two queues of indices. The earlier senator bans the other and gets back in line for the next round (index `+ n`).

**Steps.**
1. Queue the indices of `R` and of `D` separately.
2. While both are non-empty: pop the front of each; the smaller index wins and is re-queued with index `+ n`.
3. The non-empty queue's party wins.

```python
from collections import deque


class Solution:
    def predictPartyVictory(self, senate: str) -> str:
        n = len(senate)
        radiant = deque(i for i, c in enumerate(senate) if c == "R")
        dire = deque(i for i, c in enumerate(senate) if c == "D")
        while radiant and dire:
            r, d = radiant.popleft(), dire.popleft()
            if r < d:
                radiant.append(r + n)
            else:
                dire.append(d + n)
        return "Radiant" if radiant else "Dire"
```

**Complexity.** Time O(n), space O(n).

**Watch out.** Adding `n` keeps the order correct for the next round: the senator acts after everyone still waiting in this round.

```test
assert Solution().predictPartyVictory("RD") == "Radiant"
assert Solution().predictPartyVictory("RDD") == "Dire"
assert Solution().predictPartyVictory("DDRRR") == "Dire"
assert Solution().predictPartyVictory("RRDDD") == "Radiant"
```

### 2095. Delete the Middle Node of a Linked List
difficulty: Medium

**Problem.** Delete the middle node (index `n // 2`, 0-based) of a linked list and return the head.

**Example.** `[1,3,4,7,1,2,6]` → `[1,3,4,1,2,6]`.

**Idea.** Fast and slow pointers, with `fast` starting two steps ahead, so `slow` stops on the node **before** the middle.

**Steps.**
1. One node → return `None`.
2. `slow = head`, `fast = head.next.next`.
3. While `fast` and `fast.next`: move `slow` one step, `fast` two.
4. Unlink: `slow.next = slow.next.next`.

```python
class Solution:
    def deleteMiddle(self, head: Optional[ListNode]) -> Optional[ListNode]:
        if not head.next:
            return None
        slow, fast = head, head.next.next
        while fast and fast.next:
            slow, fast = slow.next, fast.next.next
        slow.next = slow.next.next
        return head
```

**Complexity.** Time O(n), space O(1).

**Watch out.** Starting `fast` two steps ahead is the trick that leaves `slow` before the middle, which is what you need to unlink it.

```test
assert to_list(Solution().deleteMiddle(build_list([1,3,4,7,1,2,6]))) == [1,3,4,1,2,6]
assert to_list(Solution().deleteMiddle(build_list([1,2,3,4]))) == [1,2,4]
assert to_list(Solution().deleteMiddle(build_list([2,1]))) == [2]
assert Solution().deleteMiddle(build_list([1])) is None
```

### 328. Odd Even Linked List
difficulty: Medium

**Problem.** Group the nodes at odd positions first, then the nodes at even positions (1-based positions, relative order kept). O(1) extra space.

**Example.** `[1,2,3,4,5]` → `[1,3,5,2,4]`.

**Idea.** Build two chains at once, `odd` and `even`, by relinking pointers; then attach the even chain after the odd one.

**Steps.**
1. `odd = head`, `even = head.next`, remember `even_head`.
2. While `even` and `even.next`: link `odd.next = even.next`, advance `odd`; link `even.next = odd.next`, advance `even`.
3. `odd.next = even_head`.

```python
class Solution:
    def oddEvenList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        if not head:
            return None
        odd, even = head, head.next
        even_head = even
        while even and even.next:
            odd.next = even.next
            odd = odd.next
            even.next = odd.next
            even = even.next
        odd.next = even_head
        return head
```

**Complexity.** Time O(n), space O(1).

**Watch out.** "Odd" refers to **positions**, not values.

```test
assert to_list(Solution().oddEvenList(build_list([1,2,3,4,5]))) == [1,3,5,2,4]
assert to_list(Solution().oddEvenList(build_list([2,1,3,5,6,4,7]))) == [2,3,6,7,1,5,4]
assert Solution().oddEvenList(None) is None
```

### 2130. Maximum Twin Sum of a Linked List
difficulty: Medium

**Problem.** In a list of even length `n`, node `i` and node `n - 1 - i` are twins. Return the maximum twin sum.

**Example.** `[5,4,2,1]` → `6` (`5+1`, `4+2`).

**Idea.** Find the middle with fast/slow pointers, reverse the second half, then walk both halves together summing pairs.

**Steps.**
1. Move `slow` one step and `fast` two until `fast` ends: `slow` is the start of the second half.
2. Reverse the second half.
3. Walk from `head` and from the reversed half at the same time; track the maximum sum.

```python
class Solution:
    def pairSum(self, head: Optional[ListNode]) -> int:
        slow = fast = head
        while fast and fast.next:
            slow, fast = slow.next, fast.next.next
        prev = None
        while slow:
            slow.next, prev, slow = prev, slow, slow.next
        best = 0
        first, second = head, prev
        while second:
            best = max(best, first.val + second.val)
            first, second = first.next, second.next
        return best
```

**Complexity.** Time O(n), space O(1).

**Watch out.** Simpler O(n)-space version: copy the values into a list and compare `vals[i] + vals[n - 1 - i]`. Fine in an interview if you mention the O(1) version.

```test
assert Solution().pairSum(build_list([5,4,2,1])) == 6
assert Solution().pairSum(build_list([4,2,2,3])) == 7
assert Solution().pairSum(build_list([1,100000])) == 100001
```

### 872. Leaf-Similar Trees
difficulty: Easy

**Problem.** Two trees are leaf-similar if their leaves, read left to right, form the same sequence.

**Example.** Two different trees whose leaves are both `6,7,4,9,8` → `true`.

**Idea.** Collect each tree's leaves with a DFS that visits left before right, then compare the two sequences.

**Steps.**
1. A generator `leaves(node)` yields the value of each leaf in left-to-right order.
2. Compare `list(leaves(root1)) == list(leaves(root2))`.

```python
class Solution:
    def leafSimilar(self, root1: Optional[TreeNode], root2: Optional[TreeNode]) -> bool:
        def leaves(node):
            stack = [node] if node else []
            while stack:
                node = stack.pop()
                if not node.left and not node.right:
                    yield node.val
                if node.right:
                    stack.append(node.right)
                if node.left:
                    stack.append(node.left)
        return list(leaves(root1)) == list(leaves(root2))
```

**Complexity.** Time O(n + m), space O(h) for the stack plus the leaf lists.

**Watch out.** Push the right child before the left so the left side is processed first.

```test
a = build_tree([3,5,1,6,2,9,8,None,None,7,4])
b = build_tree([3,5,1,6,7,4,2,None,None,None,None,None,None,9,8])
assert Solution().leafSimilar(a, b) is True
assert Solution().leafSimilar(build_tree([1,2,3]), build_tree([1,3,2])) is False
```

### 1448. Count Good Nodes in Binary Tree
difficulty: Medium

**Problem.** A node is good if no node on the path from the root to it has a greater value. Count the good nodes.

**Example.** `[3,1,4,3,null,1,5]` → `4`.

**Idea.** DFS carrying the maximum value seen on the path so far. A node is good when its value is at least that maximum.

**Steps.**
1. Stack of `(node, max_so_far)`, starting with `(root, root.val)`.
2. Pop: if `node.val >= max_so_far`, count it. Push children with `max(max_so_far, node.val)`.

```python
class Solution:
    def goodNodes(self, root: TreeNode) -> int:
        good = 0
        stack = [(root, root.val)]
        while stack:
            node, high = stack.pop()
            if node.val >= high:
                good += 1
            high = max(high, node.val)
            if node.left:
                stack.append((node.left, high))
            if node.right:
                stack.append((node.right, high))
        return good
```

**Complexity.** Time O(n), space O(h).

**Watch out.** Equal values count as good (`>=`). The root is always good.

```test
assert Solution().goodNodes(build_tree([3,1,4,3,None,1,5])) == 4
assert Solution().goodNodes(build_tree([3,3,None,4,2])) == 3
assert Solution().goodNodes(build_tree([1])) == 1
```

### 1372. Longest ZigZag Path in a Binary Tree
difficulty: Medium

**Problem.** A zigzag path alternates left and right moves. Its length is the number of edges. Return the longest zigzag path anywhere in the tree.

**Example.** `[1,null,1,1,1,null,null,1,1,null,1,null,null,null,1]` → `3`.

**Idea.** For each node track two lengths: the zigzag ending here with a **left** move, and with a **right** move. Going to the left child continues a path whose last move was right (`right + 1`) and resets the other to 0; symmetric for the right child.

**Steps.**
1. Stack of `(node, left_len, right_len)`, starting with `(root, 0, 0)`.
2. Pop and update `best` with both lengths.
3. Push `(node.left, right_len + 1, 0)` and `(node.right, 0, left_len + 1)`.

```python
class Solution:
    def longestZigZag(self, root: Optional[TreeNode]) -> int:
        best = 0
        stack = [(root, 0, 0)]
        while stack:
            node, left, right = stack.pop()
            best = max(best, left, right)
            if node.left:
                stack.append((node.left, right + 1, 0))
            if node.right:
                stack.append((node.right, 0, left + 1))
        return best
```

**Complexity.** Time O(n), space O(h).

**Watch out.** Moving in the same direction twice doesn't end the search: it **starts a new** zigzag of length 1 from the current node, which is why the reset is to 0 and then +1 on the next move.

```test
assert Solution().longestZigZag(build_tree([1,None,1,1,1,None,None,1,1,None,1,None,None,None,1])) == 3
assert Solution().longestZigZag(build_tree([1,1,1,None,1,None,None,1,1,None,1])) == 4
assert Solution().longestZigZag(build_tree([1])) == 0
```

### 1161. Maximum Level Sum of a Binary Tree
difficulty: Medium

**Problem.** The root is level 1. Return the smallest level whose node values have the largest sum.

**Example.** `[1,7,0,7,-8,null,null]` → `2` (level sums `1, 7, -1`).

**Idea.** BFS level by level, summing each level and keeping the first level with the best sum.

**Steps.**
1. Queue with the root, `level = 0`, `best_sum = -inf`.
2. For each level: sum the `len(queue)` nodes, push their children.
3. If the sum is strictly greater than the best, remember this level.

```python
from collections import deque


class Solution:
    def maxLevelSum(self, root: Optional[TreeNode]) -> int:
        best_sum, best_level, level = float("-inf"), 1, 0
        q = deque([root])
        while q:
            level += 1
            total = 0
            for _ in range(len(q)):
                node = q.popleft()
                total += node.val
                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)
            if total > best_sum:
                best_sum, best_level = total, level
        return best_level
```

**Complexity.** Time O(n), space O(width).

**Watch out.** Use `>` so ties keep the **smallest** level. Sums can be negative, so start from `-inf`.

```test
assert Solution().maxLevelSum(build_tree([1,7,0,7,-8,None,None])) == 2
assert Solution().maxLevelSum(build_tree([989,None,10250,98693,-89388,None,None,None,-32127])) == 2
assert Solution().maxLevelSum(build_tree([-1,-2,-3])) == 1
```

### 700. Search in a Binary Search Tree
difficulty: Easy

**Problem.** Return the subtree rooted at the node with value `val`, or `null`.

**Example.** `root = [4,2,7,1,3], val = 2` → `[2,1,3]`.

**Idea.** In a BST, smaller values are on the left and larger on the right, so each comparison discards half of the tree.

**Steps.**
1. While the node exists and its value isn't `val`: go left if `val` is smaller, else right.
2. Return the node (or `None`).

```python
class Solution:
    def searchBST(self, root: Optional[TreeNode], val: int) -> Optional[TreeNode]:
        node = root
        while node and node.val != val:
            node = node.left if val < node.val else node.right
        return node
```

**Complexity.** Time O(h), space O(1).

**Watch out.** h is O(log n) only if the tree is balanced; a sorted insertion order makes it O(n).

```test
assert tree_to_list(Solution().searchBST(build_tree([4,2,7,1,3]), 2)) == [2,1,3]
assert Solution().searchBST(build_tree([4,2,7,1,3]), 5) is None
```

### 450. Delete Node in a BST
difficulty: Medium

**Problem.** Delete the node with value `key` from a BST and return the (possibly new) root.

**Example.** `root = [5,3,6,2,4,null,7], key = 3` → `[5,4,6,2,null,null,7]`.

**Idea.** Find the node. With 0 or 1 child, replace it by that child. With 2 children, copy the **in-order successor** (smallest value in the right subtree) into it, then delete that successor from the right subtree.

**Steps.**
1. If `key` is smaller/larger, recurse into the left/right subtree and reattach the result.
2. Found it: no left child → return the right one; no right child → return the left one.
3. Two children: find the leftmost node of the right subtree, copy its value, delete it from the right subtree.

```python
class Solution:
    def deleteNode(self, root: Optional[TreeNode], key: int) -> Optional[TreeNode]:
        if not root:
            return None
        if key < root.val:
            root.left = self.deleteNode(root.left, key)
        elif key > root.val:
            root.right = self.deleteNode(root.right, key)
        else:
            if not root.left:
                return root.right
            if not root.right:
                return root.left
            succ = root.right
            while succ.left:
                succ = succ.left
            root.val = succ.val
            root.right = self.deleteNode(root.right, succ.val)
        return root
```

**Complexity.** Time O(h), space O(h) for the recursion.

**Watch out.** Always reassign `root.left = ...` / `root.right = ...`: the child may have been replaced.

```test
def inorder(n): return inorder(n.left) + [n.val] + inorder(n.right) if n else []
r = Solution().deleteNode(build_tree([5,3,6,2,4,None,7]), 3)
assert tree_to_list(r) == [5,4,6,2,None,None,7] and inorder(r) == [2,4,5,6,7]
assert tree_to_list(Solution().deleteNode(build_tree([5,3,6,2,4,None,7]), 0)) == [5,3,6,2,4,None,7]
assert Solution().deleteNode(None, 0) is None
assert inorder(Solution().deleteNode(build_tree([5,3,6,2,4,None,7]), 5)) == [2,3,4,6,7]
```

### 841. Keys and Rooms
difficulty: Medium

**Problem.** Room 0 is open; every other room is locked. Each room contains keys to other rooms. Can you visit all rooms?

**Example.** `[[1],[2],[3],[]]` → `true`.

**Idea.** It's graph reachability from room 0: DFS through the keys and check that every room was seen.

**Steps.**
1. `seen = {0}`, stack `[0]`.
2. Pop a room; for each key not yet seen, mark it and push it.
3. Return `len(seen) == len(rooms)`.

```python
class Solution:
    def canVisitAllRooms(self, rooms: List[List[int]]) -> bool:
        seen = {0}
        stack = [0]
        while stack:
            for key in rooms[stack.pop()]:
                if key not in seen:
                    seen.add(key)
                    stack.append(key)
        return len(seen) == len(rooms)
```

**Complexity.** Time O(rooms + keys), space O(rooms).

**Watch out.** Mark a room as seen when you **push** it, not when you pop it, to avoid pushing it twice.

```test
assert Solution().canVisitAllRooms([[1],[2],[3],[]]) is True
assert Solution().canVisitAllRooms([[1,3],[3,0,1],[2],[0]]) is False
```

### 547. Number of Provinces
difficulty: Medium

**Problem.** `isConnected[i][j] = 1` means cities `i` and `j` are directly connected. A province is a group of connected cities. Count the provinces.

**Example.** `[[1,1,0],[1,1,0],[0,0,1]]` → `2`.

**Idea.** Count connected components: every time you find an unvisited city, it starts a new province; flood it with DFS.

**Steps.**
1. For each city not yet seen: count a province, DFS from it marking every reachable city.
2. Return the count.

```python
class Solution:
    def findCircleNum(self, isConnected: List[List[int]]) -> int:
        n = len(isConnected)
        seen = [False] * n
        provinces = 0
        for start in range(n):
            if seen[start]:
                continue
            provinces += 1
            seen[start] = True
            stack = [start]
            while stack:
                city = stack.pop()
                for other in range(n):
                    if isConnected[city][other] and not seen[other]:
                        seen[other] = True
                        stack.append(other)
        return provinces
```

**Complexity.** Time O(n²) (the matrix), space O(n).

**Watch out.** Union-Find also works: start with `n` components and decrease the count on every successful union.

```test
assert Solution().findCircleNum([[1,1,0],[1,1,0],[0,0,1]]) == 2
assert Solution().findCircleNum([[1,0,0],[0,1,0],[0,0,1]]) == 3
assert Solution().findCircleNum([[1,0,0,1],[0,1,1,0],[0,1,1,1],[1,0,1,1]]) == 1
```

### 1466. Reorder Routes to Make All Paths Lead to the City Zero
difficulty: Medium

**Problem.** `n` cities form a tree with one-way roads `[a, b]` (from `a` to `b`). Reverse the fewest roads so every city can reach city 0.

**Example.** `n = 6, connections = [[0,1],[1,3],[2,3],[4,0],[4,5]]` → `3`.

**Idea.** Traverse the tree from city 0, ignoring direction. Every road you walk along in its **original** direction points away from 0 and must be reversed.

**Steps.**
1. For each road `a → b`, add `(b, 1)` to `a`'s neighbours (needs reversing if used from `a`) and `(a, 0)` to `b`'s.
2. DFS from 0; when moving to an unvisited neighbour, add its cost (1 or 0).

```python
class Solution:
    def minReorder(self, n: int, connections: List[List[int]]) -> int:
        graph = [[] for _ in range(n)]
        for a, b in connections:
            graph[a].append((b, 1))
            graph[b].append((a, 0))
        seen = [False] * n
        seen[0] = True
        stack, changes = [0], 0
        while stack:
            city = stack.pop()
            for nxt, cost in graph[city]:
                if not seen[nxt]:
                    seen[nxt] = True
                    changes += cost
                    stack.append(nxt)
        return changes
```

**Complexity.** Time O(n), space O(n).

**Watch out.** Since it's a tree, each road is used exactly once in the traversal, so each wrong-way road is counted once.

```test
assert Solution().minReorder(6, [[0,1],[1,3],[2,3],[4,0],[4,5]]) == 3
assert Solution().minReorder(5, [[1,0],[1,2],[3,2],[3,4]]) == 2
assert Solution().minReorder(3, [[1,0],[2,0]]) == 0
```

### 1926. Nearest Exit from Entrance in Maze
difficulty: Medium

**Problem.** In a maze of `.` (empty) and `+` (wall), find the fewest steps from `entrance` to an exit: an empty cell on the border that isn't the entrance. Return `-1` if none.

**Example.** `[["+","+",".","+"],[".",".",".","+"],["+","+","+","."]], entrance = [1,2]` → `1`.

**Idea.** BFS finds shortest paths in an unweighted grid. The first border cell reached (other than the entrance) is the answer.

**Steps.**
1. Queue `(row, col, steps)` with the entrance; mark it visited by turning it into a wall.
2. Pop; for each of the 4 neighbours inside the grid and empty: if it's on the border, return `steps + 1`; otherwise mark it and push it.
3. Return `-1`.

```python
from collections import deque


class Solution:
    def nearestExit(self, maze: List[List[str]], entrance: List[int]) -> int:
        rows, cols = len(maze), len(maze[0])
        r0, c0 = entrance
        maze[r0][c0] = "+"
        q = deque([(r0, c0, 0)])
        while q:
            r, c, steps = q.popleft()
            for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == ".":
                    if nr in (0, rows - 1) or nc in (0, cols - 1):
                        return steps + 1
                    maze[nr][nc] = "+"
                    q.append((nr, nc, steps + 1))
        return -1
```

**Complexity.** Time O(rows · cols), space O(rows · cols).

**Watch out.** The entrance doesn't count as an exit even if it's on the border; marking it as a wall before the search handles that.

```test
assert Solution().nearestExit([["+","+",".","+"],[".",".",".","+"],["+","+","+","."]], [1,2]) == 1
assert Solution().nearestExit([["+","+","+"],[".",".","."],["+","+","+"]], [1,0]) == 2
assert Solution().nearestExit([[".","+"]], [0,0]) == -1
```

### 2336. Smallest Number in Infinite Set
difficulty: Medium

**Problem.** The set starts with all positive integers. `popSmallest()` removes and returns the smallest; `addBack(num)` puts `num` back if it isn't in the set.

**Example.** `addBack(2), pop, pop, pop, addBack(1), pop, pop, pop` → `1, 2, 3, 1, 4, 5`.

**Idea.** Everything from a pointer `next` upward is still in the set. Numbers below `next` that were added back go into a min-heap (plus a set to avoid duplicates).

**Steps.**
1. `popSmallest`: if the heap has numbers, pop the smallest; otherwise return `next` and increase it.
2. `addBack(num)`: only if `num < next` and it's not already in the heap, push it.

```python
import heapq


class SmallestInfiniteSet:
    def __init__(self):
        self.next = 1
        self.heap = []
        self.in_heap = set()

    def popSmallest(self) -> int:
        if self.heap:
            x = heapq.heappop(self.heap)
            self.in_heap.remove(x)
            return x
        self.next += 1
        return self.next - 1

    def addBack(self, num: int) -> None:
        if num < self.next and num not in self.in_heap:
            heapq.heappush(self.heap, num)
            self.in_heap.add(num)
```

**Complexity.** O(log k) per operation, where k is the number of added-back values.

**Watch out.** Numbers `>= next` are already in the set, so adding them back does nothing.

```test
s = SmallestInfiniteSet()
s.addBack(2)
out = [s.popSmallest(), s.popSmallest(), s.popSmallest()]
s.addBack(1)
out += [s.popSmallest(), s.popSmallest(), s.popSmallest()]
assert out == [1, 2, 3, 1, 4, 5]
s.addBack(4); s.addBack(4)
assert s.popSmallest() == 4 and s.popSmallest() == 6
```

### 2542. Maximum Subsequence Score
difficulty: Medium

**Problem.** Pick `k` indices. Score = (sum of their `nums1`) × (minimum of their `nums2`). Return the maximum score.

**Example.** `nums1 = [1,3,3,2], nums2 = [2,1,3,4], k = 3` → `12`.

**Idea.** Sort the pairs by `nums2` descending. When you reach a pair, its `nums2` is the minimum of everything seen so far, so take it as the minimum and pair it with the `k` largest `nums1` values seen so far (a min-heap of size `k` keeps them and their sum).

**Steps.**
1. Sort pairs by `nums2` from high to low.
2. Push each `nums1` onto a min-heap and add to `total`; if the heap grows past `k`, pop the smallest and subtract it.
3. When the heap has exactly `k` items, the score is `total * current nums2`; keep the best.

```python
import heapq


class Solution:
    def maxScore(self, nums1: List[int], nums2: List[int], k: int) -> int:
        heap, total, best = [], 0, 0
        for b, a in sorted(zip(nums2, nums1), reverse=True):
            heapq.heappush(heap, a)
            total += a
            if len(heap) > k:
                total -= heapq.heappop(heap)
            if len(heap) == k:
                best = max(best, total * b)
        return best
```

**Complexity.** Time O(n log n), space O(n).

**Watch out.** The current pair is always included in the score (it supplies the minimum). If it was just popped because its `nums1` is small, the score is still a valid lower bound and never beats the true answer, so the result stays correct.

```test
assert Solution().maxScore([1,3,3,2], [2,1,3,4], 3) == 12
assert Solution().maxScore([4,2,3,1,1], [7,5,10,9,6], 1) == 30
```

### 2462. Total Cost to Hire K Workers
difficulty: Medium

**Problem.** Hire `k` workers in `k` rounds. Each round, pick the cheapest worker among the first `candidates` and the last `candidates` remaining workers (ties → smaller index). Return the total cost.

**Example.** `costs = [17,12,10,2,7,2,11,20,8], k = 3, candidates = 4` → `11`.

**Idea.** Two min-heaps: one for the front window, one for the back window. Two pointers `i` and `j` mark the next workers to add, so no worker is in both heaps.

**Steps.**
1. Before each round, refill each heap up to `candidates` workers while `i <= j`.
2. Take the smaller top (the front heap wins ties, because its indices are smaller).
3. Add its cost to the total.

```python
import heapq


class Solution:
    def totalCost(self, costs: List[int], k: int, candidates: int) -> int:
        front, back = [], []
        i, j = 0, len(costs) - 1
        total = 0
        for _ in range(k):
            while len(front) < candidates and i <= j:
                heapq.heappush(front, costs[i])
                i += 1
            while len(back) < candidates and i <= j:
                heapq.heappush(back, costs[j])
                j -= 1
            if not back or (front and front[0] <= back[0]):
                total += heapq.heappop(front)
            else:
                total += heapq.heappop(back)
        return total
```

**Complexity.** Time O((k + candidates) log candidates), space O(candidates).

**Watch out.** When the windows overlap, `i <= j` stops either heap from taking a worker twice.

```test
assert Solution().totalCost([17,12,10,2,7,2,11,20,8], 3, 4) == 11
assert Solution().totalCost([1,2,4,1], 3, 3) == 4
assert Solution().totalCost([5], 1, 1) == 5
```

### 374. Guess Number Higher or Lower
difficulty: Easy

**Problem.** A number was picked from `1..n`. `guess(num)` returns `-1` if the pick is lower than `num`, `1` if higher, `0` if correct. Find it.

**Example.** `n = 10, pick = 6` → `6`.

**Idea.** Binary search on `1..n`, using `guess` instead of an array comparison.

**Steps.**
1. `lo, hi = 1, n`.
2. Guess the middle: `0` → done; `-1` → search the lower half; `1` → the upper half.

```python
class Solution:
    def guessNumber(self, n: int) -> int:
        lo, hi = 1, n
        while True:
            mid = (lo + hi) // 2
            result = guess(mid)
            if result == 0:
                return mid
            if result < 0:
                hi = mid - 1
            else:
                lo = mid + 1
```

**Complexity.** Time O(log n), space O(1).

**Watch out.** `-1` means **your guess is too high** (the pick is lower). Mixing up the direction is the classic bug.

```test
for n, pick in [(10, 6), (1, 1), (2, 1), (2, 2), (2**31 - 1, 2**31 - 1)]:
    guess = lambda num, pick=pick: (pick > num) - (pick < num)
    assert Solution().guessNumber(n) == pick
```

### 2300. Successful Pairs of Spells and Potions
difficulty: Medium

**Problem.** A spell and a potion are successful if their product is at least `success`. For each spell, count the successful potions.

**Example.** `spells = [5,1,3], potions = [1,2,3,4,5], success = 7` → `[4,0,3]`.

**Idea.** Sort the potions once. For a spell `s`, the potions that work are those `>= ceil(success / s)`: find the first one with binary search; everything after it works.

**Steps.**
1. Sort `potions`.
2. For each spell: `need = (success + s - 1) // s` (integer ceiling).
3. Count `len(potions) - bisect_left(potions, need)`.

```python
from bisect import bisect_left


class Solution:
    def successfulPairs(self, spells: List[int], potions: List[int], success: int) -> List[int]:
        potions.sort()
        m = len(potions)
        return [m - bisect_left(potions, (success + s - 1) // s) for s in spells]
```

**Complexity.** Time O((n + m) log m), space O(1) extra (besides the answer).

**Watch out.** Use integer ceiling division, not `success / s` with floats, to avoid rounding errors on large numbers.

```test
assert Solution().successfulPairs([5,1,3], [1,2,3,4,5], 7) == [4,0,3]
assert Solution().successfulPairs([3,1,2], [8,5,8], 16) == [2,0,2]
```

### 875. Koko Eating Bananas
difficulty: Medium

**Problem.** Koko eats at speed `k` bananas per hour, one pile per hour at most (if a pile has fewer than `k`, she finishes it and waits). Find the minimum `k` to finish all piles within `h` hours.

**Example.** `piles = [3,6,7,11], h = 8` → `4`.

**Idea.** Binary search on the answer: if speed `k` works, every faster speed works too. Hours needed at speed `k` = `sum(ceil(p / k))`.

**Steps.**
1. Search `k` in `[1, max(piles)]`.
2. If the hours at `mid` are `<= h`, it's feasible: `hi = mid`; else `lo = mid + 1`.
3. Return `lo`.

```python
class Solution:
    def minEatingSpeed(self, piles: List[int], h: int) -> int:
        lo, hi = 1, max(piles)
        while lo < hi:
            mid = (lo + hi) // 2
            hours = sum((p + mid - 1) // mid for p in piles)
            if hours <= h:
                hi = mid
            else:
                lo = mid + 1
        return lo
```

**Complexity.** Time O(n log max(piles)), space O(1).

**Watch out.** "Binary search on the answer" applies whenever feasibility is monotonic: shipping capacity, splitting arrays, minimum days, and so on.

```test
assert Solution().minEatingSpeed([3,6,7,11], 8) == 4
assert Solution().minEatingSpeed([30,11,23,4,20], 5) == 30
assert Solution().minEatingSpeed([30,11,23,4,20], 6) == 23
assert Solution().minEatingSpeed([1000000000], 2) == 500000000
```

### 216. Combination Sum III
difficulty: Medium

**Problem.** Find all combinations of `k` distinct digits from 1 to 9 that sum to `n`.

**Example.** `k = 3, n = 9` → `[[1,2,6],[1,3,5],[2,3,4]]`.

**Idea.** Backtracking that picks digits in increasing order (so each combination appears once) and stops early when the sum is too big or there are too many digits.

**Steps.**
1. `backtrack(start, remaining, path)`.
2. If `len(path) == k`: record it when `remaining == 0`; return.
3. Try each digit `d` from `start` to 9; stop when `d > remaining` (larger digits are even worse).

```python
class Solution:
    def combinationSum3(self, k: int, n: int) -> List[List[int]]:
        result = []

        def backtrack(start, remaining, path):
            if len(path) == k:
                if remaining == 0:
                    result.append(path[:])
                return
            for d in range(start, 10):
                if d > remaining:
                    break
                path.append(d)
                backtrack(d + 1, remaining - d, path)
                path.pop()

        backtrack(1, n, [])
        return result
```

**Complexity.** At most C(9, k) combinations, which is tiny.

**Watch out.** Append a **copy** (`path[:]`): the same list object keeps changing during backtracking.

```test
assert Solution().combinationSum3(3, 7) == [[1,2,4]]
assert sorted(Solution().combinationSum3(3, 9)) == [[1,2,6],[1,3,5],[2,3,4]]
assert Solution().combinationSum3(4, 1) == []
assert Solution().combinationSum3(9, 45) == [[1,2,3,4,5,6,7,8,9]]
```

### 1137. N-th Tribonacci Number
difficulty: Easy

**Problem.** `T0 = 0, T1 = 1, T2 = 1`, and `T(n+3) = T(n) + T(n+1) + T(n+2)`. Return `T(n)`.

**Example.** `n = 4` → `4`.

**Idea.** Keep only the last three values and slide them forward.

**Steps.**
1. `a, b, c = 0, 1, 1`.
2. Repeat `n` times: `a, b, c = b, c, a + b + c`.
3. Return `a`.

```python
class Solution:
    def tribonacci(self, n: int) -> int:
        a, b, c = 0, 1, 1
        for _ in range(n):
            a, b, c = b, c, a + b + c
        return a
```

**Complexity.** Time O(n), space O(1).

**Watch out.** Plain recursion without memoization is exponential.

```test
assert [Solution().tribonacci(n) for n in range(6)] == [0, 1, 1, 2, 4, 7]
assert Solution().tribonacci(25) == 1389537
```

### 746. Min Cost Climbing Stairs
difficulty: Easy

**Problem.** `cost[i]` is paid when you step on stair `i`. You can climb 1 or 2 steps and start at stair 0 or 1. Return the minimum cost to reach the top (past the last stair).

**Example.** `[10,15,20]` → `15`.

**Idea.** `best[i]` = minimum cost to stand at position `i` (before paying for it) = `min(best[i-1] + cost[i-1], best[i-2] + cost[i-2])`. Only the last two values are needed.

**Steps.**
1. `a = b = 0` (positions 0 and 1 are free to reach).
2. For `i` from 2 to `n`: `a, b = b, min(b + cost[i-1], a + cost[i-2])`.
3. Return `b`.

```python
class Solution:
    def minCostClimbingStairs(self, cost: List[int]) -> int:
        a = b = 0
        for i in range(2, len(cost) + 1):
            a, b = b, min(b + cost[i - 1], a + cost[i - 2])
        return b
```

**Complexity.** Time O(n), space O(1).

**Watch out.** The top is position `n`, one past the last stair.

```test
assert Solution().minCostClimbingStairs([10,15,20]) == 15
assert Solution().minCostClimbingStairs([1,100,1,1,1,100,1,1,100,1]) == 6
assert Solution().minCostClimbingStairs([5,10]) == 5
```

### 790. Domino and Tromino Tiling
difficulty: Medium

**Problem.** Count the ways to tile a `2 x n` board with dominoes (`2x1`) and L-shaped trominoes, modulo `10^9 + 7`.

**Example.** `n = 3` → `5`.

**Idea.** Working out the small cases gives the recurrence `f(n) = 2·f(n-1) + f(n-3)`, with `f(0) = 1, f(1) = 1, f(2) = 2`.

**Steps.**
1. Handle `n <= 2` directly.
2. Roll three values forward with the recurrence, taking the modulo each step.

```python
class Solution:
    def numTilings(self, n: int) -> int:
        MOD = 10**9 + 7
        if n <= 2:
            return n
        a, b, c = 1, 1, 2  # f(0), f(1), f(2)
        for _ in range(3, n + 1):
            a, b, c = b, c, (2 * c + a) % MOD
        return c
```

**Complexity.** Time O(n), space O(1).

**Watch out.** If you can't remember the recurrence, use two states: `full[i]` (board filled up to column `i`) and `part[i]` (one cell sticking out): `full[i] = full[i-1] + full[i-2] + 2·part[i-1]`, `part[i] = part[i-1] + full[i-2]`.

```test
assert [Solution().numTilings(n) for n in (1, 2, 3, 4, 5)] == [1, 2, 5, 11, 24]
full, part, M = [1, 1], [0, 0], 10**9 + 7
for i in range(2, 60):
    full.append((full[i-1] + full[i-2] + 2 * part[i-1]) % M)
    part.append((part[i-1] + full[i-2]) % M)
assert all(Solution().numTilings(n) == full[n] for n in range(1, 60))
```

### 714. Best Time to Buy and Sell Stock with Transaction Fee
difficulty: Medium

**Problem.** Trade as many times as you like (one share at a time); each sale costs `fee`. Return the maximum profit.

**Example.** `prices = [1,3,2,8,4,9], fee = 2` → `8`.

**Idea.** Two states per day: `cash` (best profit holding nothing) and `hold` (best profit holding one share). Each day you may sell (move from hold to cash, paying the fee) or buy (move from cash to hold).

**Steps.**
1. `cash = 0`, `hold = -prices[0]`.
2. For each price: `cash = max(cash, hold + p - fee)`; `hold = max(hold, cash - p)`.
3. Return `cash`.

```python
class Solution:
    def maxProfit(self, prices: List[int], fee: int) -> int:
        cash, hold = 0, -prices[0]
        for p in prices[1:]:
            cash = max(cash, hold + p - fee)
            hold = max(hold, cash - p)
        return cash
```

**Complexity.** Time O(n), space O(1).

**Watch out.** Using the new `cash` when updating `hold` is safe: selling and buying on the same day only loses the fee.

```test
assert Solution().maxProfit([1,3,2,8,4,9], 2) == 8
assert Solution().maxProfit([1,3,7,5,10,3], 3) == 6
assert Solution().maxProfit([5], 1) == 0
```

### 338. Counting Bits
difficulty: Easy

**Problem.** For every `i` from 0 to `n`, return the number of 1 bits in `i`.

**Example.** `n = 5` → `[0,1,1,2,1,2]`.

**Idea.** `i >> 1` is `i` without its last bit, and its count is already known. So `bits[i] = bits[i >> 1] + (i & 1)`.

**Steps.**
1. `bits = [0] * (n + 1)`.
2. For `i` from 1 to `n`: `bits[i] = bits[i >> 1] + (i & 1)`.

```python
class Solution:
    def countBits(self, n: int) -> List[int]:
        bits = [0] * (n + 1)
        for i in range(1, n + 1):
            bits[i] = bits[i >> 1] + (i & 1)
        return bits
```

**Complexity.** Time O(n), space O(n) for the answer.

**Watch out.** Another DP: `bits[i] = bits[i & (i - 1)] + 1` (`i & (i - 1)` removes the lowest set bit).

```test
assert Solution().countBits(2) == [0,1,1]
assert Solution().countBits(5) == [0,1,1,2,1,2]
assert Solution().countBits(0) == [0]
assert Solution().countBits(1000) == [bin(i).count("1") for i in range(1001)]
```

### 1318. Minimum Flips to Make a OR b Equal to c
difficulty: Medium

**Problem.** Return the minimum number of bit flips in `a` and `b` so that `a | b == c`.

**Example.** `a = 2, b = 6, c = 5` → `3`.

**Idea.** Bits are independent. For each position: if `c`'s bit is 1, you need at least one 1 (one flip if both are 0). If it's 0, every 1 in `a` or `b` must be flipped.

**Steps.**
1. While any of `a, b, c` is non-zero, look at the lowest bits `x, y, z`.
2. `z == 1`: add 1 if `x == y == 0`. `z == 0`: add `x + y`.
3. Shift all three right.

```python
class Solution:
    def minFlips(self, a: int, b: int, c: int) -> int:
        flips = 0
        while a or b or c:
            x, y, z = a & 1, b & 1, c & 1
            if z:
                flips += x == 0 and y == 0
            else:
                flips += x + y
            a, b, c = a >> 1, b >> 1, c >> 1
        return flips
```

**Complexity.** Time O(number of bits), space O(1).

**Watch out.** When `c`'s bit is 0 and both `a` and `b` have a 1, that costs **two** flips.

```test
assert Solution().minFlips(2, 6, 5) == 3
assert Solution().minFlips(4, 2, 7) == 1
assert Solution().minFlips(1, 2, 3) == 0
assert Solution().minFlips(7, 7, 0) == 6
```

### 1268. Search Suggestions System
difficulty: Medium

**Problem.** After each typed character of `searchWord`, suggest up to three products (lexicographically smallest) that start with the typed prefix.

**Example.** `products = ["mobile","mouse","moneypot","monitor","mousepad"], searchWord = "mouse"` → `[["mobile","moneypot","monitor"],["mobile","moneypot","monitor"],["mouse","mousepad"],["mouse","mousepad"],["mouse","mousepad"]]`.

**Idea.** In a sorted list, all words with a given prefix are next to each other. Binary search for the prefix's position, then take the next three words that still start with it.

**Steps.**
1. Sort `products`.
2. For each prefix: `i = bisect_left(products, prefix)`.
3. Take `products[i:i + 3]` and keep those that start with the prefix.

```python
from bisect import bisect_left


class Solution:
    def suggestedProducts(self, products: List[str], searchWord: str) -> List[List[str]]:
        products.sort()
        result, prefix = [], ""
        for ch in searchWord:
            prefix += ch
            i = bisect_left(products, prefix)
            result.append([w for w in products[i:i + 3] if w.startswith(prefix)])
        return result
```

**Complexity.** Time O(n log n) to sort, then O(log n) comparisons per typed character; space O(1) extra.

**Watch out.** A Trie storing the top 3 words at each node is the other classic answer, and it's what this problem's category hints at. The sorted + binary search version is shorter and just as fast in practice.

```test
r = Solution().suggestedProducts(["mobile","mouse","moneypot","monitor","mousepad"], "mouse")
assert r == [["mobile","moneypot","monitor"],["mobile","moneypot","monitor"],["mouse","mousepad"],["mouse","mousepad"],["mouse","mousepad"]]
assert Solution().suggestedProducts(["havana"], "havana") == [["havana"]] * 6
assert Solution().suggestedProducts(["havana"], "tatiana") == [[]] * 7
```

### 435. Non-overlapping Intervals
difficulty: Medium

**Problem.** Return the minimum number of intervals to remove so the rest don't overlap (touching at an end point is fine).

**Example.** `[[1,2],[2,3],[3,4],[1,3]]` → `1`.

**Idea.** Keep as many intervals as possible: sort by **end** and greedily keep each interval that starts after the last kept one ends. Ending early leaves the most room for the rest.

**Steps.**
1. Sort by end.
2. `end = -inf`, `kept = 0`. For each interval: if `start >= end`, keep it and set `end` to its end.
3. Return `len(intervals) - kept`.

```python
class Solution:
    def eraseOverlapIntervals(self, intervals: List[List[int]]) -> int:
        intervals.sort(key=lambda iv: iv[1])
        end, kept = float("-inf"), 0
        for start, finish in intervals:
            if start >= end:
                kept += 1
                end = finish
        return len(intervals) - kept
```

**Complexity.** Time O(n log n), space O(1) extra.

**Watch out.** Sorting by **start** doesn't work directly: one long interval that starts early would block many short ones.

```test
assert Solution().eraseOverlapIntervals([[1,2],[2,3],[3,4],[1,3]]) == 1
assert Solution().eraseOverlapIntervals([[1,2],[1,2],[1,2]]) == 2
assert Solution().eraseOverlapIntervals([[1,2],[2,3]]) == 0
assert Solution().eraseOverlapIntervals([[1,100],[11,22],[1,11],[2,12]]) == 2
```

### 901. Online Stock Span
difficulty: Medium

**Problem.** `next(price)` returns the span: the number of consecutive days, ending today, whose price was `<=` today's price.

**Example.** prices `100,80,60,70,60,75,85` → spans `1,1,1,2,1,4,6`.

**Idea.** A monotonic stack of `(price, span)` with decreasing prices. A new price absorbs every smaller-or-equal price on top, adding their spans to its own.

**Steps.**
1. `span = 1`.
2. While the top price `<= price`: pop it and add its span.
3. Push `(price, span)` and return `span`.

```python
class StockSpanner:
    def __init__(self):
        self.stack = []

    def next(self, price: int) -> int:
        span = 1
        while self.stack and self.stack[-1][0] <= price:
            span += self.stack.pop()[1]
        self.stack.append((price, span))
        return span
```

**Complexity.** Amortized O(1) per call (each price is pushed and popped once), space O(n).

**Watch out.** Popped days don't need to be remembered individually: their spans are folded into the bigger price that absorbed them.

```test
s = StockSpanner()
assert [s.next(p) for p in (100, 80, 60, 70, 60, 75, 85)] == [1, 1, 1, 2, 1, 4, 6]
```
