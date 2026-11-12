# Problems that appear only in Top 100 Liked

### 560. Subarray Sum Equals K
difficulty: Medium

**Problem.** Count the contiguous subarrays whose sum equals `k` (numbers can be negative).

**Example.** `[1,1,1], k = 2` → `2`.

**Idea: prefix sums + hash map.** If `prefix[j] - prefix[i] == k`, the subarray between them sums to `k`. While walking, count how many earlier prefixes equal `current - k`.

**Steps.**
1. `seen = {0: 1}` (the empty prefix), `cur = 0`, `count = 0`.
2. For each `x`: `cur += x`; `count += seen.get(cur - k, 0)`; `seen[cur] += 1`.

```python
class Solution:
    def subarraySum(self, nums: List[int], k: int) -> int:
        seen = defaultdict(int)
        seen[0] = 1
        cur = count = 0
        for x in nums:
            cur += x
            count += seen[cur - k]
            seen[cur] += 1
        return count
```

**Complexity.** Time O(n), space O(n).

**Watch out.** A sliding window doesn't work here because of negative numbers. `seen[0] = 1` counts subarrays that start at index 0.

```test
assert Solution().subarraySum([1,1,1], 2) == 2
assert Solution().subarraySum([1,2,3], 3) == 2
assert Solution().subarraySum([1,-1,0], 0) == 3
```

### 283. Move Zeroes
difficulty: Easy

**Problem.** Move all zeros to the end in place, keeping the order of the other elements.

**Idea.** Write pointer `k` for the next non-zero position. Swap each non-zero element into position `k`.

**Steps.**
1. `k` is where the next non-zero number should go; start at 0.
2. Scan with `i`. When `nums[i]` isn't 0, swap it into position `k` and move `k` forward.
3. Non-zeros keep their order, and the zeros end up at the back.

```python
class Solution:
    def moveZeroes(self, nums: List[int]) -> None:
        k = 0
        for i in range(len(nums)):
            if nums[i] != 0:
                nums[k], nums[i] = nums[i], nums[k]
                k += 1
```

**Complexity.** Time O(n), space O(1).

**Watch out.** Swapping (instead of copying and filling zeros later) does it in one pass.

```test
a = [0,1,0,3,12]; Solution().moveZeroes(a); assert a == [1,3,12,0,0]
a = [0]; Solution().moveZeroes(a); assert a == [0]
```

### 438. Find All Anagrams in a String
difficulty: Medium

**Problem.** Return the start indexes of all substrings of `s` that are anagrams of `p`.

**Example.** `s = "cbaebabacd", p = "abc"` → `[0,6]`.

**Idea.** Fixed-size sliding window of length `len(p)`: keep letter counts of the window and compare with `p`'s counts (26 letters, so the comparison is O(1)).

**Steps.**
1. If `p` is longer than `s`, return `[]`.
2. Count the letters of `p` in `need` (26 slots).
3. Slide over `s`: add the new letter to `window`.
4. Once the window is longer than `len(p)`, remove the letter that left: `s[i - m]`.
5. If `window == need`, record the start index `i - m + 1`.

```python
class Solution:
    def findAnagrams(self, s: str, p: str) -> List[int]:
        m = len(p)
        if m > len(s):
            return []
        need = [0] * 26
        window = [0] * 26
        for ch in p:
            need[ord(ch) - 97] += 1
        res = []
        for i, ch in enumerate(s):
            window[ord(ch) - 97] += 1
            if i >= m:
                window[ord(s[i - m]) - 97] -= 1
            if window == need:
                res.append(i - m + 1)
        return res
```

**Complexity.** Time O(26·n), space O(1).

**Watch out.** The comparison only makes sense once the window is full, but before that it can't be equal anyway (fewer letters than `p`).

```test
assert Solution().findAnagrams("cbaebabacd", "abc") == [0,6]
assert Solution().findAnagrams("abab", "ab") == [0,1,2]
assert Solution().findAnagrams("a", "ab") == []
```

### 239. Sliding Window Maximum
difficulty: Hard

**Problem.** Return the maximum of every window of size `k`.

**Example.** `[1,3,-1,-3,5,3,6,7], k = 3` → `[3,3,5,5,6,7]`.

**Idea: monotonic deque.** Keep indexes in a deque whose values are **decreasing**. A new value removes every smaller value from the back (they can never be a max again). The front is the current max; drop it when it slides out of the window.

**Steps.**
1. For each `i`: pop from the back while `nums[back] <= nums[i]`; push `i`.
2. If the front index is `<= i - k`, pop it from the front.
3. Once `i >= k - 1`, record `nums[front]`.

```python
class Solution:
    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
        dq = deque()
        res = []
        for i, x in enumerate(nums):
            while dq and nums[dq[-1]] <= x:
                dq.pop()
            dq.append(i)
            if dq[0] <= i - k:
                dq.popleft()
            if i >= k - 1:
                res.append(nums[dq[0]])
        return res
```

**Complexity.** Time O(n) (each index pushed and popped once), space O(k).

**Watch out.** Store **indexes**, not values, so you know when the front leaves the window. A heap also works (O(n log n)) with lazy removal.

```test
assert Solution().maxSlidingWindow([1,3,-1,-3,5,3,6,7], 3) == [3,3,5,5,6,7]
assert Solution().maxSlidingWindow([1], 1) == [1]
assert Solution().maxSlidingWindow([9,8,7,6], 2) == [9,8,7]
```

### 41. First Missing Positive
difficulty: Hard

**Problem.** Return the smallest positive integer missing from an unsorted array, in O(n) time and O(1) extra space.

**Example.** `[3,4,-1,1]` → `2`; `[7,8,9,11,12]` → `1`.

**Idea: cyclic sort / index as a hash.** The answer is in `1..n+1`. Place every value `v` in `1..n` at index `v - 1` by swapping. Then the first index `i` with `nums[i] != i + 1` gives `i + 1`.

**Steps.**
1. For each `i`: while `1 <= nums[i] <= n` and `nums[nums[i] - 1] != nums[i]`, swap `nums[i]` into its home.
2. Scan for the first mismatch; if none, return `n + 1`.

```python
class Solution:
    def firstMissingPositive(self, nums: List[int]) -> int:
        n = len(nums)
        for i in range(n):
            while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
                j = nums[i] - 1
                nums[i], nums[j] = nums[j], nums[i]
        for i in range(n):
            if nums[i] != i + 1:
                return i + 1
        return n + 1
```

**Complexity.** Time O(n) (each swap puts one value home for good), space O(1).

**Watch out.** The check `nums[nums[i] - 1] != nums[i]` stops infinite swapping with duplicates. Compute `j` before swapping; `nums[i], nums[nums[i] - 1] = ...` changes `nums[i]` mid-assignment and breaks.

```test
assert Solution().firstMissingPositive([1,2,0]) == 3
assert Solution().firstMissingPositive([3,4,-1,1]) == 2
assert Solution().firstMissingPositive([7,8,9,11,12]) == 1
assert Solution().firstMissingPositive([1,1]) == 2
```

### 240. Search a 2D Matrix II
difficulty: Medium

**Problem.** Rows are sorted left to right and columns top to bottom. Is `target` in the matrix?

**Idea: staircase search.** Start at the **top-right** corner. If the value is too big, everything below it in that column is bigger too: move left. If too small, everything to its left is smaller: move down.

**Steps.**
1. Start at the top-right cell.
2. If the value equals the target → `True`.
3. If it's bigger, everything below it in that column is bigger too: move left.
4. If it's smaller, everything to its left in that row is smaller too: move down.
5. If you leave the matrix → `False`.

```python
class Solution:
    def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:
        r, c = 0, len(matrix[0]) - 1
        while r < len(matrix) and c >= 0:
            v = matrix[r][c]
            if v == target:
                return True
            if v > target:
                c -= 1
            else:
                r += 1
        return False
```

**Complexity.** Time O(m + n), space O(1).

**Watch out.** Unlike #74, rows don't continue each other, so flattening + one binary search doesn't work.

```test
m = [[1,4,7,11,15],[2,5,8,12,19],[3,6,9,16,22],[10,13,14,17,24],[18,21,23,26,30]]
assert Solution().searchMatrix(m, 5) is True
assert Solution().searchMatrix(m, 20) is False
```

### 24. Swap Nodes in Pairs
difficulty: Medium

**Problem.** Swap every two adjacent nodes (swap nodes, not values).

**Example.** `[1,2,3,4]` → `[2,1,4,3]`.

**Idea.** With `prev` before a pair `(a, b)`: relink `prev → b → a → rest`, then move `prev` to `a`.

**Steps.**
1. Put a `dummy` node before the head; `prev = dummy`.
2. While two nodes `a` and `b` follow `prev`: set `a.next = b.next`, `b.next = a`, `prev.next = b`.
3. Now the pair is `b → a`; move `prev = a` to stand before the next pair.
4. Return `dummy.next`.

```python
class Solution:
    def swapPairs(self, head: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode(0, head)
        prev = dummy
        while prev.next and prev.next.next:
            a, b = prev.next, prev.next.next
            a.next = b.next
            b.next = a
            prev.next = b
            prev = a
        return dummy.next
```

**Complexity.** Time O(n), space O(1).

**Watch out.** Set `a.next = b.next` **first**, before `b.next` is overwritten.

```test
assert to_list(Solution().swapPairs(build_list([1,2,3,4]))) == [2,1,4,3]
assert to_list(Solution().swapPairs(build_list([1,2,3]))) == [2,1,3]
assert to_list(Solution().swapPairs(None)) == []
```

### 142. Linked List Cycle II
difficulty: Medium

**Problem.** Return the node where the cycle begins, or `None`. O(1) memory.

**Idea.** Floyd: after `slow` and `fast` meet, the distance from the head to the cycle start equals the distance from the meeting point to the cycle start (going forward). So reset one pointer to the head and move both one step at a time; they meet at the cycle start.

**Steps.**
1. Move `slow` one step and `fast` two steps until they meet (no meeting → `None`).
2. Start a pointer `p` at the head.
3. Move `p` and `slow` one step at a time.
4. They meet at the start of the cycle: return that node.

```python
class Solution:
    def detectCycle(self, head: Optional[ListNode]) -> Optional[ListNode]:
        slow = fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
            if slow is fast:
                p = head
                while p is not slow:
                    p = p.next
                    slow = slow.next
                return p
        return None
```

**Complexity.** Time O(n), space O(1).

**Watch out.** Why it works: if the head-to-start distance is `a` and the start-to-meeting distance is `b` in a cycle of length `c`, then `2(a + b) = a + b + k·c`, so `a = k·c - b`, which is exactly the remaining distance from the meeting point to the start.

```test
h = build_list([3,2,0,-4]); h.next.next.next.next = h.next
assert Solution().detectCycle(h) is h.next
assert Solution().detectCycle(build_list([1])) is None
```

### 160. Intersection of Two Linked Lists
difficulty: Easy

**Problem.** Return the node where two singly linked lists merge, or `None`.

**Idea.** Two pointers walk `A then B` and `B then A`. Both travel `lenA + lenB` steps in total, so they reach the intersection at the same moment (or both reach `None` together).

**Steps.**
1. Start `a` at `headA` and `b` at `headB`.
2. Move both one step at a time.
3. When `a` reaches the end, send it to `headB`; when `b` reaches the end, send it to `headA`.
4. Both walk the same total distance, so they meet at the intersection, or both become `None` if there isn't one.

```python
class Solution:
    def getIntersectionNode(self, headA: ListNode, headB: ListNode) -> Optional[ListNode]:
        a, b = headA, headB
        while a is not b:
            a = a.next if a else headB
            b = b.next if b else headA
        return a
```

**Complexity.** Time O(m + n), space O(1).

**Watch out.** Compare nodes with `is`, not values: two lists can have equal values without sharing nodes.

```test
common = build_list([8,4,5]); A = build_list([4,1]); A.next.next = common; B = build_list([5,6,1]); B.next.next.next = common
assert Solution().getIntersectionNode(A, B) is common
assert Solution().getIntersectionNode(build_list([1]), build_list([2])) is None
```

### 206. Reverse Linked List
difficulty: Easy

**Problem.** Reverse a singly linked list.

**Idea.** Walk the list and point each node back at the previous one.

**Steps.**
1. Start `prev = None`, `cur = head`.
2. Save `nxt = cur.next` before changing anything.
3. Point `cur.next` back to `prev`.
4. Move forward: `prev = cur`, `cur = nxt`.
5. When `cur` is `None`, `prev` is the new head.

```python
class Solution:
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        prev = None
        cur = head
        while cur:
            nxt = cur.next
            cur.next = prev
            prev = cur
            cur = nxt
        return prev
```

**Complexity.** Time O(n), space O(1).

**Watch out.** Recursive version: `new_head = reverse(head.next); head.next.next = head; head.next = None; return new_head` (O(n) stack).

```test
assert to_list(Solution().reverseList(build_list([1,2,3,4,5]))) == [5,4,3,2,1]
assert to_list(Solution().reverseList(None)) == []
```

### 234. Palindrome Linked List
difficulty: Easy

**Problem.** Is the linked list a palindrome? Follow-up: O(n) time, O(1) space.

**Idea.** Find the middle (slow/fast), reverse the second half, compare the two halves node by node.

**Steps.**
1. Find the middle with `slow` (1 step) and `fast` (2 steps).
2. Reverse the second half, starting at `slow`.
3. Compare the first half (from `head`) with the reversed second half, node by node.
4. Any difference → `False`; if the second half runs out with no difference → `True`.

```python
class Solution:
    def isPalindrome(self, head: Optional[ListNode]) -> bool:
        slow = fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
        prev = None
        while slow:
            nxt = slow.next
            slow.next = prev
            prev = slow
            slow = nxt
        left, right = head, prev
        while right:
            if left.val != right.val:
                return False
            left = left.next
            right = right.next
        return True
```

**Complexity.** Time O(n), space O(1).

**Watch out.** This modifies the list; reverse the second half again if the caller needs the original. Simple O(n)-space version: copy values into a list and compare with its reverse.

```test
assert Solution().isPalindrome(build_list([1,2,2,1])) is True
assert Solution().isPalindrome(build_list([1,2])) is False
assert Solution().isPalindrome(build_list([1,2,3,2,1])) is True
```

### 94. Binary Tree Inorder Traversal
difficulty: Easy

**Problem.** Return the inorder traversal (left, node, right). Follow-up: iteratively.

**Idea.** Iterative: go left as far as possible pushing nodes, pop one, record it, then go to its right child.

**Steps.**
1. Go left from the current node as far as possible, pushing each node on a stack.
2. Pop a node and record its value.
3. Move to its right child and repeat.
4. Stop when there's no current node and the stack is empty.

```python
class Solution:
    def inorderTraversal(self, root: Optional[TreeNode]) -> List[int]:
        res, stack = [], []
        node = root
        while stack or node:
            while node:
                stack.append(node)
                node = node.left
            node = stack.pop()
            res.append(node.val)
            node = node.right
        return res
```

**Complexity.** Time O(n), space O(h).

**Watch out.** Recursive version is three lines: `inorder(left); res.append(val); inorder(right)`. This stack template is reused in Kth Smallest in a BST and BST Iterator.

```test
assert Solution().inorderTraversal(build_tree([1,None,2,3])) == [1,3,2]
assert Solution().inorderTraversal(None) == []
```

### 543. Diameter of Binary Tree
difficulty: Easy

**Problem.** Return the length (in edges) of the longest path between any two nodes.

**Idea.** For each node, the longest path through it = left height + right height. Compute heights with DFS and update a global maximum on the way.

**Steps.**
1. `height(node)`: `None` → 0.
2. Get the left and right heights recursively.
3. The longest path through this node has `l + r` edges: update `best`.
4. Return `1 + max(l, r)` to the parent. After the walk, return `best`.

```python
class Solution:
    def diameterOfBinaryTree(self, root: Optional[TreeNode]) -> int:
        best = 0

        def height(node):
            nonlocal best
            if not node:
                return 0
            l = height(node.left)
            r = height(node.right)
            best = max(best, l + r)
            return 1 + max(l, r)

        height(root)
        return best
```

**Complexity.** Time O(n), space O(h).

**Watch out.** The longest path doesn't have to pass through the root. Same pattern as Binary Tree Maximum Path Sum.

```test
assert Solution().diameterOfBinaryTree(build_tree([1,2,3,4,5])) == 3
assert Solution().diameterOfBinaryTree(build_tree([1,2])) == 1
```

### 437. Path Sum III
difficulty: Medium

**Problem.** Count downward paths (not necessarily from the root or to a leaf) whose values sum to `targetSum`.

**Idea.** Prefix sums along the current root-to-node path (like #560 on a tree). At each node, the number of paths ending here = how many earlier prefixes equal `current - target`. Remove the current prefix when backtracking.

**Steps.**
1. `prefix` counts the running sums seen on the path from the root; start with `prefix[0] = 1`.
2. At each node, add its value to the running sum `cur`.
3. Paths ending here that sum to the target = `prefix[cur - targetSum]`.
4. Add `cur` to `prefix`, recurse into both children, then remove it again when going back up.
5. Return the total count.

```python
class Solution:
    def pathSum(self, root: Optional[TreeNode], targetSum: int) -> int:
        prefix = defaultdict(int)
        prefix[0] = 1

        def dfs(node, cur):
            if not node:
                return 0
            cur += node.val
            count = prefix[cur - targetSum]
            prefix[cur] += 1
            count += dfs(node.left, cur) + dfs(node.right, cur)
            prefix[cur] -= 1          # backtrack: leave this path
            return count

        return dfs(root, 0)
```

**Complexity.** Time O(n), space O(h).

**Watch out.** Without the backtracking `-= 1`, prefixes from a different branch would be counted.

```test
assert Solution().pathSum(build_tree([10,5,-3,3,2,None,11,3,-2,None,1]), 8) == 3
assert Solution().pathSum(build_tree([5,4,8,11,None,13,4,7,2,None,None,5,1]), 22) == 3
```

### 994. Rotting Oranges
difficulty: Medium

**Problem.** Grid: 0 empty, 1 fresh, 2 rotten. Each minute, rotten oranges rot their 4 neighbours. Minutes until no fresh orange remains, or -1.

**Idea: multi-source BFS.** Start the queue with **all** rotten oranges at once; each BFS level is one minute.

**Steps.**
1. Queue every rotten orange and count the fresh ones.
2. Each round of BFS is one minute: pop all oranges currently in the queue.
3. Every fresh neighbour (up, down, left, right) becomes rotten, the fresh count drops, and it joins the queue.
4. Stop when the queue or the fresh count is empty.
5. If fresh oranges remain, return `-1`; otherwise the number of minutes.

```python
class Solution:
    def orangesRotting(self, grid: List[List[int]]) -> int:
        m, n = len(grid), len(grid[0])
        q = deque()
        fresh = 0
        for r in range(m):
            for c in range(n):
                if grid[r][c] == 2:
                    q.append((r, c))
                elif grid[r][c] == 1:
                    fresh += 1
        minutes = 0
        while q and fresh:
            for _ in range(len(q)):
                r, c = q.popleft()
                for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                    if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] == 1:
                        grid[nr][nc] = 2
                        fresh -= 1
                        q.append((nr, nc))
            minutes += 1
        return minutes if fresh == 0 else -1
```

**Complexity.** Time O(m·n), space O(m·n).

**Watch out.** The loop condition `while q and fresh` avoids counting an extra minute after the last orange rots.

```test
assert Solution().orangesRotting([[2,1,1],[1,1,0],[0,1,1]]) == 4
assert Solution().orangesRotting([[2,1,1],[0,1,1],[1,0,1]]) == -1
assert Solution().orangesRotting([[0,2]]) == 0
```

### 78. Subsets
difficulty: Medium

**Problem.** Return all subsets (the power set) of distinct integers.

**Idea.** Backtracking where **every node** of the recursion is a subset: record the path on entry, then extend it with each later element.

**Steps.**
1. `backtrack(start)`: record a copy of `path`. Every path is a subset, including the empty one.
2. For each index `i` from `start`, add `nums[i]` and recurse with `i + 1`.
3. Remove it after returning.
4. Starting each loop at `start` means each subset is built only once.

```python
class Solution:
    def subsets(self, nums: List[int]) -> List[List[int]]:
        res, path = [], []

        def backtrack(start):
            res.append(path[:])
            for i in range(start, len(nums)):
                path.append(nums[i])
                backtrack(i + 1)
                path.pop()

        backtrack(0)
        return res
```

**Complexity.** O(n · 2ⁿ).

**Watch out.** Iterative version: start with `[[]]`, and for each number add it to every existing subset: `res += [s + [x] for s in res]`.

```test
assert sorted(Solution().subsets([1,2,3])) == sorted([[],[1],[2],[1,2],[3],[1,3],[2,3],[1,2,3]])
assert Solution().subsets([0]) == [[],[0]]
```

### 131. Palindrome Partitioning
difficulty: Medium

**Problem.** Split `s` into pieces that are all palindromes; return every possible split.

**Example.** `"aab"` → `[["a","a","b"],["aa","b"]]`.

**Idea.** Backtracking over the cut position: from `start`, try every end `end`; if `s[start:end]` is a palindrome, take it and continue from `end`.

**Steps.**
1. `backtrack(start)`: if `start == len(s)`, the cut pieces cover the string: save them.
2. Try every end `end` from `start + 1` to `len(s)`.
3. If `s[start:end]` is a palindrome, add it and recurse from `end`.
4. Remove it after returning and try the next end.

```python
class Solution:
    def partition(self, s: str) -> List[List[str]]:
        res, path = [], []

        def backtrack(start):
            if start == len(s):
                res.append(path[:])
                return
            for end in range(start + 1, len(s) + 1):
                piece = s[start:end]
                if piece == piece[::-1]:
                    path.append(piece)
                    backtrack(end)
                    path.pop()

        backtrack(0)
        return res
```

**Complexity.** O(n · 2ⁿ) worst case.

**Watch out.** Precomputing a palindrome table `pal[i][j]` avoids recomputing the reversed strings for long inputs.

```test
assert Solution().partition("aab") == [["a","a","b"],["aa","b"]]
assert Solution().partition("a") == [["a"]]
```

### 51. N-Queens
difficulty: Hard

**Problem.** Return every board placing `n` non-attacking queens (`'Q'` and `'.'` strings).

**Idea.** Same as N-Queens II (#52): one queen per row, sets for columns, `r - c` diagonals and `r + c` anti-diagonals. Record the column chosen in each row and build the strings at the end.

**Steps.**
1. Place one queen per row, starting at row 0.
2. In row `r`, skip a column if `c`, `r - c` or `r + c` is already used.
3. Otherwise mark the three sets, save the column in `queens`, recurse into row `r + 1`, then undo.
4. When `r == n`, build the board: for each row, `'.' * c + 'Q' + '.' * (n - c - 1)`.

```python
class Solution:
    def solveNQueens(self, n: int) -> List[List[str]]:
        res = []
        queens = []                       # queens[r] = column of the queen in row r
        cols, diag, anti = set(), set(), set()

        def place(r):
            if r == n:
                res.append(['.' * c + 'Q' + '.' * (n - c - 1) for c in queens])
                return
            for c in range(n):
                if c in cols or r - c in diag or r + c in anti:
                    continue
                cols.add(c); diag.add(r - c); anti.add(r + c); queens.append(c)
                place(r + 1)
                cols.remove(c); diag.remove(r - c); anti.remove(r + c); queens.pop()

        place(0)
        return res
```

**Complexity.** O(n!) roughly.

**Watch out.** Build the row strings only when a full solution is found.

```test
assert Solution().solveNQueens(4) == [[".Q..","...Q","Q...","..Q."],["..Q.","Q...","...Q",".Q.."]]
assert Solution().solveNQueens(1) == [["Q"]]
```

### 84. Largest Rectangle in Histogram
difficulty: Hard

**Problem.** Bars of width 1; return the area of the largest rectangle inside the histogram.

**Example.** `[2,1,5,6,2,3]` → `10` (bars 5 and 6, height 5, width 2).

**Idea: monotonic stack.** Keep bar indexes with increasing heights. When a shorter bar arrives, every taller bar on the stack can't extend further right: pop it and compute its rectangle. Its width runs from the new top of the stack + 1 to the current index − 1.

**Steps.**
1. Append a 0-height sentinel to flush the stack at the end.
2. For each `i`: while the top bar is taller than `h[i]`, pop it with height `H`; width = `i` if the stack is empty, else `i - stack[-1] - 1`; update the best.
3. Push `i`.

```python
class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        stack = []
        best = 0
        for i, h in enumerate(heights + [0]):
            while stack and heights[stack[-1]] > h:
                H = heights[stack.pop()]
                width = i if not stack else i - stack[-1] - 1
                best = max(best, H * width)
            stack.append(i)
        return best
```

**Complexity.** Time O(n), space O(n).

**Watch out.** The sentinel `0` at the end makes sure every bar gets popped and measured.

```test
assert Solution().largestRectangleArea([2,1,5,6,2,3]) == 10
assert Solution().largestRectangleArea([2,4]) == 4
assert Solution().largestRectangleArea([1,1,1,1]) == 4
```

### 394. Decode String
difficulty: Medium

**Problem.** Decode strings like `"3[a2[c]]"` → `"accaccacc"` (`k[...]` repeats the inside `k` times).

**Idea.** A stack of `(previous string, repeat count)`. On `[`, save the current state and start fresh; on `]`, pop and build `previous + current * count`.

**Steps.**
1. Keep `cur` (the string being built) and `num` (the repeat count being read).
2. A digit: `num = num * 10 + digit` (counts can have several digits).
3. `[`: push `(cur, num)` on the stack, then reset both.
4. `]`: pop `(prev, k)` and set `cur = prev + cur * k`.
5. A letter: add it to `cur`. Return `cur` at the end.

```python
class Solution:
    def decodeString(self, s: str) -> str:
        stack = []
        cur, num = '', 0
        for ch in s:
            if ch.isdigit():
                num = num * 10 + int(ch)
            elif ch == '[':
                stack.append((cur, num))
                cur, num = '', 0
            elif ch == ']':
                prev, k = stack.pop()
                cur = prev + cur * k
            else:
                cur += ch
        return cur
```

**Complexity.** Time O(output length), space O(output length).

**Watch out.** `num = num * 10 + int(ch)` handles counts like `10[a]`.

```test
assert Solution().decodeString("3[a]2[bc]") == "aaabcbc"
assert Solution().decodeString("3[a2[c]]") == "accaccacc"
assert Solution().decodeString("2[abc]3[cd]ef") == "abcabccdcdcdef"
assert Solution().decodeString("10[a]") == "a" * 10
```

### 739. Daily Temperatures
difficulty: Medium

**Problem.** For each day, how many days until a warmer temperature (0 if never)?

**Example.** `[73,74,75,71,69,72,76,73]` → `[1,1,4,2,1,1,0,0]`.

**Idea: monotonic stack** of days still waiting for a warmer day (temperatures decreasing). A warmer day resolves every colder day on top of the stack.

**Steps.**
1. The stack holds the indexes of days still waiting for a warmer day.
2. For each day `i` with temperature `t`, pop every waiting day `j` that is colder than `t`.
3. For each popped `j`, the answer is `i - j` days.
4. Push `i`. Days left on the stack never get warmer and keep 0.

```python
class Solution:
    def dailyTemperatures(self, temperatures: List[int]) -> List[int]:
        res = [0] * len(temperatures)
        stack = []
        for i, t in enumerate(temperatures):
            while stack and temperatures[stack[-1]] < t:
                j = stack.pop()
                res[j] = i - j
            stack.append(i)
        return res
```

**Complexity.** Time O(n), space O(n).

**Watch out.** Use strict `<`: an equal temperature isn't warmer. Days left on the stack keep the default 0.

```test
assert Solution().dailyTemperatures([73,74,75,71,69,72,76,73]) == [1,1,4,2,1,1,0,0]
assert Solution().dailyTemperatures([30,40,50,60]) == [1,1,1,0]
assert Solution().dailyTemperatures([30,60,90]) == [1,1,0]
```

### 347. Top K Frequent Elements
difficulty: Medium

**Problem.** Return the `k` most frequent elements (better than O(n log n)).

**Idea: bucket sort.** A frequency is between 1 and n. Put each number into `buckets[frequency]`, then read buckets from the highest frequency down until you have `k` numbers.

**Steps.**
1. Count each number with `Counter`.
2. Make buckets: `buckets[f]` lists the numbers that appear `f` times (`f` is at most `len(nums)`).
3. Walk the buckets from the highest frequency down, collecting numbers.
4. Stop once you have `k` numbers. O(n), no sorting.

```python
class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        count = Counter(nums)
        buckets = [[] for _ in range(len(nums) + 1)]
        for num, freq in count.items():
            buckets[freq].append(num)
        res = []
        for freq in range(len(buckets) - 1, 0, -1):
            for num in buckets[freq]:
                res.append(num)
                if len(res) == k:
                    return res
        return res
```

**Complexity.** Time O(n), space O(n).

**Watch out.** Heap alternative: `heapq.nlargest(k, count, key=count.get)` (O(n log k)). `Counter(nums).most_common(k)` also works.

```test
assert sorted(Solution().topKFrequent([1,1,1,2,2,3], 2)) == [1,2]
assert Solution().topKFrequent([1], 1) == [1]
```

### 763. Partition Labels
difficulty: Medium

**Problem.** Split the string into as many parts as possible so each letter appears in at most one part. Return the part sizes.

**Example.** `"ababcbacadefegdehijhklij"` → `[9,7,8]`.

**Idea.** Record the last index of each letter. Walk the string extending the current part's `end` to the last occurrence of every letter seen; when `i == end`, the part can close.

**Steps.**
1. Record the last index of every letter.
2. Walk the string; for each letter, extend `end` to its last index.
3. When `i == end`, every letter in the current part ends here: close the part and record its length.
4. Start the next part at `i + 1`.

```python
class Solution:
    def partitionLabels(self, s: str) -> List[int]:
        last = {ch: i for i, ch in enumerate(s)}
        res = []
        start = end = 0
        for i, ch in enumerate(s):
            end = max(end, last[ch])
            if i == end:
                res.append(end - start + 1)
                start = i + 1
        return res
```

**Complexity.** Time O(n), space O(1) (26 letters).

**Watch out.** The dictionary comprehension keeps the **last** index because later assignments overwrite earlier ones.

```test
assert Solution().partitionLabels("ababcbacadefegdehijhklij") == [9,7,8]
assert Solution().partitionLabels("eccbbbbdec") == [10]
```

### 118. Pascal's Triangle
difficulty: Easy

**Problem.** Return the first `numRows` rows of Pascal's triangle.

**Idea.** Each row starts and ends with 1; every inner value is the sum of the two values above it.

**Steps.**
1. Start with `[[1]]`.
2. For each new row, take the previous row `prev`.
3. The inside values are `prev[i] + prev[i + 1]` for each neighbouring pair.
4. Add a `1` at both ends and append the row.

```python
class Solution:
    def generate(self, numRows: int) -> List[List[int]]:
        res = [[1]]
        for _ in range(numRows - 1):
            prev = res[-1]
            res.append([1] + [prev[i] + prev[i + 1] for i in range(len(prev) - 1)] + [1])
        return res
```

**Complexity.** O(numRows²).

**Watch out.** `numRows = 1` returns `[[1]]` because the loop runs zero times.

```test
assert Solution().generate(5) == [[1],[1,1],[1,2,1],[1,3,3,1],[1,4,6,4,1]]
assert Solution().generate(1) == [[1]]
```

### 279. Perfect Squares
difficulty: Medium

**Problem.** Fewest perfect squares (1, 4, 9, ...) that sum to `n`.

**Example.** `12` → `3` (4 + 4 + 4); `13` → `2` (4 + 9).

**Idea.** Like Coin Change where the coins are the squares ≤ n: `dp[i] = 1 + min(dp[i - s])` over squares `s ≤ i`.

**Steps.**
1. List the squares `1, 4, 9, ...` up to `n`.
2. `dp[i]` = fewest squares that add up to `i`; `dp[0] = 0`.
3. For each `i`, try every square `s <= i` as the last one: `dp[i] = min(dp[i], dp[i - s] + 1)`.
4. Return `dp[n]`.

```python
class Solution:
    def numSquares(self, n: int) -> int:
        squares = [i * i for i in range(1, int(n ** 0.5) + 1)]
        dp = [0] + [n] * n
        for i in range(1, n + 1):
            for s in squares:
                if s > i:
                    break
                dp[i] = min(dp[i], dp[i - s] + 1)
        return dp[n]
```

**Complexity.** Time O(n√n), space O(n).

**Watch out.** Math shortcut (Lagrange's four-square theorem): the answer is always 1–4, and it's 4 exactly when `n` has the form `4^a (8b + 7)`.

```test
assert Solution().numSquares(12) == 3
assert Solution().numSquares(13) == 2
assert Solution().numSquares(1) == 1
```

### 152. Maximum Product Subarray
difficulty: Medium

**Problem.** Largest product of a contiguous subarray.

**Example.** `[2,3,-2,4]` → `6`; `[-2,0,-1]` → `0`.

**Idea.** Like Kadane, but a negative number turns the smallest product into the largest. Track both the **max** and the **min** product ending at each position.

**Steps.**
1. Start `cur_max`, `cur_min` and `best` at `nums[0]`.
2. For each next `x`, the candidates are `x`, `cur_max * x` and `cur_min * x` (a negative min times a negative `x` can become the max).
3. `cur_max` = the largest candidate, `cur_min` = the smallest.
4. Update `best` with `cur_max`. Return `best`.

```python
class Solution:
    def maxProduct(self, nums: List[int]) -> int:
        cur_max = cur_min = best = nums[0]
        for x in nums[1:]:
            candidates = (x, cur_max * x, cur_min * x)
            cur_max = max(candidates)
            cur_min = min(candidates)
            best = max(best, cur_max)
        return best
```

**Complexity.** Time O(n), space O(1).

**Watch out.** Compute both new values from the **old** max and min (that's why the candidates tuple is built first).

```test
assert Solution().maxProduct([2,3,-2,4]) == 6
assert Solution().maxProduct([-2,0,-1]) == 0
assert Solution().maxProduct([-2,3,-4]) == 24
```

### 416. Partition Equal Subset Sum
difficulty: Medium

**Problem.** Can the array be split into two subsets with equal sums?

**Idea.** The total must be even, and you need a subset summing to `total / 2`. 0/1 knapsack: `dp[s]` = "some subset sums to `s`". For each number, update sums from **high to low** so each number is used once.

**Steps.**
1. If the total is odd, it can't be split equally → `False`.
2. Target = `total // 2`. `dp[s]` = can some numbers add up to `s`; `dp[0] = True`.
3. For each number `x`, go through `s` from `target` down to `x`: if `dp[s - x]`, set `dp[s] = True`.
4. Going downward makes sure each number is used at most once.
5. Return `dp[target]`.

```python
class Solution:
    def canPartition(self, nums: List[int]) -> bool:
        total = sum(nums)
        if total % 2:
            return False
        target = total // 2
        dp = [True] + [False] * target
        for x in nums:
            for s in range(target, x - 1, -1):
                if dp[s - x]:
                    dp[s] = True
        return dp[target]
```

**Complexity.** Time O(n · target), space O(target).

**Watch out.** Looping `s` upward would let the same number be used several times (that's the unbounded version). Bitset trick: `bits |= bits << x`, then check bit `target`.

```test
assert Solution().canPartition([1,5,11,5]) is True
assert Solution().canPartition([1,2,3,5]) is False
assert Solution().canPartition([2,2]) is True
```

### 32. Longest Valid Parentheses
difficulty: Hard

**Problem.** Length of the longest well-formed parentheses substring.

**Example.** `")()())"` → `4`.

**Idea.** A stack of indexes, starting with `-1` as the base. Push the index of each `(`. On `)`, pop; if the stack becomes empty, this `)` is unmatched, so push its index as the new base. Otherwise the valid length is `i - stack[-1]`.

**Steps.**
1. Start the stack with `-1`: the index just before the current valid run.
2. `(` → push its index.
3. `)` → pop. If the stack is now empty, this `)` has no match: push its index as the new base.
4. Otherwise the valid run ending here has length `i - stack[-1]`; update `best`.

```python
class Solution:
    def longestValidParentheses(self, s: str) -> int:
        stack = [-1]
        best = 0
        for i, ch in enumerate(s):
            if ch == '(':
                stack.append(i)
            else:
                stack.pop()
                if not stack:
                    stack.append(i)
                else:
                    best = max(best, i - stack[-1])
        return best
```

**Complexity.** Time O(n), space O(n).

**Watch out.** O(1)-space alternative: scan left-to-right and right-to-left counting `(` and `)`; whenever counts are equal, record `2 * count`, and reset when they become invalid.

```test
assert Solution().longestValidParentheses("(()") == 2
assert Solution().longestValidParentheses(")()())") == 4
assert Solution().longestValidParentheses("") == 0
assert Solution().longestValidParentheses("()(())") == 6
```

### 62. Unique Paths
difficulty: Medium

**Problem.** Count right/down paths from the top-left to the bottom-right of an `m × n` grid.

**Idea.** `dp[c]` = ways to reach the current cell = from above (old `dp[c]`) + from the left (`dp[c - 1]`).

**Steps.**
1. `dp[c]` = ways to reach column `c` of the current row. The first row is all 1s (only right moves).
2. For each next row, for `c` from 1: `dp[c] += dp[c - 1]` (old `dp[c]` = from above, `dp[c - 1]` = from the left).
3. Column 0 stays 1 (only down moves).
4. Return `dp[-1]`.

```python
class Solution:
    def uniquePaths(self, m: int, n: int) -> int:
        dp = [1] * n
        for _ in range(m - 1):
            for c in range(1, n):
                dp[c] += dp[c - 1]
        return dp[-1]
```

**Complexity.** Time O(m·n), space O(n).

**Watch out.** Math formula: you make `m - 1` downs and `n - 1` rights in some order, so the answer is `math.comb(m + n - 2, m - 1)`.

```test
assert Solution().uniquePaths(3, 7) == 28
assert Solution().uniquePaths(3, 2) == 3
assert Solution().uniquePaths(1, 1) == 1
```

### 1143. Longest Common Subsequence
difficulty: Medium

**Problem.** Length of the longest subsequence common to both strings.

**Example.** `"abcde", "ace"` → `3`.

**Idea.** `dp[i][j]` = LCS of `text1[:i]` and `text2[:j]`. Equal last characters → `dp[i-1][j-1] + 1`; otherwise `max(dp[i-1][j], dp[i][j-1])`.

**Steps.**
1. Table `dp` of size `(m + 1) × (n + 1)` filled with 0; row 0 and column 0 mean an empty string.
2. If `text1[i-1] == text2[j-1]`, that character extends the LCS: `dp[i][j] = dp[i-1][j-1] + 1`.
3. Otherwise drop one character from either string: `max(dp[i-1][j], dp[i][j-1])`.
4. Return `dp[m][n]`.

```python
class Solution:
    def longestCommonSubsequence(self, text1: str, text2: str) -> int:
        m, n = len(text1), len(text2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if text1[i - 1] == text2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
        return dp[m][n]
```

**Complexity.** Time O(m·n), space O(m·n) (reducible to two rows).

**Watch out.** Same table shape as Edit Distance; this pattern solves many two-string DP problems.

```test
assert Solution().longestCommonSubsequence("abcde", "ace") == 3
assert Solution().longestCommonSubsequence("abc", "abc") == 3
assert Solution().longestCommonSubsequence("abc", "def") == 0
```

### 31. Next Permutation
difficulty: Medium

**Problem.** Rearrange `nums` in place into the next lexicographically greater permutation (or the smallest one if it's the last).

**Example.** `[1,2,3]` → `[1,3,2]`; `[3,2,1]` → `[1,2,3]`.

**Idea.** To get the next bigger arrangement, change the digits as far to the right as possible. The longest decreasing suffix is already at its maximum, so the element just before it (the pivot) must grow by the smallest possible amount: swap it with the smallest bigger value in the suffix. The suffix is still decreasing, so reversing it makes it as small as possible.

**Steps.**
1. From the right, find the first index `i` with `nums[i] < nums[i + 1]` (the pivot). Everything after it is decreasing.
2. If there is a pivot, find from the right the first `nums[j] > nums[i]` and swap them.
3. Reverse the part after `i` so it becomes increasing (the smallest arrangement).
4. With no pivot (the whole array decreases), `i = -1` and the whole array is reversed to the first permutation.

```python
class Solution:
    def nextPermutation(self, nums: List[int]) -> None:
        i = len(nums) - 2
        while i >= 0 and nums[i] >= nums[i + 1]:
            i -= 1
        if i >= 0:
            j = len(nums) - 1
            while nums[j] <= nums[i]:
                j -= 1
            nums[i], nums[j] = nums[j], nums[i]
        l, r = i + 1, len(nums) - 1
        while l < r:
            nums[l], nums[r] = nums[r], nums[l]
            l += 1
            r -= 1
```

**Complexity.** Time O(n), space O(1).

**Watch out.** If no pivot exists (`i == -1`), the whole array is reversed, giving the smallest permutation.

```test
a = [1,2,3]; Solution().nextPermutation(a); assert a == [1,3,2]
a = [3,2,1]; Solution().nextPermutation(a); assert a == [1,2,3]
a = [1,1,5]; Solution().nextPermutation(a); assert a == [1,5,1]
a = [1,3,2]; Solution().nextPermutation(a); assert a == [2,1,3]
```

### 75. Sort Colors
difficulty: Medium

**Problem.** Sort an array of 0s, 1s and 2s in place in one pass (no library sort).

**Idea: Dutch national flag.** Three regions: `[0, low)` zeros, `[low, mid)` ones, `(high, end]` twos. Look at `nums[mid]`: 0 → swap to `low`; 1 → leave; 2 → swap to `high` (don't advance `mid`, the swapped-in value is unchecked).

**Steps.**
1. Three pointers: `low` (next place for a 0), `mid` (current), `high` (next place for a 2).
2. `nums[mid] == 0`: swap it to `low`; move `low` and `mid` forward.
3. `nums[mid] == 1`: it's in the right region; move `mid` forward.
4. `nums[mid] == 2`: swap it to `high` and move `high` back. Don't move `mid`: the swapped-in value still needs checking.
5. Stop when `mid > high`.

```python
class Solution:
    def sortColors(self, nums: List[int]) -> None:
        low, mid, high = 0, 0, len(nums) - 1
        while mid <= high:
            if nums[mid] == 0:
                nums[low], nums[mid] = nums[mid], nums[low]
                low += 1
                mid += 1
            elif nums[mid] == 1:
                mid += 1
            else:
                nums[mid], nums[high] = nums[high], nums[mid]
                high -= 1
```

**Complexity.** Time O(n), space O(1).

**Watch out.** After swapping a 2 to the back, keep `mid` where it is.

```test
a = [2,0,2,1,1,0]; Solution().sortColors(a); assert a == [0,0,1,1,2,2]
a = [2,0,1]; Solution().sortColors(a); assert a == [0,1,2]
```

### 287. Find the Duplicate Number
difficulty: Medium

**Problem.** `n + 1` numbers in `1..n` with exactly one repeated value (maybe several times). Find it without modifying the array and with O(1) space.

**Idea.** Treat `i → nums[i]` as a linked list. Because one value is pointed to twice, the "list" has a cycle, and the cycle's entrance is the duplicate. Use Floyd's algorithm (#142).

**Steps.**
1. Treat each index `i` as pointing to `nums[i]`. The duplicate value has two arrows into it, which makes a cycle.
2. Phase 1: move `slow = nums[slow]` and `fast = nums[nums[fast]]` until they meet.
3. Phase 2: reset `slow` to `nums[0]` and move both one step at a time.
4. Where they meet is the cycle entrance, which is the duplicate.

```python
class Solution:
    def findDuplicate(self, nums: List[int]) -> int:
        slow = fast = nums[0]
        while True:
            slow = nums[slow]
            fast = nums[nums[fast]]
            if slow == fast:
                break
        slow = nums[0]
        while slow != fast:
            slow = nums[slow]
            fast = nums[fast]
        return slow
```

**Complexity.** Time O(n), space O(1).

**Watch out.** Index 0 is never a target (values are 1..n), so starting there always leads into the cycle. Alternative: binary search on the value, counting how many numbers are `<= mid` (O(n log n)).

```test
assert Solution().findDuplicate([1,3,4,2,2]) == 2
assert Solution().findDuplicate([3,1,3,4,2]) == 3
assert Solution().findDuplicate([3,3,3,3,3]) == 3
```
