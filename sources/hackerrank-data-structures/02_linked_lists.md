## Linked Lists

### Print the Elements of a Linked List

**Problem.** Print each node's value of a singly linked list, one per line.

**Idea.** Walk from the head following `next` until `None`.

**Steps.**
1. `node = head`; while `node`: print `node.data`, move to `node.next`.

```python
class SinglyLinkedListNode:
    def __init__(self, node_data):
        self.data = node_data
        self.next = None


class SinglyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def insert_node(self, node_data):
        node = SinglyLinkedListNode(node_data)
        if not self.head:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node


def printLinkedList(head):
    node = head
    while node:
        print(node.data)
        node = node.next


if __name__ == '__main__':
    llist = SinglyLinkedList()
    for _ in range(int(input())):
        llist.insert_node(int(input()))
    printLinkedList(llist.head)
```

**Watch out.** An empty list (head `None`) prints nothing, and the `while node` loop handles it with no special case.

```stdin
2
16
13
```

```stdout
16
13
```

### Insert a Node at the Tail of a Linked List

**Problem.** Append a value to the end of a list (given only its head) and return the head.

**Idea.** If the list is empty, the new node *is* the head. Otherwise walk to the last node and link the new node after it.

**Steps.**
1. Create the node; if `head` is `None`, return it.
2. Walk to the node whose `next` is `None`; attach; return `head`.

```python
import os


class SinglyLinkedListNode:
    def __init__(self, node_data):
        self.data = node_data
        self.next = None


def print_singly_linked_list(node, sep, fptr):
    while node:
        fptr.write(str(node.data))
        node = node.next
        if node:
            fptr.write(sep)


def insertNodeAtTail(head, data):
    node = SinglyLinkedListNode(data)
    if head is None:
        return node
    cur = head
    while cur.next:
        cur = cur.next
    cur.next = node
    return head


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    head = None
    for _ in range(int(input())):
        head = insertNodeAtTail(head, int(input()))
    print_singly_linked_list(head, '\n', fptr)
    fptr.write('\n')
    fptr.close()
```

**Watch out.** Each call walks the whole list, so building `n` nodes this way is O(n²). That is fine for the limits here, and it is the interface the exercise fixes.

```stdin
5
141
302
164
530
474
```

```stdout
141
302
164
530
474
```

### Insert a node at the head of a linked list

**Problem.** Insert a value at the front and return the new head.

**Idea.** The new node points at the old head and becomes the head itself. This is O(1).

**Steps.**
1. `node.next = head`; return `node`.

```python
import os


class SinglyLinkedListNode:
    def __init__(self, node_data):
        self.data = node_data
        self.next = None


def print_singly_linked_list(node, sep, fptr):
    while node:
        fptr.write(str(node.data))
        node = node.next
        if node:
            fptr.write(sep)


def insertNodeAtHead(llist, data):
    node = SinglyLinkedListNode(data)
    node.next = llist
    return node


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    head = None
    for _ in range(int(input())):
        head = insertNodeAtHead(head, int(input()))
    print_singly_linked_list(head, '\n', fptr)
    fptr.write('\n')
    fptr.close()
```

**Watch out.** Inserting each value at the head reverses the input order, which is exactly what the sample shows.

```stdin
5
383
484
392
975
321
```

```stdout
321
975
392
484
383
```

### Insert a node at a specific position in a linked list

**Problem.** Insert a value so that it ends up at 0-based `position`, and return the head.

**Idea.** Position 0 means a new head. Otherwise walk `position − 1` steps to the node *before* the target spot and splice the new node in.

**Steps.**
1. If `position == 0`, link the new node to the head and return it.
2. Walk to node `position − 1`; set `node.next = cur.next` and `cur.next = node`.

```python
import os


class SinglyLinkedListNode:
    def __init__(self, node_data):
        self.data = node_data
        self.next = None


class SinglyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def insert_node(self, node_data):
        node = SinglyLinkedListNode(node_data)
        if not self.head:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node


def print_singly_linked_list(node, sep, fptr):
    while node:
        fptr.write(str(node.data))
        node = node.next
        if node:
            fptr.write(sep)


def insertNodeAtPosition(llist, data, position):
    node = SinglyLinkedListNode(data)
    if position == 0:
        node.next = llist
        return node
    cur = llist
    for _ in range(position - 1):
        cur = cur.next
    node.next = cur.next
    cur.next = node
    return llist


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    llist = SinglyLinkedList()
    for _ in range(int(input().strip())):
        llist.insert_node(int(input().strip()))
    data = int(input().strip())
    position = int(input().strip())
    print_singly_linked_list(insertNodeAtPosition(llist.head, data, position), ' ', fptr)
    fptr.write('\n')
    fptr.close()
```

**Watch out.** Set `node.next` *before* overwriting `cur.next`; doing it the other way round loses the rest of the list.

```stdin
3
16
13
7
1
2
```

```stdout
16 13 1 7
```

### Delete a Node

**Problem.** Delete the node at 0-based `position` and return the head.

**Idea.** Deleting the head returns `head.next`. Otherwise stop at the node before the target and bypass the target.

**Steps.**
1. `position == 0` → return `head.next`.
2. Walk `position − 1` steps; `cur.next = cur.next.next`.

```python
import os


class SinglyLinkedListNode:
    def __init__(self, node_data):
        self.data = node_data
        self.next = None


class SinglyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def insert_node(self, node_data):
        node = SinglyLinkedListNode(node_data)
        if not self.head:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node


def print_singly_linked_list(node, sep, fptr):
    while node:
        fptr.write(str(node.data))
        node = node.next
        if node:
            fptr.write(sep)


def deleteNode(llist, position):
    if position == 0:
        return llist.next
    cur = llist
    for _ in range(position - 1):
        cur = cur.next
    cur.next = cur.next.next
    return llist


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    llist = SinglyLinkedList()
    for _ in range(int(input().strip())):
        llist.insert_node(int(input().strip()))
    position = int(input().strip())
    print_singly_linked_list(deleteNode(llist.head, position), ' ', fptr)
    fptr.write('\n')
    fptr.close()
```

**Watch out.** Python frees the bypassed node automatically. In C or C++ you would also have to free its memory.

```stdin
8
20
6
2
19
7
4
15
9
3
```

```stdout
20 6 2 7 4 15 9
```

### Print in Reverse

**Problem.** Print a singly linked list from tail to head.

**Idea.** A singly linked list cannot be walked backwards. Collect the values on the way forward, then print them reversed. This is the iterative form of the recursive "print the rest first, then yourself".

**Steps.**
1. Walk and push the values onto a list; print it reversed.

```python
class SinglyLinkedListNode:
    def __init__(self, node_data):
        self.data = node_data
        self.next = None


class SinglyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def insert_node(self, node_data):
        node = SinglyLinkedListNode(node_data)
        if not self.head:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node


def reversePrint(llist):
    vals = []
    while llist:
        vals.append(llist.data)
        llist = llist.next
    for v in reversed(vals):
        print(v)


if __name__ == '__main__':
    for _ in range(int(input().strip())):
        llist = SinglyLinkedList()
        for _ in range(int(input().strip())):
            llist.insert_node(int(input().strip()))
        reversePrint(llist.head)
```

**Watch out.** The recursive version is elegant but hits Python's recursion limit (about 1000) on long lists; the explicit list does not.

```stdin
3
5
16
12
4
2
5
3
7
3
9
5
5
1
18
3
13
```

```stdout
5
2
4
12
16
9
3
7
13
3
18
1
5
```

### Reverse a linked list

**Problem.** Reverse a singly linked list in place and return the new head.

**Idea.** Walk once, turning each `next` pointer backwards. Keep three references: `prev` (the already reversed part), `cur`, and `nxt` (saved before relinking).

**Steps.**
1. `prev = None`; while `cur`: `nxt = cur.next`, `cur.next = prev`, `prev = cur`, `cur = nxt`.
2. Return `prev`.

```python
import os


class SinglyLinkedListNode:
    def __init__(self, node_data):
        self.data = node_data
        self.next = None


class SinglyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def insert_node(self, node_data):
        node = SinglyLinkedListNode(node_data)
        if not self.head:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node


def print_singly_linked_list(node, sep, fptr):
    while node:
        fptr.write(str(node.data))
        node = node.next
        if node:
            fptr.write(sep)


def reverse(llist):
    prev = None
    cur = llist
    while cur:
        nxt = cur.next
        cur.next = prev
        prev, cur = cur, nxt
    return prev


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    for _ in range(int(input().strip())):
        llist = SinglyLinkedList()
        for _ in range(int(input().strip())):
            llist.insert_node(int(input().strip()))
        print_singly_linked_list(reverse(llist.head), ' ', fptr)
        fptr.write('\n')
    fptr.close()
```

**Watch out.** Save `cur.next` before overwriting it, or you lose the rest of the list. The loop is O(n) time and O(1) extra space.

```stdin
1
5
1
2
3
4
5
```

```stdout
5 4 3 2 1
```

### Compare two linked lists

**Problem.** Print 1 if two lists hold the same values in the same order, else 0.

**Idea.** Walk both lists together. Any mismatch means not equal, and so does one list ending before the other. They are equal only if both run out at the same time.

**Steps.**
1. While both nodes exist: compare and advance.
2. Return `a is None and b is None` (as 1/0).

```python
import os


class SinglyLinkedListNode:
    def __init__(self, node_data):
        self.data = node_data
        self.next = None


class SinglyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def insert_node(self, node_data):
        node = SinglyLinkedListNode(node_data)
        if not self.head:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node


def compare_lists(llist1, llist2):
    a, b = llist1, llist2
    while a and b:
        if a.data != b.data:
            return 0
        a, b = a.next, b.next
    return 1 if a is None and b is None else 0


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    for _ in range(int(input())):
        l1 = SinglyLinkedList()
        for _ in range(int(input())):
            l1.insert_node(int(input()))
        l2 = SinglyLinkedList()
        for _ in range(int(input())):
            l2.insert_node(int(input()))
        fptr.write(str(compare_lists(l1.head, l2.head)) + '\n')
    fptr.close()
```

**Watch out.** A list that is a prefix of the other (`1 2` vs `1 2 3`) must give 0. That is why the length check at the end matters.

```stdin
2
2
1
2
1
1
2
1
2
2
1
2
```

```stdout
0
1
```

### Merge two sorted linked lists

**Problem.** Merge two sorted lists into one sorted list by relinking the nodes.

**Idea.** Use a **dummy head** and a `tail` pointer. Repeatedly attach the smaller front node, then append whatever remains of the other list.

**Steps.**
1. While both lists are non-empty: attach the smaller one and advance it.
2. Attach the leftover; return `dummy.next`.

```python
import os


class SinglyLinkedListNode:
    def __init__(self, node_data):
        self.data = node_data
        self.next = None


class SinglyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def insert_node(self, node_data):
        node = SinglyLinkedListNode(node_data)
        if not self.head:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node


def print_singly_linked_list(node, sep, fptr):
    while node:
        fptr.write(str(node.data))
        node = node.next
        if node:
            fptr.write(sep)


def mergeLists(head1, head2):
    dummy = tail = SinglyLinkedListNode(0)
    a, b = head1, head2
    while a and b:
        if a.data <= b.data:
            tail.next, a = a, a.next
        else:
            tail.next, b = b, b.next
        tail = tail.next
    tail.next = a or b
    return dummy.next


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    for _ in range(int(input())):
        l1 = SinglyLinkedList()
        for _ in range(int(input())):
            l1.insert_node(int(input()))
        l2 = SinglyLinkedList()
        for _ in range(int(input())):
            l2.insert_node(int(input()))
        print_singly_linked_list(mergeLists(l1.head, l2.head), ' ', fptr)
        fptr.write('\n')
    fptr.close()
```

**Watch out.** The dummy node removes the special case of "which list provides the head". Using `<=` keeps equal values in their original order (stable).

```stdin
1
3
1
2
3
2
3
4
```

```stdout
1 2 3 3 4
```

### Get Node Value

**Problem.** Return the value of the node `positionFromTail` places from the end (0 = last node).

**Idea.** **Two pointers with a gap.** Advance a lead pointer `k` steps, then move both pointers until the lead reaches the last node; the trailing pointer is then at the answer. This is one pass with O(1) memory.

**Steps.**
1. `lead` moves `positionFromTail` steps ahead.
2. While `lead.next`: move both. Return `trail.data`.

```python
import os


class SinglyLinkedListNode:
    def __init__(self, node_data):
        self.data = node_data
        self.next = None


class SinglyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def insert_node(self, node_data):
        node = SinglyLinkedListNode(node_data)
        if not self.head:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node


def getNode(llist, positionFromTail):
    lead = trail = llist
    for _ in range(positionFromTail):
        lead = lead.next
    while lead.next:
        lead = lead.next
        trail = trail.next
    return trail.data


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    for _ in range(int(input().strip())):
        llist = SinglyLinkedList()
        for _ in range(int(input().strip())):
            llist.insert_node(int(input().strip()))
        position = int(input().strip())
        fptr.write(str(getNode(llist.head, position)) + '\n')
    fptr.close()
```

**Watch out.** Counting from the tail is 0-based: position 0 is the last node, not the one before it.

```stdin
2
1
1
0
3
3
2
1
2
```

```stdout
1
3
```

### Delete duplicate-value nodes from a sorted linked list

**Problem.** Remove repeated values from a sorted list so that each value appears once.

**Idea.** In a sorted list, duplicates are adjacent. While the next node has the same value, bypass it; otherwise move on.

**Steps.**
1. `cur = head`; while `cur.next`: if equal, `cur.next = cur.next.next`, else `cur = cur.next`.

```python
import os


class SinglyLinkedListNode:
    def __init__(self, node_data):
        self.data = node_data
        self.next = None


class SinglyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def insert_node(self, node_data):
        node = SinglyLinkedListNode(node_data)
        if not self.head:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node


def print_singly_linked_list(node, sep, fptr):
    while node:
        fptr.write(str(node.data))
        node = node.next
        if node:
            fptr.write(sep)


def removeDuplicates(llist):
    cur = llist
    while cur and cur.next:
        if cur.next.data == cur.data:
            cur.next = cur.next.next
        else:
            cur = cur.next
    return llist


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    for _ in range(int(input().strip())):
        llist = SinglyLinkedList()
        for _ in range(int(input().strip())):
            llist.insert_node(int(input().strip()))
        print_singly_linked_list(removeDuplicates(llist.head), ' ', fptr)
        fptr.write('\n')
    fptr.close()
```

**Watch out.** Do not advance `cur` after a deletion: the new `cur.next` may be yet another duplicate (as in `3 3 3`).

```stdin
1
5
1
2
2
3
4
```

```stdout
1 2 3 4
```

### Cycle Detection

**Problem.** Return 1 if the list contains a cycle, else 0.

**Idea.** **Floyd's tortoise and hare.** A slow pointer moves one step and a fast pointer two. If there is a cycle, the fast pointer eventually laps the slow one and they meet. If not, the fast pointer reaches the end. Memory is O(1).

**Steps.**
1. Advance `slow` by 1 and `fast` by 2 while `fast and fast.next`.
2. If they ever point to the same node, return 1; otherwise 0.

```python
import os


class SinglyLinkedListNode:
    def __init__(self, node_data):
        self.data = node_data
        self.next = None


class SinglyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def insert_node(self, node_data):
        node = SinglyLinkedListNode(node_data)
        if not self.head:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node


def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return 1
    return 0


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    for _ in range(int(input())):
        index = int(input())
        count = int(input())
        llist = SinglyLinkedList()
        for _ in range(count):
            llist.insert_node(int(input()))
        extra = SinglyLinkedListNode(-1)
        temp = llist.head
        for i in range(count):
            if i == index:
                extra = temp
            if i != count - 1:
                temp = temp.next
        temp.next = extra                      # index -1 leaves no cycle
        fptr.write(str(int(has_cycle(llist.head))) + '\n')
    fptr.close()
```

**Watch out.** Compare node *identity* (`is`), not values; different nodes may hold equal data. The driver links the tail to node `index`, and `-1` means "no cycle".

```stdin
2
-1
1
1
1
3
1
2
3
```

```stdout
0
1
```

### Find Merge Point of Two Lists

**Problem.** Two lists join at some node and share the tail from there. Return the value of the first shared node.

**Idea.** **Pointer switching.** Walk `a` through list 1 then list 2, and `b` through list 2 then list 1. Both travel `len1 + len2 − shared` steps before reaching the merge node, so they arrive there together. This needs no lengths and no extra memory.

**Steps.**
1. While `a is not b`: `a = a.next or head2`, `b = b.next or head1`.
2. Return `a.data`.

```python
import os


class SinglyLinkedListNode:
    def __init__(self, node_data):
        self.data = node_data
        self.next = None


class SinglyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def insert_node(self, node_data):
        node = SinglyLinkedListNode(node_data)
        if not self.head:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node


def findMergeNode(head1, head2):
    a, b = head1, head2
    while a is not b:
        a = a.next if a.next else head2
        b = b.next if b.next else head1
    return a.data


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    for _ in range(int(input())):
        index = int(input())
        l1 = SinglyLinkedList()
        c1 = int(input())
        for _ in range(c1):
            l1.insert_node(int(input()))
        l2 = SinglyLinkedList()
        c2 = int(input())
        for _ in range(c2):
            l2.insert_node(int(input()))
        ptr1 = l1.head
        for _ in range(index):
            ptr1 = ptr1.next
        l2.tail.next = ptr1                    # join list 2's tail into list 1
        fptr.write(str(findMergeNode(l1.head, l2.head)) + '\n')
    fptr.close()
```

**Watch out.** The lists are guaranteed to merge, so the switching loop always terminates. Without a merge, the `a.next or head` form would cycle forever; a version that must handle that case switches to `None` at the ends instead.

```stdin
2
1
3
1
2
3
1
1
0
2
5
6
1
7
```

```stdout
2
5
```

### Inserting a Node Into a Sorted Doubly Linked List

**Problem.** Insert a value into a sorted doubly linked list, keeping it sorted, and return the head.

**Idea.** Find the first node with a value `≥ data`, then fix four links: `prev.next`, `node.prev`, `node.next` and `next.prev`. Inserting at the head or at the tail are the two edge cases.

**Steps.**
1. If the list is empty or `data ≤ head.data`, the new node becomes the head.
2. Otherwise walk while `cur.next and cur.next.data < data`; splice after `cur`.

```python
import os


class DoublyLinkedListNode:
    def __init__(self, node_data):
        self.data = node_data
        self.next = None
        self.prev = None


class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def insert_node(self, node_data):
        node = DoublyLinkedListNode(node_data)
        if not self.head:
            self.head = node
        else:
            self.tail.next = node
            node.prev = self.tail
        self.tail = node


def print_doubly_linked_list(node, sep, fptr):
    while node:
        fptr.write(str(node.data))
        node = node.next
        if node:
            fptr.write(sep)


def sortedInsert(llist, data):
    node = DoublyLinkedListNode(data)
    if llist is None:
        return node
    if data <= llist.data:
        node.next = llist
        llist.prev = node
        return node
    cur = llist
    while cur.next and cur.next.data < data:
        cur = cur.next
    node.next = cur.next
    node.prev = cur
    if cur.next:
        cur.next.prev = node
    cur.next = node
    return llist


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    for _ in range(int(input().strip())):
        llist = DoublyLinkedList()
        for _ in range(int(input().strip())):
            llist.insert_node(int(input().strip()))
        data = int(input().strip())
        print_doubly_linked_list(sortedInsert(llist.head, data), ' ', fptr)
        fptr.write('\n')
    fptr.close()
```

**Watch out.** Forgetting `cur.next.prev = node` leaves the backward links broken even though forward printing still looks right.

```stdin
1
4
1
3
4
10
5
```

```stdout
1 3 4 5 10
```

### Reverse a doubly linked list

**Problem.** Reverse a doubly linked list and return the new head.

**Idea.** Swap `next` and `prev` on every node. After the swap, the old `prev` (now `next`) is where the walk would go backwards, so continue through the old `next`, saved before the swap. The last node visited is the new head.

**Steps.**
1. For each node: swap its links; remember it as the candidate head; continue with the saved old `next`.

```python
import os


class DoublyLinkedListNode:
    def __init__(self, node_data):
        self.data = node_data
        self.next = None
        self.prev = None


class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def insert_node(self, node_data):
        node = DoublyLinkedListNode(node_data)
        if not self.head:
            self.head = node
        else:
            self.tail.next = node
            node.prev = self.tail
        self.tail = node


def print_doubly_linked_list(node, sep, fptr):
    while node:
        fptr.write(str(node.data))
        node = node.next
        if node:
            fptr.write(sep)


def reverse(llist):
    cur = llist
    head = None
    while cur:
        nxt = cur.next
        cur.next, cur.prev = cur.prev, cur.next
        head = cur
        cur = nxt
    return head


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    for _ in range(int(input().strip())):
        llist = DoublyLinkedList()
        for _ in range(int(input().strip())):
            llist.insert_node(int(input().strip()))
        print_doubly_linked_list(reverse(llist.head), ' ', fptr)
        fptr.write('\n')
    fptr.close()
```

**Watch out.** An empty list returns `None`, and a single node stays as it is; the loop handles both.

```stdin
1
4
1
2
3
4
```

```stdout
4 3 2 1
```
