# Two Pointers

### 125. Valid Palindrome
difficulty: Easy

**Problem.** After lowercasing and removing every non-alphanumeric character, does the string read the same forward and backward?

**Example.** `"A man, a plan, a canal: Panama"` → `true`; `"race a car"` → `false`.

**Idea.** Two pointers from both ends. Skip characters that aren't letters or digits, compare the rest case-insensitively. No cleaned copy needed.

**Steps.**
1. `l = 0`, `r = len(s) - 1`.
2. While `l < r`: move `l` right past non-alphanumerics, move `r` left past them (both loops also check `l < r`).
3. If `s[l].lower() != s[r].lower()`, return false. Otherwise move both inward.
4. Return true.

```python
class Solution:
    def isPalindrome(self, s: str) -> bool:
        l, r = 0, len(s) - 1
        while l < r:
            while l < r and not s[l].isalnum():
                l += 1
            while l < r and not s[r].isalnum():
                r -= 1
            if s[l].lower() != s[r].lower():
                return False
            l += 1
            r -= 1
        return True
```

**Complexity.** Time O(n), space O(1).

**Watch out.**
- Use `isalnum()` in **both** skip loops (a classic bug is `isalpha()` on one side, which fails on `"0P"`).
- Don't compare with ASCII tricks like "differ by 32": `'0'` and `'P'` differ by exactly 32.
- Short O(n)-space version: `t = [c.lower() for c in s if c.isalnum()]; return t == t[::-1]`.

```test
assert Solution().isPalindrome("A man, a plan, a canal: Panama") is True
assert Solution().isPalindrome("race a car") is False
assert Solution().isPalindrome(" ") is True
assert Solution().isPalindrome("0P") is False
```

### 392. Is Subsequence
difficulty: Easy

**Problem.** Is `s` a subsequence of `t` (its characters appear in `t` in the same order, not necessarily next to each other)?

**Example.** `s = "abc", t = "ahbgdc"` → `true`; `s = "axc"` → `false`.

**Idea: greedy two pointers.** Walk through `t`; keep a pointer `i` into `s` for the next character you need. Matching the **earliest** possible occurrence leaves the most room for the rest.

**Steps.**
1. `i = 0`.
2. For each `ch` in `t`: if `i < len(s)` and `s[i] == ch`, increase `i`.
3. Return `i == len(s)`.

```python
class Solution:
    def isSubsequence(self, s: str, t: str) -> bool:
        i = 0
        for ch in t:
            if i < len(s) and s[i] == ch:
                i += 1
        return i == len(s)
```

**Complexity.** Time O(len t), space O(1).

**Watch out (follow-up: billions of `s` strings, one `t`).** Preprocess `t` once: for each character, store the sorted list of its indexes. For each query, keep `prev` and binary-search (`bisect_right`) the first index of the next character **strictly after** `prev`. Each query is O(|s| log |t|).

```py
from bisect import bisect_right
from collections import defaultdict
pos = defaultdict(list)
for i, ch in enumerate(t):
    pos[ch].append(i)

def check(s):
    prev = -1
    for ch in s:
        idx = pos.get(ch, [])
        j = bisect_right(idx, prev)
        if j == len(idx):
            return False
        prev = idx[j]
    return True
```

```test
assert Solution().isSubsequence("abc", "ahbgdc") is True
assert Solution().isSubsequence("axc", "ahbgdc") is False
assert Solution().isSubsequence("", "ahbgdc") is True
```

### 167. Two Sum II - Input Array Is Sorted
difficulty: Medium

**Problem.** `numbers` is sorted and **1-indexed**. Return `[index1, index2]` of the two numbers adding to `target` (exactly one solution), using O(1) extra space.

**Example.** `[2,7,11,15], target = 9` → `[1,2]`.

**Idea.** One pointer at each end. If the sum is too small, move the left pointer right (bigger number); if too big, move the right pointer left.

**Steps.**
1. `l = 0`, `r = n - 1`.
2. While `l < r`: compute the sum; return `[l+1, r+1]` if it equals the target, else move one pointer.

```python
class Solution:
    def twoSum(self, numbers: List[int], target: int) -> List[int]:
        l, r = 0, len(numbers) - 1
        while l < r:
            total = numbers[l] + numbers[r]
            if total == target:
                return [l + 1, r + 1]
            if total < target:
                l += 1
            else:
                r -= 1
```

**Complexity.** Time O(n), space O(1).

**Watch out.**
- Add 1 to both indexes: the problem is 1-indexed.
- Why moving is safe: if `numbers[l] + numbers[r]` is too small, `numbers[l]` plus anything left of `r` is even smaller, so `numbers[l]` can never be part of the answer.

```test
assert Solution().twoSum([2,7,11,15], 9) == [1,2]
assert Solution().twoSum([2,3,4], 6) == [1,3]
assert Solution().twoSum([-1,0], -1) == [1,2]
```

### 11. Container With Most Water
difficulty: Medium

**Problem.** Vertical lines with heights `height[i]`. Pick two lines that, with the x-axis, hold the most water. Return that area.

**Example.** `[1,8,6,2,5,4,8,3,7]` → `49` (lines at index 1 and 8: `min(8,7) * 7`).

**Idea.** Start with the widest container (both ends). The area is limited by the **shorter** line. Moving the taller line inward can only shrink the width without raising the limit, so always move the **shorter** one.

**Steps.**
1. `l = 0`, `r = n - 1`, `best = 0`.
2. While `l < r`: `best = max(best, min(h[l], h[r]) * (r - l))`; move the pointer at the shorter line.

```python
class Solution:
    def maxArea(self, height: List[int]) -> int:
        l, r = 0, len(height) - 1
        best = 0
        while l < r:
            best = max(best, min(height[l], height[r]) * (r - l))
            if height[l] < height[r]:
                l += 1
            else:
                r -= 1
        return best
```

**Complexity.** Time O(n), space O(1).

**Watch out.** On a tie, moving either pointer is fine: any container using the current shorter line with a closer partner can't beat the current one.

```test
assert Solution().maxArea([1,8,6,2,5,4,8,3,7]) == 49
assert Solution().maxArea([1,1]) == 1
```

### 15. 3Sum
difficulty: Medium

**Problem.** Return all **unique** triplets `[a, b, c]` from `nums` with `a + b + c == 0`.

**Example.** `[-1,0,1,2,-1,-4]` → `[[-1,-1,2],[-1,0,1]]`.

**Idea.** Sort. Fix the first number `nums[i]`, then find pairs adding to `-nums[i]` in the rest with two pointers (like #167). Sorting also puts equal numbers together, which makes skipping duplicates easy.

**Steps.**
1. Sort `nums`.
2. For each `i`: stop if `nums[i] > 0`; skip if `nums[i] == nums[i-1]`.
3. `l = i + 1`, `r = n - 1`. Sum too small → `l += 1`; too big → `r -= 1`; zero → record, move both, then skip duplicate `nums[l]` values.

```python
class Solution:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        nums.sort()
        res = []
        n = len(nums)
        for i in range(n - 2):
            if nums[i] > 0:
                break
            if i > 0 and nums[i] == nums[i - 1]:
                continue
            l, r = i + 1, n - 1
            while l < r:
                total = nums[i] + nums[l] + nums[r]
                if total < 0:
                    l += 1
                elif total > 0:
                    r -= 1
                else:
                    res.append([nums[i], nums[l], nums[r]])
                    l += 1
                    r -= 1
                    while l < r and nums[l] == nums[l - 1]:
                        l += 1
        return res
```

**Complexity.** Time O(n²), space O(1) extra besides the output.

**Watch out.**
- Compare `nums[i]` with the **previous** element when skipping. Comparing with the next would wrongly skip `[-1,-1,2]`.
- Brute force (three loops) is O(n³) and times out for n = 3000.

```test
assert sorted(Solution().threeSum([-1,0,1,2,-1,-4])) == [[-1,-1,2],[-1,0,1]]
assert Solution().threeSum([0,1,1]) == []
assert Solution().threeSum([0,0,0,0]) == [[0,0,0]]
```

# Sliding Window

### 209. Minimum Size Subarray Sum
difficulty: Medium

**Problem.** Given positive integers `nums` and `target`, return the length of the shortest contiguous subarray with sum `>= target`, or 0.

**Example.** `target = 7, nums = [2,3,1,2,4,3]` → `2` (`[4,3]`).

**Idea: sliding window.** All numbers are positive, so growing the window increases the sum and shrinking decreases it. Expand on the right; while the sum is big enough, record the length and shrink from the left.

**Steps.**
1. `l = 0`, `total = 0`, `best = inf`.
2. For each `r`: add `nums[r]`. While `total >= target`: update `best`, subtract `nums[l]`, `l += 1`.
3. Return `0` if `best` is still inf.

```python
class Solution:
    def minSubArrayLen(self, target: int, nums: List[int]) -> int:
        l = total = 0
        best = float('inf')
        for r, x in enumerate(nums):
            total += x
            while total >= target:
                best = min(best, r - l + 1)
                total -= nums[l]
                l += 1
        return 0 if best == float('inf') else best
```

**Complexity.** Time O(n) (each index enters and leaves once), space O(1).

**Watch out.**
- Use `while`, not `if`, when shrinking: several removals may still keep the sum big enough.
- Follow-up O(n log n): prefix sums are strictly increasing (positive numbers), so for each start `i`, binary-search the first `j` with `prefix[j] >= prefix[i] + target`.

```test
assert Solution().minSubArrayLen(7, [2,3,1,2,4,3]) == 2
assert Solution().minSubArrayLen(4, [1,4,4]) == 1
assert Solution().minSubArrayLen(11, [1,1,1,1,1,1,1,1]) == 0
```

### 3. Longest Substring Without Repeating Characters
difficulty: Medium

**Problem.** Return the length of the longest substring with no repeated characters.

**Example.** `"abcabcbb"` → `3`; `"pwwkew"` → `3` (`"wke"`).

**Idea.** Window `s[l..r]` with no repeats. Remember the last index of each character. When the new character was seen **inside** the window, jump `l` past that previous position.

**Steps.**
1. `last = {}`, `l = 0`, `best = 0`.
2. For each `r, ch`: if `ch in last and last[ch] >= l`, set `l = last[ch] + 1`. Then `last[ch] = r`, `best = max(best, r - l + 1)`.

```python
class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        last = {}
        l = best = 0
        for r, ch in enumerate(s):
            if ch in last and last[ch] >= l:
                l = last[ch] + 1
            last[ch] = r
            best = max(best, r - l + 1)
        return best
```

**Complexity.** Time O(n), space O(k) for k distinct characters.

**Watch out.** The check `last[ch] >= l` stops `l` from jumping **backward** when the old occurrence is already outside the window (try `"abba"`: the answer is 2, not 3).

```test
assert Solution().lengthOfLongestSubstring("abcabcbb") == 3
assert Solution().lengthOfLongestSubstring("bbbbb") == 1
assert Solution().lengthOfLongestSubstring("pwwkew") == 3
assert Solution().lengthOfLongestSubstring("abba") == 2
assert Solution().lengthOfLongestSubstring("") == 0
```

### 30. Substring with Concatenation of All Words
difficulty: Hard

**Problem.** All strings in `words` have the same length. Return every start index in `s` of a substring that is a concatenation of **all** the words exactly once, in any order.

**Example.** `s = "barfoothefoobarman", words = ["foo","bar"]` → `[0,9]`.

**Idea.** Words have a fixed length `w`, so cut `s` into word-sized pieces. For each of the `w` possible offsets (0..w-1), slide a window **word by word**, keeping a `Counter` of the words inside. If a word appears too often, shrink from the left; if the window holds exactly all words, record its start.

**Steps.**
1. `need = Counter(words)`, `w = len(words[0])`, `k = len(words)`.
2. For each `offset` in `range(w)`: `left = offset`, `seen = Counter()`, `count = 0`.
3. For `right` stepping by `w`: take `word = s[right:right+w]`.
   - Not in `need`: reset the window (`seen.clear()`, `count = 0`, `left = right + w`).
   - Else add it; while `seen[word] > need[word]`, remove the leftmost word and move `left`.
   - If `count == k`, record `left`.

```python
class Solution:
    def findSubstring(self, s: str, words: List[str]) -> List[int]:
        w, k = len(words[0]), len(words)
        need = Counter(words)
        res = []
        for offset in range(w):
            left = offset
            seen = Counter()
            count = 0
            for right in range(offset, len(s) - w + 1, w):
                word = s[right:right + w]
                if word not in need:
                    seen.clear()
                    count = 0
                    left = right + w
                    continue
                seen[word] += 1
                count += 1
                while seen[word] > need[word]:
                    seen[s[left:left + w]] -= 1
                    count -= 1
                    left += w
                if count == k:
                    res.append(left)
        return res
```

**Complexity.** Time O(len(s) · w) overall (each offset scans `s` once, each word slice costs w), space O(k).

**Watch out.** When the window is full (`count == k`), the next added word triggers the shrink automatically, because some word count will exceed what's needed or the left word gets removed. Don't forget to try every offset `0..w-1`, otherwise matches starting at other alignments are missed.

```test
assert sorted(Solution().findSubstring("barfoothefoobarman", ["foo","bar"])) == [0,9]
assert Solution().findSubstring("wordgoodgoodgoodbestword", ["word","good","best","word"]) == []
assert sorted(Solution().findSubstring("barfoofoobarthefoobarman", ["bar","foo","the"])) == [6,9,12]
assert Solution().findSubstring("aaaa", ["aa","aa"]) == [0]
```

### 76. Minimum Window Substring
difficulty: Hard

**Problem.** Return the shortest substring of `s` that contains every character of `t` (with multiplicity), or `""`.

**Example.** `s = "ADOBECODEBANC", t = "ABC"` → `"BANC"`.

**Idea.** Sliding window with counts. `need` counts the characters of `t`; `missing` is how many characters (with duplicates) the window still lacks. Expand right until `missing == 0`, then shrink from the left as far as possible while still valid, recording the best window.

**Steps.**
1. `need = Counter(t)`, `missing = len(t)`, `l = 0`.
2. For each `r, ch`: if `need[ch] > 0`, `missing -= 1`; then `need[ch] -= 1` (it can go negative = surplus).
3. When `missing == 0`: move `l` right while `need[s[l]] < 0` (surplus characters), restoring `need`. Record the window. Then remove `s[l]` to break validity (`need[s[l]] += 1`, `missing += 1`, `l += 1`).

```python
class Solution:
    def minWindow(self, s: str, t: str) -> str:
        need = Counter(t)
        missing = len(t)
        l = 0
        best = (float('inf'), 0, 0)
        for r, ch in enumerate(s):
            if need[ch] > 0:
                missing -= 1
            need[ch] -= 1
            if missing == 0:
                while need[s[l]] < 0:        # drop surplus characters
                    need[s[l]] += 1
                    l += 1
                if r - l + 1 < best[0]:
                    best = (r - l + 1, l, r)
                need[s[l]] += 1              # break the window to look for a shorter one
                missing += 1
                l += 1
        return "" if best[0] == float('inf') else s[best[1]:best[2] + 1]
```

**Complexity.** Time O(|s| + |t|), space O(k) distinct characters.

**Watch out.** `need[ch]` going negative means "the window has more of this character than required"; those are exactly the characters you can drop from the left.

```test
assert Solution().minWindow("ADOBECODEBANC", "ABC") == "BANC"
assert Solution().minWindow("a", "a") == "a"
assert Solution().minWindow("a", "aa") == ""
assert Solution().minWindow("aa", "aa") == "aa"
```

# Matrix

### 36. Valid Sudoku
difficulty: Medium

**Problem.** Check whether a partially filled 9×9 board is valid: no digit repeats in any row, column, or 3×3 box (empty cells are `"."`). It doesn't need to be solvable.

**Idea.** One pass with sets: for each digit, remember it for its row, its column, and its box. The box index is `(r // 3) * 3 + c // 3`.

**Steps.**
1. `rows`, `cols`, `boxes` = 9 empty sets each.
2. For every filled cell: if the digit is already in its row, column or box set, return false; otherwise add it to all three.

```python
class Solution:
    def isValidSudoku(self, board: List[List[str]]) -> bool:
        rows = [set() for _ in range(9)]
        cols = [set() for _ in range(9)]
        boxes = [set() for _ in range(9)]
        for r in range(9):
            for c in range(9):
                d = board[r][c]
                if d == '.':
                    continue
                b = (r // 3) * 3 + c // 3
                if d in rows[r] or d in cols[c] or d in boxes[b]:
                    return False
                rows[r].add(d)
                cols[c].add(d)
                boxes[b].add(d)
        return True
```

**Complexity.** O(81) = O(1) time and space.

**Watch out.** `[set()] * 9` would create 9 references to the **same** set; use a list comprehension.

```test
b = [["5","3",".",".","7",".",".",".","."],["6",".",".","1","9","5",".",".","."],[".","9","8",".",".",".",".","6","."],["8",".",".",".","6",".",".",".","3"],["4",".",".","8",".","3",".",".","1"],["7",".",".",".","2",".",".",".","6"],[".","6",".",".",".",".","2","8","."],[".",".",".","4","1","9",".",".","5"],[".",".",".",".","8",".",".","7","9"]]
assert Solution().isValidSudoku(b) is True
b2 = [row[:] for row in b]; b2[0][0] = "8"
assert Solution().isValidSudoku(b2) is False
```

### 54. Spiral Matrix
difficulty: Medium

**Problem.** Return all elements of an `m × n` matrix in spiral order (right, down, left, up, repeat).

**Example.** `[[1,2,3],[4,5,6],[7,8,9]]` → `[1,2,3,6,9,8,7,4,5]`.

**Idea.** Keep four boundaries: `top`, `bottom`, `left`, `right`. Walk the top row, right column, bottom row, left column, shrinking the boundary after each side.

**Steps.**
1. While `top <= bottom and left <= right`:
2. Top row left→right, then `top += 1`. Right column top→bottom, then `right -= 1`.
3. If `top <= bottom`: bottom row right→left, `bottom -= 1`. If `left <= right`: left column bottom→top, `left += 1`.

```python
class Solution:
    def spiralOrder(self, matrix: List[List[int]]) -> List[int]:
        res = []
        top, bottom = 0, len(matrix) - 1
        left, right = 0, len(matrix[0]) - 1
        while top <= bottom and left <= right:
            for c in range(left, right + 1):
                res.append(matrix[top][c])
            top += 1
            for r in range(top, bottom + 1):
                res.append(matrix[r][right])
            right -= 1
            if top <= bottom:
                for c in range(right, left - 1, -1):
                    res.append(matrix[bottom][c])
                bottom -= 1
            if left <= right:
                for r in range(bottom, top - 1, -1):
                    res.append(matrix[r][left])
                left += 1
        return res
```

**Complexity.** Time O(m·n), space O(1) besides the output.

**Watch out.** The two `if` checks prevent reading a single remaining row or column twice (try a 3×4 or 1×3 matrix).

```test
assert Solution().spiralOrder([[1,2,3],[4,5,6],[7,8,9]]) == [1,2,3,6,9,8,7,4,5]
assert Solution().spiralOrder([[1,2,3,4],[5,6,7,8],[9,10,11,12]]) == [1,2,3,4,8,12,11,10,9,5,6,7]
assert Solution().spiralOrder([[1,2,3]]) == [1,2,3]
assert Solution().spiralOrder([[1],[2],[3]]) == [1,2,3]
```

### 48. Rotate Image
difficulty: Medium

**Problem.** Rotate an `n × n` matrix 90° clockwise **in place**.

**Example.** `[[1,2,3],[4,5,6],[7,8,9]]` → `[[7,4,1],[8,5,2],[9,6,3]]`.

**Idea.** A clockwise rotation = **transpose** (swap across the main diagonal) + **reverse each row**.

**Steps.**
1. For `i < j`: swap `m[i][j]` and `m[j][i]`.
2. Reverse every row.

```python
class Solution:
    def rotate(self, matrix: List[List[int]]) -> None:
        n = len(matrix)
        for i in range(n):
            for j in range(i + 1, n):
                matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
        for row in matrix:
            row.reverse()
```

**Complexity.** Time O(n²), space O(1).

**Watch out.** In the transpose, `j` must start at `i + 1`; looping over all pairs swaps each pair twice and undoes the transpose. For counter-clockwise: transpose, then reverse each **column** (or reverse rows first, then transpose).

```test
m = [[1,2,3],[4,5,6],[7,8,9]]; Solution().rotate(m); assert m == [[7,4,1],[8,5,2],[9,6,3]]
m = [[5,1,9,11],[2,4,8,10],[13,3,6,7],[15,14,12,16]]; Solution().rotate(m); assert m == [[15,13,2,5],[14,3,4,1],[12,6,8,9],[16,7,10,11]]
```

### 73. Set Matrix Zeroes
difficulty: Medium

**Problem.** If a cell is 0, set its whole row and column to 0, in place. Follow-up: O(1) extra space.

**Idea.** Use the **first row and first column as markers**: `matrix[r][0] = 0` means "row r must be zeroed", `matrix[0][c] = 0` means "column c must be zeroed". The first row and column themselves need two separate flags, because they're being used as storage.

**Steps.**
1. Record whether the first row and first column originally contain a 0.
2. For every other cell that's 0, set its markers `matrix[r][0]` and `matrix[0][c]` to 0.
3. Zero every inner cell whose row or column marker is 0.
4. Finally zero the first row / first column if their flags say so.

```python
class Solution:
    def setZeroes(self, matrix: List[List[int]]) -> None:
        m, n = len(matrix), len(matrix[0])
        first_row = any(matrix[0][c] == 0 for c in range(n))
        first_col = any(matrix[r][0] == 0 for r in range(m))

        for r in range(1, m):
            for c in range(1, n):
                if matrix[r][c] == 0:
                    matrix[r][0] = 0
                    matrix[0][c] = 0

        for r in range(1, m):
            for c in range(1, n):
                if matrix[r][0] == 0 or matrix[0][c] == 0:
                    matrix[r][c] = 0

        if first_row:
            for c in range(n):
                matrix[0][c] = 0
        if first_col:
            for r in range(m):
                matrix[r][0] = 0
```

**Complexity.** Time O(m·n), space O(1).

**Watch out.** Simpler O(m + n) version: collect zero rows and columns into two sets first, then zero them. Don't zero cells while scanning, or new zeros will spread incorrectly.

```test
m = [[1,1,1],[1,0,1],[1,1,1]]; Solution().setZeroes(m); assert m == [[1,0,1],[0,0,0],[1,0,1]]
m = [[0,1,2,0],[3,4,5,2],[1,3,1,5]]; Solution().setZeroes(m); assert m == [[0,0,0,0],[0,4,5,0],[0,3,1,0]]
```

### 289. Game of Life
difficulty: Medium

**Problem.** Apply one step of Conway's Game of Life to a 0/1 board **in place**. Live cell: survives with 2 or 3 live neighbours, else dies. Dead cell: becomes alive with exactly 3 live neighbours.

**Idea.** All cells must update at the same time, so you can't overwrite values you still need. Encode both states in one number: bit 0 = current state, bit 1 = next state. Count neighbours using `cell & 1`, then shift everything right at the end.

**Steps.**
1. For each cell, count live neighbours with `board[x][y] & 1`.
2. If the cell will be alive next step, set bit 1: `board[r][c] |= 2`.
3. After the whole pass, `board[r][c] >>= 1`.

```python
class Solution:
    def gameOfLife(self, board: List[List[int]]) -> None:
        m, n = len(board), len(board[0])
        for r in range(m):
            for c in range(n):
                live = 0
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if (dr or dc) and 0 <= r + dr < m and 0 <= c + dc < n:
                            live += board[r + dr][c + dc] & 1
                if board[r][c] & 1:
                    if live in (2, 3):
                        board[r][c] |= 2
                elif live == 3:
                    board[r][c] |= 2
        for r in range(m):
            for c in range(n):
                board[r][c] >>= 1
```

**Complexity.** Time O(m·n), space O(1).

**Watch out.** `(dr or dc)` skips the cell itself. Reading `& 1` always gives the **old** state even after bit 1 was set.

```test
b = [[0,1,0],[0,0,1],[1,1,1],[0,0,0]]; Solution().gameOfLife(b); assert b == [[0,0,0],[1,0,1],[0,1,1],[0,1,0]]
b = [[1,1],[1,0]]; Solution().gameOfLife(b); assert b == [[1,1],[1,1]]
```

# Hashmap

### 383. Ransom Note
difficulty: Easy

**Problem.** Can `ransomNote` be built from the letters of `magazine`, each letter used at most once?

**Idea.** Count the magazine letters, then use one count per note letter. If a letter runs out, return false.

**Steps.**
1. `count = Counter(magazine)`.
2. For each `c` in the note: if `count[c] == 0`, return false; else `count[c] -= 1`.

```python
class Solution:
    def canConstruct(self, ransomNote: str, magazine: str) -> bool:
        count = Counter(magazine)
        for c in ransomNote:
            if count[c] == 0:
                return False
            count[c] -= 1
        return True
```

**Complexity.** Time O(m + n), space O(1) (26 letters).

**Watch out.** `Counter` returns 0 for missing keys, so no `KeyError`. One-liner: `return not (Counter(ransomNote) - Counter(magazine))`.

```test
assert Solution().canConstruct("a", "b") is False
assert Solution().canConstruct("aa", "ab") is False
assert Solution().canConstruct("aa", "aab") is True
```

### 205. Isomorphic Strings
difficulty: Easy

**Problem.** Can each character of `s` be replaced to get `t`, where a character always maps to the same character and no two characters map to the same one?

**Example.** `"egg", "add"` → `true`; `"f11", "b23"` → `false`; `"paper", "title"` → `true`.

**Idea.** The mapping must be one-to-one in **both** directions, so keep two dictionaries.

**Steps.**
1. For each pair `(a, b)` from `zip(s, t)`:
2. If `a` already maps to something other than `b`, or `b` is already mapped from something other than `a`, return false.
3. Record both directions.

```python
class Solution:
    def isIsomorphic(self, s: str, t: str) -> bool:
        s_to_t, t_to_s = {}, {}
        for a, b in zip(s, t):
            if a in s_to_t and s_to_t[a] != b:
                return False
            if b in t_to_s and t_to_s[b] != a:
                return False
            s_to_t[a] = b
            t_to_s[b] = a
        return True
```

**Complexity.** Time O(n), space O(k) distinct characters.

**Watch out.** One dictionary isn't enough: `"ab"` vs `"cc"` would pass with only `s → t`. Short trick: `len(set(s)) == len(set(t)) == len(set(zip(s, t)))`.

```test
assert Solution().isIsomorphic("egg", "add") is True
assert Solution().isIsomorphic("f11", "b23") is False
assert Solution().isIsomorphic("paper", "title") is True
assert Solution().isIsomorphic("ab", "cc") is False
```

### 290. Word Pattern
difficulty: Easy

**Problem.** Does string `s` (words separated by single spaces) follow `pattern`, with a one-to-one match between letters and words?

**Example.** `pattern = "abba", s = "dog cat cat dog"` → `true`; `"dog cat cat fish"` → `false`.

**Idea.** Same as #205, but letters ↔ words. Check lengths first, because `zip` silently stops at the shorter one.

**Steps.**
1. Split `s` into `words`.
2. If `len(pattern) != len(words)`, return `False` (`zip` would silently ignore the extra items).
3. Keep two maps: letter → word and word → letter.
4. For each pair `(c, w)`: if `c` is already mapped to a different word, or `w` to a different letter, return `False`.
5. Otherwise record both directions. If the loop ends, return `True`.

```python
class Solution:
    def wordPattern(self, pattern: str, s: str) -> bool:
        words = s.split()
        if len(pattern) != len(words):
            return False
        c_to_w, w_to_c = {}, {}
        for c, w in zip(pattern, words):
            if c in c_to_w and c_to_w[c] != w:
                return False
            if w in w_to_c and w_to_c[w] != c:
                return False
            c_to_w[c] = w
            w_to_c[w] = c
        return True
```

**Complexity.** Time O(n + L), space O(n).

**Watch out.** Without the length check, `"abba"` vs `"dog cat cat"` would wrongly pass. Short version: `len(set(pattern)) == len(set(words)) == len(set(zip(pattern, words)))` after the length check.

```test
assert Solution().wordPattern("abba", "dog cat cat dog") is True
assert Solution().wordPattern("abba", "dog cat cat fish") is False
assert Solution().wordPattern("aaaa", "dog cat cat dog") is False
assert Solution().wordPattern("ab", "dog dog") is False
assert Solution().wordPattern("aaa", "aa aa aa aa") is False
```

### 242. Valid Anagram
difficulty: Easy

**Problem.** Is `t` an anagram of `s` (same letters, same counts, any order)?

**Idea.** Different lengths → false. Otherwise count letters of `s` and consume them with `t`.

**Steps.**
1. If the lengths differ, they can't be anagrams → `False`.
2. Count the letters of `s` with `Counter`.
3. Walk through `t`: if a letter's count is already 0, `t` has too many of it → `False`; otherwise decrease the count.
4. If every letter was consumed, return `True`.

```python
class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False
        count = Counter(s)
        for c in t:
            if count[c] == 0:
                return False
            count[c] -= 1
        return True
```

**Complexity.** Time O(n), space O(1) for lowercase letters.

**Watch out.**
- Same set of letters isn't enough: `"aab"` and `"abb"` are not anagrams.
- Short versions: `Counter(s) == Counter(t)` or `sorted(s) == sorted(t)` (O(n log n)).
- Unicode follow-up: the 26-slot array trick breaks, but a dictionary/`Counter` works for any character (normalize strings with `unicodedata.normalize` first).

```test
assert Solution().isAnagram("anagram", "nagaram") is True
assert Solution().isAnagram("rat", "car") is False
assert Solution().isAnagram("aab", "abb") is False
```

### 49. Group Anagrams
difficulty: Medium

**Problem.** Group the strings that are anagrams of each other.

**Example.** `["eat","tea","tan","ate","nat","bat"]` → `[["bat"],["nat","tan"],["ate","eat","tea"]]` (any order).

**Idea.** Anagrams share the same **key**: the sorted letters (`"eat"` → `"aet"`). Group words by that key in a dictionary.

**Steps.**
1. `groups = defaultdict(list)`.
2. For each word: `groups[''.join(sorted(word))].append(word)`.
3. Return the dictionary values.

```python
class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        groups = defaultdict(list)
        for w in strs:
            groups[''.join(sorted(w))].append(w)
        return list(groups.values())
```

**Complexity.** Time O(n · k log k) for words of length k, space O(n·k).

**Watch out.** Faster key, O(k): a tuple of 26 letter counts, `key = tuple(count)`. A list can't be a dictionary key, a tuple can.

```test
res = Solution().groupAnagrams(["eat","tea","tan","ate","nat","bat"])
assert sorted(sorted(g) for g in res) == [["ate","eat","tea"],["bat"],["nat","tan"]]
assert Solution().groupAnagrams([""]) == [[""]]
```

### 1. Two Sum
difficulty: Easy

**Problem.** Return the indexes of the two numbers that add up to `target` (exactly one answer; can't use the same element twice). Follow-up: better than O(n²).

**Example.** `[2,7,11,15], 9` → `[0,1]`.

**Idea.** For each number `x`, the partner you need is `target - x`. Keep a dictionary of numbers seen so far → index. Check for the partner **before** storing `x`.

**Steps.**
1. `seen = {}`.
2. For each `i, x`: if `target - x` is in `seen`, return `[seen[target - x], i]`. Else `seen[x] = i`.

```python
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        seen = {}
        for i, x in enumerate(nums):
            if target - x in seen:
                return [seen[target - x], i]
            seen[x] = i
```

**Complexity.** Time O(n), space O(n).

**Watch out.** Checking before storing is what prevents using the same element twice (`[3,2,4], 6` must not return `[0,0]`). Duplicates like `[3,3]` still work.

```test
assert Solution().twoSum([2,7,11,15], 9) == [0,1]
assert Solution().twoSum([3,2,4], 6) == [1,2]
assert Solution().twoSum([3,3], 6) == [0,1]
```

### 202. Happy Number
difficulty: Easy

**Problem.** Repeatedly replace `n` by the sum of the squares of its digits. If it reaches 1, `n` is happy; if it loops forever, it isn't.

**Example.** `19` → `1² + 9² = 82 → 68 → 100 → 1` → `true`.

**Idea.** The sequence either reaches 1 or falls into a cycle. Detect the cycle with a set of seen numbers (or Floyd's slow/fast pointers for O(1) space).

**Steps.**
1. While `n != 1` and `n` not seen: add `n` to `seen`, replace `n` with the digit-square sum.
2. Return `n == 1`.

```python
class Solution:
    def isHappy(self, n: int) -> bool:
        def nxt(x):
            total = 0
            while x:
                x, d = divmod(x, 10)
                total += d * d
            return total

        seen = set()
        while n != 1 and n not in seen:
            seen.add(n)
            n = nxt(n)
        return n == 1
```

**Complexity.** Time O(log n) per step and the values quickly drop below a few hundred; space O(log n).

**Watch out.** O(1)-space version (like Linked List Cycle): `slow = nxt(slow)`, `fast = nxt(nxt(fast))` until they meet; happy if they meet at 1.

```test
assert Solution().isHappy(19) is True
assert Solution().isHappy(2) is False
assert Solution().isHappy(1) is True
```

### 219. Contains Duplicate II
difficulty: Easy

**Problem.** Are there two different indexes `i`, `j` with `nums[i] == nums[j]` and `|i - j| <= k`?

**Example.** `[1,0,1,1], k = 1` → `true`.

**Idea.** Remember the last index of each value. When you see a value again, check the distance to its **most recent** index.

**Steps.**
1. `last = {}`.
2. For each `i, x`: if `x in last and i - last[x] <= k`, return true. Then `last[x] = i` (always overwrite).

```python
class Solution:
    def containsNearbyDuplicate(self, nums: List[int], k: int) -> bool:
        last = {}
        for i, x in enumerate(nums):
            if x in last and i - last[x] <= k:
                return True
            last[x] = i
        return False
```

**Complexity.** Time O(n), space O(n).

**Watch out.** Always update `last[x]` even when the distance was too large: the next occurrence should compare with the closest one. Sliding-window alternative with O(k) space: keep a set of the last `k` values and remove `nums[i - k]` as the window moves.

```test
assert Solution().containsNearbyDuplicate([1,2,3,1], 3) is True
assert Solution().containsNearbyDuplicate([1,0,1,1], 1) is True
assert Solution().containsNearbyDuplicate([1,2,3,1,2,3], 2) is False
```

### 128. Longest Consecutive Sequence
difficulty: Medium

**Problem.** Return the length of the longest run of consecutive integers (in any order in the array), in O(n).

**Example.** `[100,4,200,1,3,2]` → `4` (`1,2,3,4`).

**Idea.** Put everything in a set. A number `x` **starts** a run only if `x - 1` isn't in the set. From each start, count upward. Every number is visited at most twice, so it's O(n).

**Steps.**
1. `s = set(nums)`.
2. For each `x` in `s` with `x - 1` not in `s`: count `y = x, x+1, ...` while in the set.
3. Track the longest count.

```python
class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        s = set(nums)
        best = 0
        for x in s:
            if x - 1 not in s:
                y = x
                while y + 1 in s:
                    y += 1
                best = max(best, y - x + 1)
        return best
```

**Complexity.** Time O(n), space O(n).

**Watch out.** Loop over the **set**, not the list: with many duplicates, looping the list would repeat the same counting.

```test
assert Solution().longestConsecutive([100,4,200,1,3,2]) == 4
assert Solution().longestConsecutive([0,3,7,2,5,8,4,6,0,1]) == 9
assert Solution().longestConsecutive([]) == 0
```

# Intervals

### 228. Summary Ranges
difficulty: Easy

**Problem.** Given a sorted list of unique integers, return the smallest list of ranges covering them, formatted `"a->b"` or `"a"`.

**Example.** `[0,1,2,4,5,7]` → `["0->2","4->5","7"]`.

**Idea.** Walk the array; extend the current run while the next number is exactly one more.

**Steps.**
1. `i = 0`. While `i < n`: `start = nums[i]`.
2. While `i + 1 < n` and `nums[i+1] == nums[i] + 1`: `i += 1`.
3. Append `"start"` or `"start->nums[i]"`, then `i += 1`.

```python
class Solution:
    def summaryRanges(self, nums: List[int]) -> List[str]:
        res = []
        i, n = 0, len(nums)
        while i < n:
            start = nums[i]
            while i + 1 < n and nums[i + 1] == nums[i] + 1:
                i += 1
            res.append(str(start) if start == nums[i] else f"{start}->{nums[i]}")
            i += 1
        return res
```

**Complexity.** Time O(n), space O(1) besides the output.

**Watch out.** Check `i + 1 < n` first so you never read past the end. The empty list returns `[]` naturally.

```test
assert Solution().summaryRanges([0,1,2,4,5,7]) == ["0->2","4->5","7"]
assert Solution().summaryRanges([0,2,3,4,6,8,9]) == ["0","2->4","6","8->9"]
assert Solution().summaryRanges([]) == []
```

### 56. Merge Intervals
difficulty: Medium

**Problem.** Merge all overlapping intervals.

**Example.** `[[1,3],[2,6],[8,10],[15,18]]` → `[[1,6],[8,10],[15,18]]`. Touching intervals (`[1,4],[4,5]`) count as overlapping.

**Idea.** Sort by start; then any interval that overlaps the current merged block comes right after it.

**Steps.**
1. Sort by start; `res = [first interval]`.
2. For each next `[s, e]`: if `s <= res[-1][1]`, extend `res[-1][1] = max(res[-1][1], e)`; else append it.

```python
class Solution:
    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
        intervals.sort(key=lambda x: x[0])
        res = [intervals[0][:]]
        for s, e in intervals[1:]:
            if s <= res[-1][1]:
                res[-1][1] = max(res[-1][1], e)
            else:
                res.append([s, e])
        return res
```

**Complexity.** Time O(n log n), space O(n).

**Watch out.**
- `<=` makes touching intervals merge.
- `max` is needed because an interval can sit inside the previous one (`[1,10]` then `[2,3]`).

```test
assert Solution().merge([[1,3],[2,6],[8,10],[15,18]]) == [[1,6],[8,10],[15,18]]
assert Solution().merge([[1,4],[4,5]]) == [[1,5]]
assert Solution().merge([[4,7],[1,4]]) == [[1,7]]
assert Solution().merge([[1,10],[2,3]]) == [[1,10]]
```

### 57. Insert Interval
difficulty: Medium

**Problem.** `intervals` is sorted and non-overlapping. Insert `newInterval` and merge if needed.

**Example.** `[[1,3],[6,9]]`, new `[2,5]` → `[[1,5],[6,9]]`.

**Idea.** The intervals are sorted, so they fall into three groups in order: the ones entirely before the new interval, the ones that overlap it (merge them all into it), and the ones entirely after it. One pass with a single index handles all three.

**Steps.**
1. Phase 1: copy every interval that ends **before** the new one starts (`end < s`).
2. Phase 2: while intervals start at or before the new one's end (`start <= e`), they overlap: merge by `s = min(...)`, `e = max(...)`.
3. Append the merged `[s, e]`.
4. Phase 3: copy all the remaining intervals unchanged. Return the result.

```python
class Solution:
    def insert(self, intervals: List[List[int]], newInterval: List[int]) -> List[List[int]]:
        res = []
        i, n = 0, len(intervals)
        s, e = newInterval
        while i < n and intervals[i][1] < s:
            res.append(intervals[i])
            i += 1
        while i < n and intervals[i][0] <= e:
            s = min(s, intervals[i][0])
            e = max(e, intervals[i][1])
            i += 1
        res.append([s, e])
        res.extend(intervals[i:])
        return res
```

**Complexity.** Time O(n), space O(n).

**Watch out.** The overlap condition is `intervals[i][0] <= e` (touching counts). No sorting needed: the input is already sorted.

```test
assert Solution().insert([[1,3],[6,9]], [2,5]) == [[1,5],[6,9]]
assert Solution().insert([[1,2],[3,5],[6,7],[8,10],[12,16]], [4,8]) == [[1,2],[3,10],[12,16]]
assert Solution().insert([], [5,7]) == [[5,7]]
assert Solution().insert([[1,5]], [6,8]) == [[1,5],[6,8]]
```

### 452. Minimum Number of Arrows to Burst Balloons
difficulty: Medium

**Problem.** Balloons are horizontal intervals `[start, end]`. An arrow shot at `x` bursts every balloon with `start <= x <= end`. Return the minimum number of arrows.

**Example.** `[[10,16],[2,8],[1,6],[7,12]]` → `2` (shoot at 6 and 11).

**Idea: greedy by end.** Sort by end. Shoot the first arrow at the end of the first balloon (as far right as possible while still hitting it). Every balloon starting at or before that point is burst; the first one starting after it needs a new arrow at its end.

**Steps.**
1. Sort by end. `arrows = 1`, `pos = points[0][1]`.
2. For each balloon: if `start > pos`, `arrows += 1`, `pos = end`.

```python
class Solution:
    def findMinArrowShots(self, points: List[List[int]]) -> int:
        points.sort(key=lambda p: p[1])
        arrows = 1
        pos = points[0][1]
        for start, end in points[1:]:
            if start > pos:
                arrows += 1
                pos = end
        return arrows
```

**Complexity.** Time O(n log n), space O(1) extra.

**Watch out.** Use `start > pos` (strictly): a balloon starting exactly at `pos` is still hit. Sorting by **end** is the key; sorting by start needs extra `min` updates.

```test
assert Solution().findMinArrowShots([[10,16],[2,8],[1,6],[7,12]]) == 2
assert Solution().findMinArrowShots([[1,2],[3,4],[5,6],[7,8]]) == 4
assert Solution().findMinArrowShots([[1,2],[2,3],[3,4],[4,5]]) == 2
```
