# Stack

### 20. Valid Parentheses
difficulty: Easy

**Problem.** A string of `()[]{}`: is every bracket closed by the same type, in the correct order?

**Example.** `"()[]{}"` → `true`; `"(]"` → `false`; `"([)]"` → `false`.

**Idea.** A stack holds the brackets still waiting to be closed. A closing bracket must match the **most recent** open one (the top of the stack).

**Steps.**
1. For each character: if it's an opening bracket, push it.
2. If it's a closing bracket: the stack must be non-empty and its top must be the matching opener; pop it.
3. At the end, the stack must be empty.

```python
class Solution:
    def isValid(self, s: str) -> bool:
        pairs = {')': '(', ']': '[', '}': '{'}
        stack = []
        for ch in s:
            if ch in pairs:
                if not stack or stack[-1] != pairs[ch]:
                    return False
                stack.pop()
            else:
                stack.append(ch)
        return not stack
```

**Complexity.** Time O(n), space O(n).

**Watch out.** `"(("` ends with a non-empty stack → false; `")"` hits an empty stack → false. Both must be handled.

```test
assert Solution().isValid("()[]{}") is True
assert Solution().isValid("(]") is False
assert Solution().isValid("([)]") is False
assert Solution().isValid("([])") is True
assert Solution().isValid("((") is False
```

### 71. Simplify Path
difficulty: Medium

**Problem.** Simplify a Unix absolute path: `.` = current dir, `..` = parent, multiple slashes = one slash. Return the canonical path (starts with `/`, no trailing slash).

**Example.** `"/home//foo/"` → `"/home/foo"`; `"/a/./b/../../c/"` → `"/c"`.

**Idea.** Split on `/` and use a stack of directory names: `..` pops (if possible), `.` and empty pieces are ignored, anything else is pushed (including names like `...`).

**Steps.**
1. Split the path on `/`. Repeated slashes give empty pieces.
2. For each piece: `..` → pop the last directory if the stack isn't empty.
3. Empty piece or `.` → ignore it.
4. Anything else (including `...`) is a directory name → push it.
5. Return `'/' + '/'.join(stack)`.

```python
class Solution:
    def simplifyPath(self, path: str) -> str:
        stack = []
        for part in path.split('/'):
            if part == '..':
                if stack:
                    stack.pop()
            elif part and part != '.':
                stack.append(part)
        return '/' + '/'.join(stack)
```

**Complexity.** Time O(n), space O(n).

**Watch out.** `..` at the root stays at the root (pop only if the stack isn't empty). `"..."` is a valid directory name.

```test
assert Solution().simplifyPath("/home/") == "/home"
assert Solution().simplifyPath("/home//foo/") == "/home/foo"
assert Solution().simplifyPath("/home/user/Documents/../Pictures") == "/home/user/Pictures"
assert Solution().simplifyPath("/../") == "/"
assert Solution().simplifyPath("/.../a/../b/c/../d/./") == "/.../b/d"
```

### 155. Min Stack
difficulty: Medium

**Problem.** Design a stack with `push`, `pop`, `top`, and `getMin`, all O(1).

**Idea.** Store, with every value, the **minimum of the stack at that moment**. Then the current min is always on top, and popping automatically restores the previous minimum.

**Steps.**
1. Each stack entry is a pair `(value, minimum of the stack including this value)`.
2. `push(val)`: the new minimum is `min(val, top's minimum)`, or `val` if the stack is empty; push the pair.
3. `pop()`: remove the top pair. The pair below already stores the previous minimum.
4. `top()` returns the first item of the top pair; `getMin()` returns the second. All O(1).

```python
class MinStack:
    def __init__(self):
        self.stack = []          # pairs: (value, min so far)

    def push(self, val: int) -> None:
        cur_min = min(val, self.stack[-1][1]) if self.stack else val
        self.stack.append((val, cur_min))

    def pop(self) -> None:
        self.stack.pop()

    def top(self) -> int:
        return self.stack[-1][0]

    def getMin(self) -> int:
        return self.stack[-1][1]
```

**Complexity.** O(1) per operation, O(n) space.

**Watch out.** A single `min` variable doesn't work: after popping the minimum you wouldn't know the previous one.

```test
s = MinStack(); s.push(-2); s.push(0); s.push(-3)
assert s.getMin() == -3; s.pop(); assert s.top() == 0 and s.getMin() == -2
```

### 150. Evaluate Reverse Polish Notation
difficulty: Medium

**Problem.** Evaluate an expression in Reverse Polish (postfix) notation with `+ - * /`. Division truncates toward zero.

**Example.** `["2","1","+","3","*"]` → `9` (`(2 + 1) * 3`).

**Idea.** Numbers go on a stack. An operator pops the top two (`b` first, then `a`), computes `a op b`, and pushes the result.

**Steps.**
1. Go through the tokens left to right with an empty stack.
2. A number → push it as an `int`.
3. An operator → pop `b` (the top), then pop `a`, and push `a op b`. The order matters for `-` and `/`.
4. For `/`, use `int(a / b)` to truncate toward zero (`//` would round `-7 / 2` down to `-4`).
5. At the end the stack holds one number: return it.

```python
class Solution:
    def evalRPN(self, tokens: List[str]) -> int:
        stack = []
        for t in tokens:
            if t in ('+', '-', '*', '/'):
                b = stack.pop()
                a = stack.pop()
                if t == '+':
                    stack.append(a + b)
                elif t == '-':
                    stack.append(a - b)
                elif t == '*':
                    stack.append(a * b)
                else:
                    stack.append(int(a / b))     # truncate toward zero
            else:
                stack.append(int(t))
        return stack[0]
```

**Complexity.** Time O(n), space O(n).

**Watch out.**
- Order matters for `-` and `/`: the **second** pop is the left operand.
- Python's `//` floors (`-7 // 2 = -4`); the problem needs truncation (`-3`), so use `int(a / b)`.

```test
assert Solution().evalRPN(["2","1","+","3","*"]) == 9
assert Solution().evalRPN(["4","13","5","/","+"]) == 6
assert Solution().evalRPN(["10","6","9","3","+","-11","*","/","*","17","+","5","+"]) == 22
```

### 224. Basic Calculator
difficulty: Hard

**Problem.** Evaluate an expression string with `+`, `-`, parentheses, spaces, and unary minus (no `eval`).

**Example.** `"(1+(4+5+2)-3)+(6+8)"` → `23`; `"-(2 + 3)"` → `-5`.

**Idea.** Keep a running `result` and the current `sign`. On `(`, push the current `result` and `sign` on a stack and start fresh inside. On `)`, finish the inside value and combine: `result = saved_result + saved_sign * inside`.

**Steps.**
1. `result = 0`, `sign = 1`, `num = 0`, `stack = []`.
2. Digit: build `num`. `+`/`-`: add `sign * num` to `result`, reset `num`, set `sign`.
3. `(`: push `result`, push `sign`; reset `result = 0`, `sign = 1`.
4. `)`: add the pending number; then `result = stack.pop() * result + stack.pop()` (sign first, then the previous result).
5. At the end, add the last `num`.

```python
class Solution:
    def calculate(self, s: str) -> int:
        result, sign, num = 0, 1, 0
        stack = []
        for ch in s:
            if ch.isdigit():
                num = num * 10 + int(ch)
            elif ch in '+-':
                result += sign * num
                num = 0
                sign = 1 if ch == '+' else -1
            elif ch == '(':
                stack.append(result)
                stack.append(sign)
                result, sign = 0, 1
            elif ch == ')':
                result += sign * num
                num = 0
                result *= stack.pop()        # sign before the parenthesis
                result += stack.pop()        # result before the parenthesis
        return result + sign * num
```

**Complexity.** Time O(n), space O(n) for nesting.

**Watch out.** A leading `-` works naturally (`result` is 0, so it acts like `0 - ...`). Spaces are simply skipped because no branch matches them.

```test
assert Solution().calculate("1 + 1") == 2
assert Solution().calculate(" 2-1 + 2 ") == 3
assert Solution().calculate("(1+(4+5+2)-3)+(6+8)") == 23
assert Solution().calculate("-(2 + 3)") == -5
assert Solution().calculate("1-(     -2)") == 3
```

# Linked List

### 141. Linked List Cycle
difficulty: Easy

**Problem.** Does the linked list contain a cycle? Follow-up: O(1) memory.

**Idea: Floyd's tortoise and hare.** `slow` moves 1 step, `fast` moves 2. In a cycle, `fast` catches up with `slow`; without one, `fast` hits the end.

**Steps.**
1. Start `slow` and `fast` at `head`.
2. Each round, move `slow` one step and `fast` two steps.
3. If they ever point to the same node, `fast` lapped `slow` inside a loop → `True`.
4. If `fast` reaches the end (`None`), there's no cycle → `False`.

```python
class Solution:
    def hasCycle(self, head: Optional[ListNode]) -> bool:
        slow = fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
            if slow is fast:
                return True
        return False
```

**Complexity.** Time O(n), space O(1).

**Watch out.** Compare with `is` (same node), not `==` on values. Simpler O(n)-space version: keep a set of visited nodes.

```test
h = build_list([3,2,0,-4]); h.next.next.next.next = h.next
assert Solution().hasCycle(h) is True
assert Solution().hasCycle(build_list([1])) is False
assert Solution().hasCycle(None) is False
```

### 2. Add Two Numbers
difficulty: Medium

**Problem.** Two numbers are stored as linked lists with digits in **reverse** order. Return their sum as a list in the same format.

**Example.** `[2,4,3] + [5,6,4]` → `[7,0,8]` (342 + 465 = 807).

**Idea.** Add digit by digit with a carry, exactly like on paper. The digits are already lowest-first, which is the order addition needs.

**Steps.**
1. Dummy head, `carry = 0`.
2. While either list has nodes or `carry` is non-zero: add the available digits and carry; append `total % 10`; `carry = total // 10`.

```python
class Solution:
    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
        dummy = tail = ListNode()
        carry = 0
        while l1 or l2 or carry:
            total = carry
            if l1:
                total += l1.val
                l1 = l1.next
            if l2:
                total += l2.val
                l2 = l2.next
            carry, digit = divmod(total, 10)
            tail.next = ListNode(digit)
            tail = tail.next
        return dummy.next
```

**Complexity.** Time O(max(m, n)), space O(max(m, n)) for the result.

**Watch out.** `or carry` in the loop condition adds the final carry digit (`[9,9] + [1]` → `[0,0,1]`).

```test
assert to_list(Solution().addTwoNumbers(build_list([2,4,3]), build_list([5,6,4]))) == [7,0,8]
assert to_list(Solution().addTwoNumbers(build_list([0]), build_list([0]))) == [0]
assert to_list(Solution().addTwoNumbers(build_list([9,9,9,9,9,9,9]), build_list([9,9,9,9]))) == [8,9,9,9,0,0,0,1]
```

### 21. Merge Two Sorted Lists
difficulty: Easy

**Problem.** Merge two sorted linked lists into one sorted list by splicing their nodes.

**Idea.** A dummy node plus a `tail` pointer. Repeatedly attach the smaller front node, then attach whatever remains of the other list.

**Steps.**
1. Create a `dummy` node and a `tail` pointer at it.
2. While both lists have nodes, attach the smaller front node to `tail.next` and advance that list.
3. Move `tail` forward to the node just attached.
4. When one list runs out, attach the rest of the other one.
5. Return `dummy.next`, the real head.

```python
class Solution:
    def mergeTwoLists(self, list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
        dummy = tail = ListNode()
        while list1 and list2:
            if list1.val <= list2.val:
                tail.next = list1
                list1 = list1.next
            else:
                tail.next = list2
                list2 = list2.next
            tail = tail.next
        tail.next = list1 if list1 else list2
        return dummy.next
```

**Complexity.** Time O(m + n), space O(1).

**Watch out.** The dummy node removes the special case "the merged list is still empty". The leftovers are already sorted, so attach them in one step.

```test
assert to_list(Solution().mergeTwoLists(build_list([1,2,4]), build_list([1,3,4]))) == [1,1,2,3,4,4]
assert to_list(Solution().mergeTwoLists(None, None)) == []
assert to_list(Solution().mergeTwoLists(None, build_list([0]))) == [0]
```

### 138. Copy List with Random Pointer
difficulty: Medium

**Problem.** Each node has `next` and `random` (pointing to any node or `None`). Return a **deep copy** of the list.

**Idea.** Two passes with a dictionary `old node → new node`: first create every copy, then wire `next` and `random` using the dictionary.

**Steps.**
1. Pass 1: `copies[node] = Node(node.val)` for every node.
2. Pass 2: `copies[node].next = copies.get(node.next)`, same for `random`.
3. Return `copies.get(head)`.

```python
class Solution:
    def copyRandomList(self, head: 'Optional[Node]') -> 'Optional[Node]':
        copies = {}
        node = head
        while node:
            copies[node] = Node(node.val)
            node = node.next
        node = head
        while node:
            copies[node].next = copies.get(node.next)
            copies[node].random = copies.get(node.random)
            node = node.next
        return copies.get(head)
```

**Complexity.** Time O(n), space O(n).

**Watch out.** `copies.get(None)` returns `None`, which handles the end of the list and null randoms. O(1)-space trick: interleave copies (`A → A' → B → B'`), set `A'.random = A.random.next`, then split the lists.

```test
a = Node(7); b = Node(13); c = Node(11); a.next = b; b.next = c; b.random = a; c.random = c
cp = Solution().copyRandomList(a)
assert cp is not a and cp.val == 7 and cp.next.val == 13 and cp.next.random is cp and cp.next.next.random is cp.next.next
assert Solution().copyRandomList(None) is None
```

### 92. Reverse Linked List II
difficulty: Medium

**Problem.** Reverse the nodes from position `left` to `right` (1-indexed) in one pass.

**Example.** `[1,2,3,4,5], left = 2, right = 4` → `[1,4,3,2,5]`.

**Idea.** Walk to the node **before** position `left` (`prev`). Then repeatedly take the node right after the current one and move it to the front of the sublist ("head insertion"), `right - left` times.

**Steps.**
1. Dummy before head; move `prev` `left - 1` steps.
2. `cur = prev.next` (it will end up last in the reversed part).
3. Repeat `right - left` times: `nxt = cur.next`; `cur.next = nxt.next`; `nxt.next = prev.next`; `prev.next = nxt`.

```python
class Solution:
    def reverseBetween(self, head: Optional[ListNode], left: int, right: int) -> Optional[ListNode]:
        dummy = ListNode(0, head)
        prev = dummy
        for _ in range(left - 1):
            prev = prev.next
        cur = prev.next
        for _ in range(right - left):
            nxt = cur.next
            cur.next = nxt.next
            nxt.next = prev.next
            prev.next = nxt
        return dummy.next
```

**Complexity.** Time O(n), space O(1).

**Watch out.** The dummy node handles `left = 1` (the head changes). Trace `[1,2,3,4,5]`, left 2: move 3 to front → `1,3,2,4,5`; move 4 to front → `1,4,3,2,5`.

```test
assert to_list(Solution().reverseBetween(build_list([1,2,3,4,5]), 2, 4)) == [1,4,3,2,5]
assert to_list(Solution().reverseBetween(build_list([5]), 1, 1)) == [5]
assert to_list(Solution().reverseBetween(build_list([3,5]), 1, 2)) == [5,3]
```

### 25. Reverse Nodes in k-Group
difficulty: Hard

**Problem.** Reverse the list `k` nodes at a time. A final group with fewer than `k` nodes stays as it is.

**Example.** `[1,2,3,4,5], k = 2` → `[2,1,4,3,5]`.

**Idea.** For each group: first check that `k` nodes exist; if so, reverse them in place and reconnect the group between the node before it (`group_prev`) and the node after it.

**Steps.**
1. Dummy node; `group_prev = dummy`.
2. Find the `k`-th node from `group_prev`; if missing, stop.
3. Reverse the `k` nodes (standard reversal, starting with `prev = kth.next` so the group's new tail links to the rest).
4. Reconnect: `group_prev.next = kth`, and move `group_prev` to the old first node (now last).

```python
class Solution:
    def reverseKGroup(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:
        dummy = ListNode(0, head)
        group_prev = dummy
        while True:
            kth = group_prev
            for _ in range(k):
                kth = kth.next
                if not kth:
                    return dummy.next
            group_next = kth.next
            prev, cur = group_next, group_prev.next
            while cur is not group_next:
                nxt = cur.next
                cur.next = prev
                prev = cur
                cur = nxt
            first = group_prev.next          # becomes the last node of this group
            group_prev.next = kth
            group_prev = first
```

**Complexity.** Time O(n), space O(1).

**Watch out.** Starting the reversal with `prev = group_next` makes the reversed group's tail point to the rest of the list automatically.

```test
assert to_list(Solution().reverseKGroup(build_list([1,2,3,4,5]), 2)) == [2,1,4,3,5]
assert to_list(Solution().reverseKGroup(build_list([1,2,3,4,5]), 3)) == [3,2,1,4,5]
assert to_list(Solution().reverseKGroup(build_list([1,2]), 1)) == [1,2]
```

### 19. Remove Nth Node From End of List
difficulty: Medium

**Problem.** Remove the `n`-th node from the end of the list, in one pass.

**Example.** `[1,2,3,4,5], n = 2` → `[1,2,3,5]`.

**Idea.** Two pointers with a gap of `n`. Move `fast` `n` steps ahead, then move both until `fast` is at the last node; `slow` is then right **before** the node to delete.

**Steps.**
1. Dummy before head; `fast = slow = dummy`.
2. Move `fast` `n` steps.
3. While `fast.next`: move both.
4. `slow.next = slow.next.next`.

```python
class Solution:
    def removeNthFromEnd(self, head: Optional[ListNode], n: int) -> Optional[ListNode]:
        dummy = ListNode(0, head)
        fast = slow = dummy
        for _ in range(n):
            fast = fast.next
        while fast.next:
            fast = fast.next
            slow = slow.next
        slow.next = slow.next.next
        return dummy.next
```

**Complexity.** Time O(n), space O(1).

**Watch out.** The dummy node handles removing the head (`[1], n = 1` → `[]`).

```test
assert to_list(Solution().removeNthFromEnd(build_list([1,2,3,4,5]), 2)) == [1,2,3,5]
assert to_list(Solution().removeNthFromEnd(build_list([1]), 1)) == []
assert to_list(Solution().removeNthFromEnd(build_list([1,2]), 2)) == [2]
```

### 82. Remove Duplicates from Sorted List II
difficulty: Medium

**Problem.** In a sorted list, delete **all** nodes whose value appears more than once (keep only distinct values).

**Example.** `[1,2,3,3,4,4,5]` → `[1,2,5]`.

**Idea.** `prev` points at the last node that's definitely kept. If the node after it starts a run of duplicates, skip the whole run; otherwise move `prev` forward.

**Steps.**
1. Put a `dummy` node before `head` so the head itself can be removed; `prev = dummy`.
2. Look at `cur = prev.next`. If `cur.next` has the same value, a run of duplicates starts here.
3. Skip the whole run: move `cur` forward while it has that value, then set `prev.next = cur`.
4. Otherwise `cur` is unique: keep it and move `prev = cur`.
5. Return `dummy.next`.

```python
class Solution:
    def deleteDuplicates(self, head: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode(0, head)
        prev = dummy
        while prev.next:
            cur = prev.next
            if cur.next and cur.next.val == cur.val:
                val = cur.val
                while cur and cur.val == val:
                    cur = cur.next
                prev.next = cur              # drop the whole run
            else:
                prev = cur
        return dummy.next
```

**Complexity.** Time O(n), space O(1).

**Watch out.** Don't advance `prev` after removing a run: the next node might start another run.

```test
assert to_list(Solution().deleteDuplicates(build_list([1,2,3,3,4,4,5]))) == [1,2,5]
assert to_list(Solution().deleteDuplicates(build_list([1,1,1,2,3]))) == [2,3]
assert to_list(Solution().deleteDuplicates(build_list([1,1]))) == []
```

### 61. Rotate List
difficulty: Medium

**Problem.** Rotate the list to the right by `k` places.

**Example.** `[1,2,3,4,5], k = 2` → `[4,5,1,2,3]`.

**Idea.** Make the list a **ring** (connect tail to head), then cut it at the right place. The new tail is at position `n - k % n - 1`.

**Steps.**
1. Find the length `n` and the tail.
2. `k %= n`; if 0, return head.
3. `tail.next = head` (ring). Walk `n - k - 1` steps from head to the new tail; new head is its `next`; cut.

```python
class Solution:
    def rotateRight(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:
        if not head or not head.next:
            return head
        n, tail = 1, head
        while tail.next:
            tail = tail.next
            n += 1
        k %= n
        if k == 0:
            return head
        tail.next = head
        new_tail = head
        for _ in range(n - k - 1):
            new_tail = new_tail.next
        new_head = new_tail.next
        new_tail.next = None
        return new_head
```

**Complexity.** Time O(n), space O(1).

**Watch out.** `k` can be huge (up to 2·10⁹), so `k %= n` is required.

```test
assert to_list(Solution().rotateRight(build_list([1,2,3,4,5]), 2)) == [4,5,1,2,3]
assert to_list(Solution().rotateRight(build_list([0,1,2]), 4)) == [2,0,1]
assert to_list(Solution().rotateRight(None, 1)) == []
```

### 86. Partition List
difficulty: Medium

**Problem.** Reorder the list so all nodes `< x` come before nodes `>= x`, keeping the original relative order in each part.

**Example.** `[1,4,3,2,5,2], x = 3` → `[1,2,2,4,3,5]`.

**Idea.** Build two lists with dummy heads (`less` and `greater`), append each node to the right one, then join them.

**Steps.**
1. Make two dummy heads: `less` for values `< x`, `greater` for the rest, each with a tail pointer.
2. Walk the list and append each node to the matching chain. This keeps the original order in both.
3. Set `gt.next = None` so the last node doesn't still point into the old list.
4. Link the end of the `less` chain to the start of `greater`; return `less.next`.

```python
class Solution:
    def partition(self, head: Optional[ListNode], x: int) -> Optional[ListNode]:
        less = lt = ListNode()
        greater = gt = ListNode()
        while head:
            if head.val < x:
                lt.next = head
                lt = lt.next
            else:
                gt.next = head
                gt = gt.next
            head = head.next
        gt.next = None               # end the second list
        lt.next = greater.next
        return less.next
```

**Complexity.** Time O(n), space O(1).

**Watch out.** `gt.next = None` is essential: the last "greater" node may still point to a "less" node and create a cycle.

```test
assert to_list(Solution().partition(build_list([1,4,3,2,5,2]), 3)) == [1,2,2,4,3,5]
assert to_list(Solution().partition(build_list([2,1]), 2)) == [1,2]
```

### 146. LRU Cache
difficulty: Medium

**Problem.** Design a cache with capacity `capacity`: `get(key)` returns the value or -1; `put(key, value)` inserts/updates and, when over capacity, evicts the **least recently used** key. Both O(1).

**Idea.** A hash map for O(1) lookup + an order of recency. Python's `OrderedDict` keeps insertion order and can move a key to the end in O(1): the end is "most recent", the front is "least recent".

**Steps.**
1. Store the items in an `OrderedDict`: the end is the most recently used, the front the least.
2. `get(key)`: if missing return `-1`; else move the key to the end and return its value.
3. `put(key, value)`: if the key exists, move it to the end; then set the value.
4. If the size is now above capacity, remove the front item with `popitem(last=False)`.

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.data = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.data:
            return -1
        self.data.move_to_end(key)          # mark as most recently used
        return self.data[key]

    def put(self, key: int, value: int) -> None:
        if key in self.data:
            self.data.move_to_end(key)
        self.data[key] = value
        if len(self.data) > self.cap:
            self.data.popitem(last=False)   # remove the least recently used
```

**Complexity.** O(1) per operation.

**Watch out.** Interviewers often ask for the classic version without `OrderedDict`: a dictionary `key → node` plus a **doubly linked list** with dummy head and tail; move nodes to the front on use and remove from the tail when over capacity.

```py
class Node:
    def __init__(self, k=0, v=0):
        self.k, self.v, self.prev, self.next = k, v, None, None

class LRUCache:
    def __init__(self, capacity):
        self.cap, self.map = capacity, {}
        self.head, self.tail = Node(), Node()       # head.next = most recent
        self.head.next, self.tail.prev = self.tail, self.head

    def _remove(self, n):
        n.prev.next, n.next.prev = n.next, n.prev

    def _add_front(self, n):
        n.prev, n.next = self.head, self.head.next
        self.head.next.prev = n
        self.head.next = n

    def get(self, key):
        if key not in self.map:
            return -1
        n = self.map[key]
        self._remove(n); self._add_front(n)
        return n.v

    def put(self, key, value):
        if key in self.map:
            self._remove(self.map[key])
        n = self.map[key] = Node(key, value)
        self._add_front(n)
        if len(self.map) > self.cap:
            lru = self.tail.prev
            self._remove(lru)
            del self.map[lru.k]
```

```test
c = LRUCache(2); c.put(1, 1); c.put(2, 2)
assert c.get(1) == 1; c.put(3, 3); assert c.get(2) == -1; c.put(4, 4)
assert c.get(1) == -1 and c.get(3) == 3 and c.get(4) == 4
```

# Binary Tree General

### 104. Maximum Depth of Binary Tree
difficulty: Easy

**Problem.** Return the number of nodes on the longest root-to-leaf path.

**Example.** `[3,9,20,null,null,15,7]` → `3`.

**Idea.** Depth of a tree = 1 + the larger depth of its two subtrees; an empty tree has depth 0.

**Steps.**
1. If the node is `None`, its depth is 0.
2. Otherwise compute the depth of the left subtree and of the right subtree recursively.
3. Return `1 +` the larger of the two (the 1 counts the current node).

```python
class Solution:
    def maxDepth(self, root: Optional[TreeNode]) -> int:
        if not root:
            return 0
        return 1 + max(self.maxDepth(root.left), self.maxDepth(root.right))
```

**Complexity.** Time O(n), space O(h).

**Watch out.** Iterative BFS: count levels, processing exactly `len(queue)` nodes per level (that snapshot is what separates levels).

```py
from collections import deque
if not root:
    return 0
q, depth = deque([root]), 0
while q:
    for _ in range(len(q)):
        node = q.popleft()
        if node.left: q.append(node.left)
        if node.right: q.append(node.right)
    depth += 1
return depth
```

```test
assert Solution().maxDepth(build_tree([3,9,20,None,None,15,7])) == 3
assert Solution().maxDepth(build_tree([1,None,2])) == 2
assert Solution().maxDepth(None) == 0
```

### 100. Same Tree
difficulty: Easy

**Problem.** Are two binary trees identical in shape and values?

**Idea.** Compare node by node: both empty → same; one empty → different; values differ → different; otherwise both subtrees must match.

**Steps.**
1. Both nodes `None` → the trees match here → `True`.
2. Only one is `None`, or their values differ → `False`.
3. Otherwise both left subtrees and both right subtrees must also be the same: recurse on both and combine with `and`.

```python
class Solution:
    def isSameTree(self, p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
        if not p and not q:
            return True
        if not p or not q or p.val != q.val:
            return False
        return self.isSameTree(p.left, q.left) and self.isSameTree(p.right, q.right)
```

**Complexity.** Time O(n), space O(h).

**Watch out.** Comparing traversal lists without `None` markers fails: `[1,2]` and `[1,null,2]` have the same preorder.

```test
assert Solution().isSameTree(build_tree([1,2,3]), build_tree([1,2,3])) is True
assert Solution().isSameTree(build_tree([1,2]), build_tree([1,None,2])) is False
assert Solution().isSameTree(build_tree([1,2,1]), build_tree([1,1,2])) is False
```

### 226. Invert Binary Tree
difficulty: Easy

**Problem.** Mirror the tree: swap every node's left and right children.

**Idea.** Swap the children of the current node, then invert both subtrees.

**Steps.**
1. If the node is `None`, return `None`.
2. Swap its left and right children.
3. Recursively invert the left subtree and the right subtree.
4. Return the node (the root of the inverted tree).

```python
class Solution:
    def invertTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        if not root:
            return None
        root.left, root.right = root.right, root.left
        self.invertTree(root.left)
        self.invertTree(root.right)
        return root
```

**Complexity.** Time O(n), space O(h).

**Watch out.** Swapping moves whole subtrees; the recursion flips everything inside them. A BFS/queue version works the same way (swap each popped node's children).

```test
assert tree_to_list(Solution().invertTree(build_tree([4,2,7,1,3,6,9]))) == [4,7,2,9,6,3,1]
assert tree_to_list(Solution().invertTree(build_tree([2,1,3]))) == [2,3,1]
assert Solution().invertTree(None) is None
```

### 101. Symmetric Tree
difficulty: Easy

**Problem.** Is the tree a mirror of itself around its center?

**Idea.** Two subtrees are mirrors when their roots are equal and **left of one** mirrors **right of the other** (outer pair and inner pair).

**Steps.**
1. Compare the root's left subtree with its right subtree using a helper `mirror(a, b)`.
2. Both `None` → `True`. One `None` or different values → `False`.
3. Otherwise the **outer** children must mirror (`a.left`, `b.right`) and the **inner** children too (`a.right`, `b.left`).

```python
class Solution:
    def isSymmetric(self, root: Optional[TreeNode]) -> bool:
        def mirror(a, b):
            if not a and not b:
                return True
            if not a or not b or a.val != b.val:
                return False
            return mirror(a.left, b.right) and mirror(a.right, b.left)
        return mirror(root.left, root.right)
```

**Complexity.** Time O(n), space O(h).

**Watch out.** Iterative version: a queue of pairs, pushing `(a.left, b.right)` and `(a.right, b.left)`.

```test
assert Solution().isSymmetric(build_tree([1,2,2,3,4,4,3])) is True
assert Solution().isSymmetric(build_tree([1,2,2,None,3,None,3])) is False
```

### 105. Construct Binary Tree from Preorder and Inorder Traversal
difficulty: Medium

**Problem.** Rebuild the tree from its preorder and inorder traversals (values are unique).

**Example.** `preorder = [3,9,20,15,7], inorder = [9,3,15,20,7]` → `[3,9,20,null,null,15,7]`.

**Idea.** The first preorder value is the root. In inorder, everything left of the root is the left subtree, everything right is the right subtree. A dictionary `value → inorder index` finds the split in O(1). Consume preorder from left to right, building the **left** subtree first.

**Steps.**
1. `idx = {v: i for i, v in enumerate(inorder)}`; a pointer `pre` into preorder.
2. `build(lo, hi)` builds the subtree of `inorder[lo..hi]`: take `preorder[pre]` as root, find its inorder position `m`, build left `(lo, m-1)` then right `(m+1, hi)`.

```python
class Solution:
    def buildTree(self, preorder: List[int], inorder: List[int]) -> Optional[TreeNode]:
        idx = {v: i for i, v in enumerate(inorder)}
        it = iter(preorder)

        def build(lo, hi):
            if lo > hi:
                return None
            val = next(it)
            node = TreeNode(val)
            m = idx[val]
            node.left = build(lo, m - 1)
            node.right = build(m + 1, hi)
            return node

        return build(0, len(inorder) - 1)
```

**Complexity.** Time O(n), space O(n).

**Watch out.** Left must be built **before** right, because preorder lists the whole left subtree first. Slicing arrays instead of passing indexes makes it O(n²).

```test
assert tree_to_list(Solution().buildTree([3,9,20,15,7], [9,3,15,20,7])) == [3,9,20,None,None,15,7]
assert tree_to_list(Solution().buildTree([-1], [-1])) == [-1]
```

### 106. Construct Binary Tree from Inorder and Postorder Traversal
difficulty: Medium

**Problem.** Rebuild the tree from inorder and postorder traversals (unique values).

**Idea.** The **last** postorder value is the root. Reading postorder **backward** gives root, then the right subtree, then the left. So build the **right** subtree before the left.

**Steps.**
1. Map each value to its index in `inorder` for O(1) lookups.
2. Read `postorder` from the end: each value taken is the root of the current subtree.
3. Find the root's index `m` in inorder: everything left of `m` is its left subtree, right of `m` its right subtree.
4. Build the **right** subtree first (`m + 1 .. hi`), then the left (`lo .. m - 1`), because reversed postorder lists root, right, left.
5. A range with `lo > hi` is empty → `None`.

```python
class Solution:
    def buildTree(self, inorder: List[int], postorder: List[int]) -> Optional[TreeNode]:
        idx = {v: i for i, v in enumerate(inorder)}
        it = reversed(postorder)

        def build(lo, hi):
            if lo > hi:
                return None
            val = next(it)
            node = TreeNode(val)
            m = idx[val]
            node.right = build(m + 1, hi)
            node.left = build(lo, m - 1)
            return node

        return build(0, len(inorder) - 1)
```

**Complexity.** Time O(n), space O(n).

**Watch out.** The order of the two recursive calls is the whole difference from #105.

```test
assert tree_to_list(Solution().buildTree([9,3,15,20,7], [9,15,7,20,3])) == [3,9,20,None,None,15,7]
assert tree_to_list(Solution().buildTree([-1], [-1])) == [-1]
```

### 117. Populating Next Right Pointers in Each Node II
difficulty: Medium

**Problem.** Each node has a `next` pointer. Point it to the node on its right **on the same level** (or `None`). The tree is any binary tree. Follow-up: O(1) extra space.

**Idea.** Use the already-linked level as a linked list to link the next level. Walk the current level through `next` pointers; append its children to the next level with a dummy node and a `tail` pointer.

**Steps.**
1. `cur = root`.
2. While `cur`: `dummy = Node(0)`, `tail = dummy`. For each node in the level (via `next`), append `left` then `right` children to `tail`.
3. Move `cur = dummy.next` (the start of the next level).

```python
class Solution:
    def connect(self, root: 'Node') -> 'Node':
        cur = root
        while cur:
            dummy = tail = Node(0)
            node = cur
            while node:
                if node.left:
                    tail.next = node.left
                    tail = tail.next
                if node.right:
                    tail.next = node.right
                    tail = tail.next
                node = node.next
            cur = dummy.next
        return root
```

**Complexity.** Time O(n), space O(1).

**Watch out.** BFS with a queue is easier (link each node to the next one popped in the same level) but uses O(width) space.

```test
r = Node(1, Node(2, Node(4), Node(5)), Node(3, None, Node(7)))
Solution().connect(r)
assert r.next is None and r.left.next is r.right and r.left.left.next is r.left.right and r.left.right.next is r.right.right
```

### 114. Flatten Binary Tree to Linked List
difficulty: Medium

**Problem.** Flatten the tree **in place** into a "linked list" using `right` pointers, in preorder; all `left` pointers become `None`.

**Example.** `[1,2,5,3,4,null,6]` → `1 → 2 → 3 → 4 → 5 → 6`.

**Idea (O(1) space, Morris-like).** For each node with a left subtree: find the **rightmost** node of the left subtree (the last node of the left part in preorder). Attach the current right subtree there, move the left subtree to the right, clear `left`. Then continue with `node.right`.

**Steps.**
1. Start at `node = root`.
2. If the node has a left child, find the rightmost node of the left subtree (`last`).
3. Attach the node's right subtree after `last`: `last.right = node.right`.
4. Move the left subtree to the right: `node.right = node.left`, `node.left = None`.
5. Go to `node.right` and repeat until the end. No extra memory is used.

```python
class Solution:
    def flatten(self, root: Optional[TreeNode]) -> None:
        node = root
        while node:
            if node.left:
                last = node.left
                while last.right:
                    last = last.right
                last.right = node.right
                node.right = node.left
                node.left = None
            node = node.right
```

**Complexity.** Time O(n) (each edge walked a constant number of times), space O(1).

**Watch out.** Recursive alternative: process nodes in **reverse preorder** (right, left, root) with a `prev` pointer: `node.right = prev; node.left = None; prev = node`.

```test
r = build_tree([1,2,5,3,4,None,6]); Solution().flatten(r)
out = []
while r:
    assert r.left is None; out.append(r.val); r = r.right
assert out == [1,2,3,4,5,6]
```

### 112. Path Sum
difficulty: Easy

**Problem.** Is there a root-to-**leaf** path whose values add up to `targetSum`?

**Idea.** Subtract each node's value going down. At a leaf, check whether the remaining sum equals the leaf's value.

**Steps.**
1. Empty node → no path → `False`.
2. At a leaf (no children), the path works if the leaf's value equals the remaining target.
3. Otherwise subtract the node's value from the target.
4. Return whether the left **or** the right subtree has a path for the remaining sum.

```python
class Solution:
    def hasPathSum(self, root: Optional[TreeNode], targetSum: int) -> bool:
        if not root:
            return False
        if not root.left and not root.right:
            return root.val == targetSum
        rest = targetSum - root.val
        return self.hasPathSum(root.left, rest) or self.hasPathSum(root.right, rest)
```

**Complexity.** Time O(n), space O(h).

**Watch out.** The path must end at a **leaf**. An empty tree is false even when `targetSum = 0`.

```test
assert Solution().hasPathSum(build_tree([5,4,8,11,None,13,4,7,2,None,None,None,1]), 22) is True
assert Solution().hasPathSum(build_tree([1,2,3]), 5) is False
assert Solution().hasPathSum(None, 0) is False
assert Solution().hasPathSum(build_tree([1,2]), 1) is False
```

### 129. Sum Root to Leaf Numbers
difficulty: Medium

**Problem.** Each root-to-leaf path spells a number (digits from root to leaf). Return the sum of all these numbers.

**Example.** `[1,2,3]` → `12 + 13 = 25`.

**Idea.** Carry the number built so far down the tree: `cur = cur * 10 + node.val`. At a leaf, that's a complete number.

**Steps.**
1. DFS with the number built so far, starting at 0.
2. At each node, extend it: `cur = cur * 10 + node.val`.
3. At a leaf, `cur` is a complete root-to-leaf number: return it.
4. Otherwise return the sum from the left and right subtrees. `None` children add 0.

```python
class Solution:
    def sumNumbers(self, root: Optional[TreeNode]) -> int:
        def dfs(node, cur):
            if not node:
                return 0
            cur = cur * 10 + node.val
            if not node.left and not node.right:
                return cur
            return dfs(node.left, cur) + dfs(node.right, cur)
        return dfs(root, 0)
```

**Complexity.** Time O(n), space O(h).

**Watch out.** Return the number only at leaves; returning at `None` children would count partial numbers twice.

```test
assert Solution().sumNumbers(build_tree([1,2,3])) == 25
assert Solution().sumNumbers(build_tree([4,9,0,5,1])) == 1026
```

### 124. Binary Tree Maximum Path Sum
difficulty: Hard

**Problem.** A path is any sequence of connected nodes (no node twice; it doesn't have to pass the root). Return the maximum path sum. Values can be negative.

**Example.** `[-10,9,20,null,null,15,7]` → `42` (15 + 20 + 7).

**Idea.** For each node, compute the best **downward** path starting at it: `node.val + max(0, best_left, best_right)` (a negative branch is better skipped). The best path that **bends** at this node is `node.val + max(0, left) + max(0, right)`; update a global answer with it.

**Steps.**
1. `gain(node)`: return 0 for `None`.
2. `l = max(gain(left), 0)`, `r = max(gain(right), 0)`.
3. `best = max(best, node.val + l + r)`.
4. Return `node.val + max(l, r)` (a path going up can use only one side).

```python
class Solution:
    def maxPathSum(self, root: Optional[TreeNode]) -> int:
        best = float('-inf')

        def gain(node):
            nonlocal best
            if not node:
                return 0
            l = max(gain(node.left), 0)
            r = max(gain(node.right), 0)
            best = max(best, node.val + l + r)
            return node.val + max(l, r)

        gain(root)
        return best
```

**Complexity.** Time O(n), space O(h).

**Watch out.** Start `best` at `-inf`, not 0: a tree of all negatives must return its largest value.

```test
assert Solution().maxPathSum(build_tree([1,2,3])) == 6
assert Solution().maxPathSum(build_tree([-10,9,20,None,None,15,7])) == 42
assert Solution().maxPathSum(build_tree([-3])) == -3
```

### 173. Binary Search Tree Iterator
difficulty: Medium

**Problem.** Implement an iterator over a BST in **inorder** (sorted) order: `next()` returns the next smallest value, `hasNext()`. Average O(1) time and O(h) memory.

**Idea.** Simulate the iterative inorder traversal: a stack holding the path of "left" nodes. `next()` pops the smallest node, then pushes the left spine of its right subtree.

**Steps.**
1. Constructor: push the root and all its left descendants on a stack (the path to the smallest value).
2. `next()`: pop the top node. That's the next smallest value.
3. Before returning, push the left spine of that node's right child, which holds the next larger values.
4. `hasNext()`: True while the stack isn't empty. Each node is pushed and popped once, so O(1) on average.

```python
class BSTIterator:
    def __init__(self, root: Optional[TreeNode]):
        self.stack = []
        self._push_left(root)

    def _push_left(self, node):
        while node:
            self.stack.append(node)
            node = node.left

    def next(self) -> int:
        node = self.stack.pop()
        self._push_left(node.right)
        return node.val

    def hasNext(self) -> bool:
        return bool(self.stack)
```

**Complexity.** `next` is amortized O(1) (each node pushed and popped once); memory O(h).

**Watch out.** Don't flatten the whole tree into a list in `__init__`: that works but uses O(n) memory, not O(h).

```test
it = BSTIterator(build_tree([7,3,15,None,None,9,20]))
assert [it.next(), it.next(), it.hasNext(), it.next(), it.next(), it.next(), it.hasNext()] == [3,7,True,9,15,20,False]
```

### 222. Count Complete Tree Nodes
difficulty: Easy

**Problem.** Count the nodes of a **complete** binary tree faster than O(n).

**Idea.** Compare the leftmost depth and the rightmost depth of a subtree. If equal, it's a **perfect** tree with `2^h - 1` nodes. Otherwise recurse on both children. Only one branch per level is not perfect, so it's O(log² n).

**Steps.**
1. Measure the height going only left (`lh`) and only right (`rh`).
2. If they're equal, the subtree is perfect: return `2^h - 1` (`(1 << lh) - 1`).
3. Otherwise return `1 + countNodes(left) + countNodes(right)`.
4. At each level at most one side isn't perfect, so this is O(log² n).

```python
class Solution:
    def countNodes(self, root: Optional[TreeNode]) -> int:
        if not root:
            return 0
        lh = rh = 0
        node = root
        while node:
            lh += 1
            node = node.left
        node = root
        while node:
            rh += 1
            node = node.right
        if lh == rh:
            return (1 << lh) - 1
        return 1 + self.countNodes(root.left) + self.countNodes(root.right)
```

**Complexity.** Time O(log² n), space O(log n).

**Watch out.** `1 << h` is `2**h`. A plain recursive count also passes (O(n)), but the interview point is using the "complete" property.

```test
assert Solution().countNodes(build_tree([1,2,3,4,5,6])) == 6
assert Solution().countNodes(None) == 0
assert Solution().countNodes(build_tree([1])) == 1
assert Solution().countNodes(build_tree(list(range(1, 16)))) == 15
```

### 236. Lowest Common Ancestor of a Binary Tree
difficulty: Medium

**Problem.** Given two nodes `p` and `q` (both in the tree), return their lowest common ancestor (a node can be its own ancestor).

**Idea.** Search both nodes recursively. A call returns the node if it found `p` or `q` in its subtree. If **both** sides return something, the current node is where the paths split: it's the LCA. If only one side returns, pass that up.

**Steps.**
1. If the node is `None`, `p` or `q`, return it.
2. Search the left subtree and the right subtree.
3. If both searches return a node, `p` and `q` are on different sides, so the current node is the LCA.
4. Otherwise return whichever side found something (it holds the LCA or the one node found).

```python
class Solution:
    def lowestCommonAncestor(self, root: 'TreeNode', p: 'TreeNode', q: 'TreeNode') -> 'TreeNode':
        if not root or root is p or root is q:
            return root
        left = self.lowestCommonAncestor(root.left, p, q)
        right = self.lowestCommonAncestor(root.right, p, q)
        if left and right:
            return root
        return left or right
```

**Complexity.** Time O(n), space O(h).

**Watch out.** If `p` is an ancestor of `q`, the search stops at `p` and returns it, which is correct.

```test
t = build_tree([3,5,1,6,2,0,8,None,None,7,4])
assert Solution().lowestCommonAncestor(t, find(t,5), find(t,1)).val == 3
assert Solution().lowestCommonAncestor(t, find(t,5), find(t,4)).val == 5
```

# Binary Tree BFS

### 199. Binary Tree Right Side View
difficulty: Medium

**Problem.** Standing on the right of the tree, return the values you can see from top to bottom.

**Example.** `[1,2,3,4,null,null,null,5]` → `[1,3,4,5]`.

**Idea.** Level-order BFS; the **last** node of each level is the visible one.

**Steps.**
1. Queue with the root.
2. For each level: `size = len(q)`; pop `size` nodes, push children left then right; record the value when `i == size - 1`.

```python
class Solution:
    def rightSideView(self, root: Optional[TreeNode]) -> List[int]:
        res = []
        if not root:
            return res
        q = deque([root])
        while q:
            size = len(q)
            for i in range(size):
                node = q.popleft()
                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)
                if i == size - 1:
                    res.append(node.val)
        return res
```

**Complexity.** Time O(n), space O(width).

**Watch out.** "Visible from the right" is not "follow right children": deeper levels may be visible only through the left subtree. DFS alternative: visit right before left and record the first node at each new depth (`if depth == len(res)`).

```test
assert Solution().rightSideView(build_tree([1,2,3,None,5,None,4])) == [1,3,4]
assert Solution().rightSideView(build_tree([1,2,3,4,None,None,None,5])) == [1,3,4,5]
assert Solution().rightSideView(None) == []
```

### 637. Average of Levels in Binary Tree
difficulty: Easy

**Problem.** Return the average value of the nodes on each level.

**Example.** `[3,9,20,null,null,15,7]` → `[3.0, 14.5, 11.0]`.

**Idea.** Level-order BFS: sum the values of each level and divide by its size.

**Steps.**
1. Put the root in a queue.
2. For each level, record `size = len(q)`: that's how many nodes the level has.
3. Pop exactly `size` nodes, add up their values, and queue their children.
4. Append `total / size` (true division gives a float). Repeat until the queue is empty.

```python
class Solution:
    def averageOfLevels(self, root: Optional[TreeNode]) -> List[float]:
        res = []
        q = deque([root])
        while q:
            size = len(q)
            total = 0
            for _ in range(size):
                node = q.popleft()
                total += node.val
                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)
            res.append(total / size)
        return res
```

**Complexity.** Time O(n), space O(width).

**Watch out.** Use `/`, not `//`. In Java/C++, use a `long`/`double` sum: values can be ±2³¹.

```test
assert Solution().averageOfLevels(build_tree([3,9,20,None,None,15,7])) == [3.0, 14.5, 11.0]
```

### 102. Binary Tree Level Order Traversal
difficulty: Medium

**Problem.** Return the values level by level, left to right.

**Example.** `[3,9,20,null,null,15,7]` → `[[3],[9,20],[15,7]]`.

**Idea.** BFS with a queue, processing exactly `len(q)` nodes per level.

**Steps.**
1. Empty tree → `[]`. Otherwise start a queue with the root.
2. For each level, pop `len(q)` nodes (the size fixed at the start of the level).
3. Add each popped value to `level` and queue its children.
4. Append `level` to the result; repeat until the queue is empty.

```python
class Solution:
    def levelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:
        res = []
        if not root:
            return res
        q = deque([root])
        while q:
            level = []
            for _ in range(len(q)):
                node = q.popleft()
                level.append(node.val)
                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)
            res.append(level)
        return res
```

**Complexity.** Time O(n), space O(width).

**Watch out.** `range(len(q))` is evaluated once at the start of the `for`, which is exactly the level size even though the queue grows.

```test
assert Solution().levelOrder(build_tree([3,9,20,None,None,15,7])) == [[3],[9,20],[15,7]]
assert Solution().levelOrder(build_tree([1])) == [[1]]
assert Solution().levelOrder(None) == []
```

### 103. Binary Tree Zigzag Level Order Traversal
difficulty: Medium

**Problem.** Level order, but alternate direction: left→right, then right→left, and so on.

**Example.** `[3,9,20,null,null,15,7]` → `[[3],[20,9],[15,7]]`.

**Idea.** Same BFS as #102; reverse every second level before adding it.

**Steps.**
1. Do the normal level-order BFS from #102.
2. Keep a flag `left_to_right`, starting `True`.
3. Append each level as is, or reversed when the flag is `False`.
4. Flip the flag after every level.

```python
class Solution:
    def zigzagLevelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:
        res = []
        if not root:
            return res
        q = deque([root])
        left_to_right = True
        while q:
            level = []
            for _ in range(len(q)):
                node = q.popleft()
                level.append(node.val)
                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)
            res.append(level if left_to_right else level[::-1])
            left_to_right = not left_to_right
        return res
```

**Complexity.** Time O(n), space O(width).

**Watch out.** Don't change the order in which children are queued; only the collected level list is reversed.

```test
assert Solution().zigzagLevelOrder(build_tree([3,9,20,None,None,15,7])) == [[3],[20,9],[15,7]]
assert Solution().zigzagLevelOrder(build_tree([1,2,3,4,None,None,5])) == [[1],[3,2],[4,5]]
```

# Binary Search Tree

### 530. Minimum Absolute Difference in BST
difficulty: Easy

**Problem.** Return the minimum absolute difference between the values of any two nodes of a BST.

**Idea.** Inorder traversal of a BST visits values in **sorted** order, and the minimum difference in a sorted list is between neighbours. Track the previous value during the traversal.

**Steps.**
1. Inorder traversal (left, node, right) visits BST values in sorted order.
2. Keep `prev`, the previously visited value.
3. At each node, update `best = min(best, node.val - prev)`.
4. Set `prev = node.val` and continue. Return `best`.

```python
class Solution:
    def getMinimumDifference(self, root: Optional[TreeNode]) -> int:
        prev = None
        best = float('inf')

        def inorder(node):
            nonlocal prev, best
            if not node:
                return
            inorder(node.left)
            if prev is not None:
                best = min(best, node.val - prev)
            prev = node.val
            inorder(node.right)

        inorder(root)
        return best
```

**Complexity.** Time O(n), space O(h).

**Watch out.** `nonlocal` is needed to assign to `prev` and `best` inside the nested function. Collecting all values and sorting also works but is O(n log n) and ignores the BST property.

```test
assert Solution().getMinimumDifference(build_tree([4,2,6,1,3])) == 1
assert Solution().getMinimumDifference(build_tree([1,0,48,None,None,12,49])) == 1
```

### 230. Kth Smallest Element in a BST
difficulty: Medium

**Problem.** Return the `k`-th smallest value (1-indexed) in a BST.

**Idea.** Iterative inorder traversal; the `k`-th popped node is the answer. It stops early, without visiting the whole tree.

**Steps.**
1. Go left from the current node as far as possible, pushing every node on a stack.
2. Pop a node: it's the next smallest value. Decrease `k`.
3. If `k` reaches 0, return its value.
4. Otherwise move to its right child and repeat.

```python
class Solution:
    def kthSmallest(self, root: Optional[TreeNode], k: int) -> int:
        stack = []
        node = root
        while stack or node:
            while node:
                stack.append(node)
                node = node.left
            node = stack.pop()
            k -= 1
            if k == 0:
                return node.val
            node = node.right
```

**Complexity.** Time O(h + k), space O(h).

**Watch out (follow-up).** If the tree is modified often and `k`-th queries are frequent, store the size of each subtree in its node; then each query is O(h).

```test
assert Solution().kthSmallest(build_tree([3,1,4,None,2]), 1) == 1
assert Solution().kthSmallest(build_tree([5,3,6,2,4,None,None,1]), 3) == 3
```

### 98. Validate Binary Search Tree
difficulty: Medium

**Problem.** Is the tree a valid BST (every node's left subtree strictly smaller, right subtree strictly larger)?

**Idea.** Pass down the allowed range `(low, high)`. Going left lowers the upper bound to the node's value; going right raises the lower bound.

**Steps.**
1. Call `valid(root, -inf, +inf)`.
2. Empty node → valid.
3. The node's value must be strictly between `low` and `high`; otherwise → `False`.
4. Left child: range `(low, node.val)`. Right child: range `(node.val, high)`. Both must be valid.

```python
class Solution:
    def isValidBST(self, root: Optional[TreeNode]) -> bool:
        def valid(node, low, high):
            if not node:
                return True
            if not (low < node.val < high):
                return False
            return valid(node.left, low, node.val) and valid(node.right, node.val, high)
        return valid(root, float('-inf'), float('inf'))
```

**Complexity.** Time O(n), space O(h).

**Watch out.** Checking only `left.val < node.val < right.val` is wrong: `[5,4,6,null,null,3,7]` passes that local check but 3 is in the right subtree of 5. Alternative: inorder traversal must be strictly increasing.

```test
assert Solution().isValidBST(build_tree([2,1,3])) is True
assert Solution().isValidBST(build_tree([5,1,4,None,None,3,6])) is False
assert Solution().isValidBST(build_tree([5,4,6,None,None,3,7])) is False
assert Solution().isValidBST(build_tree([2,2,2])) is False
```
