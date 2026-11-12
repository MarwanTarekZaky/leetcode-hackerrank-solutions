# Graph General

### 200. Number of Islands
difficulty: Medium

**Problem.** A grid of `'1'` (land) and `'0'` (water). Count the islands (groups of land connected up/down/left/right).

**Example.** A grid with three separate land groups → `3`.

**Idea.** Scan every cell. When you find unvisited land, it's a new island: count it, then **flood-fill** (DFS/BFS) the whole island, marking it as water so it's never counted again.

**Steps.**
1. For each cell: if it's `'1'`, `count += 1` and run the flood fill from it.
2. Flood fill: stop if out of bounds or not `'1'`; otherwise set to `'0'` and visit the four neighbours.

```python
class Solution:
    def numIslands(self, grid: List[List[str]]) -> int:
        rows, cols = len(grid), len(grid[0])
        count = 0
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] != '1':
                    continue
                count += 1
                grid[r][c] = '0'
                q = deque([(r, c)])
                while q:
                    x, y = q.popleft()
                    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                        if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] == '1':
                            grid[nx][ny] = '0'
                            q.append((nx, ny))
        return count
```

**Complexity.** Time O(rows·cols), space O(rows·cols) worst case for the queue.

**Watch out.**
- Cells are the **strings** `'1'`/`'0'`, not integers.
- Mark land as water **when you push it**, not when you pop, or the same cell gets queued many times.
- A recursive DFS is shorter but can exceed Python's recursion limit on a big all-land grid; BFS avoids that.

```test
g = [["1","1","1","1","0"],["1","1","0","1","0"],["1","1","0","0","0"],["0","0","0","0","0"]]
assert Solution().numIslands(g) == 1
g = [["1","1","0","0","0"],["1","1","0","0","0"],["0","0","1","0","0"],["0","0","0","1","1"]]
assert Solution().numIslands(g) == 3
```

### 130. Surrounded Regions
difficulty: Medium

**Problem.** Flip every `'O'` region that is completely surrounded by `'X'` into `'X'`. Regions touching the border stay.

**Idea.** Think in reverse: the `'O'`s that survive are exactly those connected to a **border** `'O'`. Flood-fill from every border `'O'` and mark them safe (`'S'`). Then flip all remaining `'O'` to `'X'` and turn `'S'` back to `'O'`.

**Steps.**
1. For each border cell that is `'O'`, BFS and mark connected `'O'`s as `'S'`.
2. Scan the board: `'O'` → `'X'`, `'S'` → `'O'`.

```python
class Solution:
    def solve(self, board: List[List[str]]) -> None:
        m, n = len(board), len(board[0])
        q = deque()
        for r in range(m):
            for c in range(n):
                if (r in (0, m - 1) or c in (0, n - 1)) and board[r][c] == 'O':
                    board[r][c] = 'S'
                    q.append((r, c))
        while q:
            r, c = q.popleft()
            for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= nr < m and 0 <= nc < n and board[nr][nc] == 'O':
                    board[nr][nc] = 'S'
                    q.append((nr, nc))
        for r in range(m):
            for c in range(n):
                if board[r][c] == 'O':
                    board[r][c] = 'X'
                elif board[r][c] == 'S':
                    board[r][c] = 'O'
```

**Complexity.** Time O(m·n), space O(m·n).

**Watch out.** Trying to decide "is this region surrounded?" from the inside is much harder; starting from the border is the trick.

```test
b = [["X","X","X","X"],["X","O","O","X"],["X","X","O","X"],["X","O","X","X"]]
Solution().solve(b); assert b == [["X","X","X","X"],["X","X","X","X"],["X","X","X","X"],["X","O","X","X"]]
b = [["X"]]; Solution().solve(b); assert b == [["X"]]
```

### 133. Clone Graph
difficulty: Medium

**Problem.** Deep-copy a connected undirected graph given one node (each node has `val` and a list of `neighbors`).

**Idea.** DFS/BFS with a dictionary `original → copy`. The dictionary also acts as the visited set and handles cycles: if a node was already copied, reuse its copy.

**Steps.**
1. Empty input → `None`.
2. Copy the start node and store `copies[node] = clone`; put the node in a queue.
3. Pop a node; for each neighbour not yet copied, copy it and queue it.
4. Append the neighbour's copy to the current node's copy's neighbour list.
5. Return `copies[node]`.

```python
class Solution:
    def cloneGraph(self, node: Optional['Node']) -> Optional['Node']:
        if not node:
            return None
        copies = {node: Node(node.val)}
        q = deque([node])
        while q:
            cur = q.popleft()
            for nb in cur.neighbors:
                if nb not in copies:
                    copies[nb] = Node(nb.val)
                    q.append(nb)
                copies[cur].neighbors.append(copies[nb])
        return copies[node]
```

**Complexity.** Time O(V + E), space O(V).

**Watch out.** Create the copy **when first seen**, before queueing, so every edge links to a single copy per node.

```test
a, b, c, d = Node(1), Node(2), Node(3), Node(4)
a.neighbors = [b, d]; b.neighbors = [a, c]; c.neighbors = [b, d]; d.neighbors = [a, c]
cp = Solution().cloneGraph(a)
assert cp is not a and cp.val == 1 and [x.val for x in cp.neighbors] == [2, 4]
assert cp.neighbors[0].neighbors[0] is cp
assert Solution().cloneGraph(None) is None
```

### 399. Evaluate Division
difficulty: Medium

**Problem.** Given equations like `a / b = 2.0`, answer queries `x / y` (return -1.0 if it can't be determined).

**Example.** `a/b = 2, b/c = 3` → `a/c = 6`, `b/a = 0.5`, `a/e = -1`.

**Idea.** Build a weighted graph: edge `a → b` with weight 2 and `b → a` with weight 1/2. A query `x / y` is the **product of the weights along any path** from `x` to `y`. Use BFS from `x`.

**Steps.**
1. Graph: for each equation `(a, b, v)`, add `a→b (v)` and `b→a (1/v)`.
2. For each query: if either variable is unknown, -1. Else BFS from `x` carrying the product; return it when you reach `y`.

```python
class Solution:
    def calcEquation(self, equations: List[List[str]], values: List[float], queries: List[List[str]]) -> List[float]:
        graph = defaultdict(dict)
        for (a, b), v in zip(equations, values):
            graph[a][b] = v
            graph[b][a] = 1 / v

        def query(x, y):
            if x not in graph or y not in graph:
                return -1.0
            q = deque([(x, 1.0)])
            seen = {x}
            while q:
                node, prod = q.popleft()
                if node == y:
                    return prod
                for nb, w in graph[node].items():
                    if nb not in seen:
                        seen.add(nb)
                        q.append((nb, prod * w))
            return -1.0

        return [query(x, y) for x, y in queries]
```

**Complexity.** Each query O(V + E); total O(Q·(V + E)).

**Watch out.** `x / x` is 1.0 only if `x` appears in the equations; an unknown variable divided by itself is -1.0. Advanced alternative: weighted union-find.

```test
r = Solution().calcEquation([["a","b"],["b","c"]], [2.0,3.0], [["a","c"],["b","a"],["a","e"],["a","a"],["x","x"]])
assert [round(v, 5) for v in r] == [6.0, 0.5, -1.0, 1.0, -1.0]
```

### 207. Course Schedule
difficulty: Medium

**Problem.** `numCourses` courses and pairs `[a, b]` meaning "take `b` before `a`". Can you finish all courses?

**Idea.** You can finish everything exactly when the prerequisite graph has **no cycle**. Kahn's algorithm (topological sort with BFS): repeatedly take courses with no remaining prerequisites (in-degree 0). If you manage to take all of them, there's no cycle.

**Steps.**
1. Build `graph[b].append(a)` and count `indeg[a]`.
2. Queue all courses with in-degree 0.
3. Pop a course, count it, decrease the in-degree of courses that depend on it; queue those that reach 0.
4. Return `taken == numCourses`.

```python
class Solution:
    def canFinish(self, numCourses: int, prerequisites: List[List[int]]) -> bool:
        graph = [[] for _ in range(numCourses)]
        indeg = [0] * numCourses
        for a, b in prerequisites:
            graph[b].append(a)
            indeg[a] += 1
        q = deque(i for i in range(numCourses) if indeg[i] == 0)
        taken = 0
        while q:
            c = q.popleft()
            taken += 1
            for nxt in graph[c]:
                indeg[nxt] -= 1
                if indeg[nxt] == 0:
                    q.append(nxt)
        return taken == numCourses
```

**Complexity.** Time O(V + E), space O(V + E).

**Watch out.** Courses in a cycle never reach in-degree 0, so they're never taken. DFS alternative: three colours (unvisited, visiting, done); reaching a "visiting" node means a cycle.

```test
assert Solution().canFinish(2, [[1,0]]) is True
assert Solution().canFinish(2, [[1,0],[0,1]]) is False
assert Solution().canFinish(3, []) is True
```

### 210. Course Schedule II
difficulty: Medium

**Problem.** Same as #207, but return **an order** in which to take all courses, or `[]` if impossible.

**Idea.** Kahn's algorithm again; the order in which courses are popped **is** a valid topological order.

**Steps.**
1. Build the graph `b → a` for each `[a, b]` and count incoming edges (`indeg`).
2. Queue every course with `indeg == 0` (no prerequisites).
3. Pop a course, add it to `order`, and decrease the indegree of the courses that depend on it; queue any that reach 0.
4. If `order` has all the courses, return it; otherwise there's a cycle → `[]`.

```python
class Solution:
    def findOrder(self, numCourses: int, prerequisites: List[List[int]]) -> List[int]:
        graph = [[] for _ in range(numCourses)]
        indeg = [0] * numCourses
        for a, b in prerequisites:
            graph[b].append(a)
            indeg[a] += 1
        q = deque(i for i in range(numCourses) if indeg[i] == 0)
        order = []
        while q:
            c = q.popleft()
            order.append(c)
            for nxt in graph[c]:
                indeg[nxt] -= 1
                if indeg[nxt] == 0:
                    q.append(nxt)
        return order if len(order) == numCourses else []
```

**Complexity.** Time O(V + E), space O(V + E).

**Watch out.** Return `[]` when some courses were never popped (a cycle).

```test
def ok(n, pre, order):
    pos = {c: i for i, c in enumerate(order)}
    return len(order) == n and all(pos[b] < pos[a] for a, b in pre)
assert ok(4, [[1,0],[2,0],[3,1],[3,2]], Solution().findOrder(4, [[1,0],[2,0],[3,1],[3,2]]))
assert Solution().findOrder(2, [[0,1],[1,0]]) == []
assert Solution().findOrder(1, []) == [0]
```

# Graph BFS

### 909. Snakes and Ladders
difficulty: Medium

**Problem.** An `n × n` board numbered 1..n² boustrophedon-style from the bottom-left (rows alternate direction). From square `s`, a roll moves to `s+1 .. s+6`; if that square has a snake or ladder (`board[r][c] != -1`), you must move to its destination (only once per roll). Return the fewest rolls to reach n², or -1.

**Idea.** Shortest path in an unweighted graph → **BFS**. Each square is a node; each roll is an edge of cost 1. The tricky part is converting a square label to `(row, col)`.

**Steps.**
1. `value_at(s)`: `row_from_bottom, offset = divmod(s - 1, n)`; `r = n - 1 - row_from_bottom`; `c = offset` on even rows from the bottom, `n - 1 - offset` on odd rows.
2. BFS from `(1, 0 rolls)`. For each `nxt` in `s+1 .. min(s+6, n²)`: `dest = value_at(nxt)` if it isn't -1, else `nxt`. If `dest == n²`, return `rolls + 1`. If unseen, mark and queue it.
3. Queue empty → -1.

```python
class Solution:
    def snakesAndLadders(self, board: List[List[int]]) -> int:
        n = len(board)
        target = n * n

        def value_at(s):
            row_from_bottom, offset = divmod(s - 1, n)
            r = n - 1 - row_from_bottom
            c = offset if row_from_bottom % 2 == 0 else n - 1 - offset
            return board[r][c]

        seen = {1}
        q = deque([(1, 0)])
        while q:
            s, rolls = q.popleft()
            for nxt in range(s + 1, min(s + 6, target) + 1):
                dest = value_at(nxt)
                if dest == -1:
                    dest = nxt
                if dest == target:
                    return rolls + 1
                if dest not in seen:
                    seen.add(dest)
                    q.append((dest, rolls + 1))
        return -1
```

**Complexity.** Time O(n²), space O(n²).

**Watch out.**
- Store the square you **end up on** after the snake/ladder in `seen`, not the rolled square.
- Never follow a second snake/ladder from a destination.
- `n == 1` can't happen (n ≥ 2), so the start is never the target.

```test
b = [[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1],[-1,35,-1,-1,13,-1],[-1,-1,-1,-1,-1,-1],[-1,15,-1,-1,-1,-1]]
assert Solution().snakesAndLadders(b) == 4
assert Solution().snakesAndLadders([[-1,-1],[-1,3]]) == 1
```

### 433. Minimum Genetic Mutation
difficulty: Medium

**Problem.** Genes are 8-character strings of `A C G T`. One mutation changes one character, and every intermediate gene must be in `bank`. Return the minimum mutations from `startGene` to `endGene`, or -1.

**Idea.** BFS over genes: neighbours are all strings that differ in one position and are in the bank.

**Steps.**
1. `bank = set(bank)`; if `endGene` not in it, return -1.
2. BFS from `(startGene, 0)`; for each position and each of `ACGT`, build the mutated gene; if it's in the bank and unseen, queue it.

```python
class Solution:
    def minMutation(self, startGene: str, endGene: str, bank: List[str]) -> int:
        bank = set(bank)
        if endGene not in bank:
            return -1
        q = deque([(startGene, 0)])
        seen = {startGene}
        while q:
            gene, steps = q.popleft()
            if gene == endGene:
                return steps
            for i in range(len(gene)):
                for ch in 'ACGT':
                    nxt = gene[:i] + ch + gene[i + 1:]
                    if nxt in bank and nxt not in seen:
                        seen.add(nxt)
                        q.append((nxt, steps + 1))
        return -1
```

**Complexity.** Time O(B · 8 · 4) for a bank of size B, space O(B).

**Watch out.** The start gene doesn't need to be in the bank. This is a small version of Word Ladder (#127).

```test
assert Solution().minMutation("AACCGGTT", "AACCGGTA", ["AACCGGTA"]) == 1
assert Solution().minMutation("AACCGGTT", "AAACGGTA", ["AACCGGTA","AACCGCTA","AAACGGTA"]) == 2
assert Solution().minMutation("AAAAAAAA", "CCCCCCCC", []) == -1
```

### 127. Word Ladder
difficulty: Hard

**Problem.** Transform `beginWord` into `endWord`, changing one letter at a time, every intermediate word in `wordList`. Return the number of words in the shortest sequence (including both ends), or 0.

**Example.** `hit → hot → dot → dog → cog` → `5`.

**Idea.** BFS where neighbours are words one letter apart. Generate neighbours by trying all 26 letters at each position and checking a set (faster than comparing against every word). Remove words from the set when visited.

**Steps.**
1. `words = set(wordList)`; if `endWord` not in it, return 0.
2. BFS from `(beginWord, 1)`; for each position and letter, build `nxt`; if in `words`, remove it and queue `(nxt, steps + 1)`.

```python
class Solution:
    def ladderLength(self, beginWord: str, endWord: str, wordList: List[str]) -> int:
        words = set(wordList)
        if endWord not in words:
            return 0
        q = deque([(beginWord, 1)])
        while q:
            word, steps = q.popleft()
            if word == endWord:
                return steps
            for i in range(len(word)):
                for ch in 'abcdefghijklmnopqrstuvwxyz':
                    nxt = word[:i] + ch + word[i + 1:]
                    if nxt in words:
                        words.remove(nxt)
                        q.append((nxt, steps + 1))
        return 0
```

**Complexity.** Time O(N · L · 26) for N words of length L, space O(N).

**Watch out.** Removing a word from the set when it's queued is the "visited" marking. Faster in practice: bidirectional BFS from both ends.

```test
assert Solution().ladderLength("hit", "cog", ["hot","dot","dog","lot","log","cog"]) == 5
assert Solution().ladderLength("hit", "cog", ["hot","dot","dog","lot","log"]) == 0
```

# Trie

### 208. Implement Trie (Prefix Tree)
difficulty: Medium

**Problem.** Implement `insert(word)`, `search(word)` (whole word stored?) and `startsWith(prefix)`.

**Idea.** Each node is a dictionary `char → child node`, plus a flag marking the end of a word. Walking a word follows one character per level.

**Steps.**
1. Each node has a `children` dict and an `is_end` flag.
2. `insert`: walk the word from the root, creating missing children, and set `is_end` on the last node.
3. `_walk(s)`: follow the characters; return the final node, or `None` if a character is missing.
4. `search`: the walk must succeed **and** end on a node with `is_end`.
5. `startsWith`: the walk only needs to succeed.

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.is_end = True

    def _walk(self, s):
        node = self.root
        for ch in s:
            node = node.children.get(ch)
            if node is None:
                return None
        return node

    def search(self, word: str) -> bool:
        node = self._walk(word)
        return node is not None and node.is_end

    def startsWith(self, prefix: str) -> bool:
        return self._walk(prefix) is not None
```

**Complexity.** O(L) per operation for a word of length L.

**Watch out.** `search("app")` after only inserting `"apple"` must be false; that's what `is_end` is for.

```test
t = Trie(); t.insert("apple")
assert t.search("apple") and not t.search("app") and t.startsWith("app")
t.insert("app"); assert t.search("app")
```

### 211. Design Add and Search Words Data Structure
difficulty: Medium

**Problem.** `addWord(word)` and `search(word)`, where the search pattern may contain `.` matching any letter.

**Idea.** A trie (like #208). For `.`, try **every** child recursively (DFS); for a normal letter, follow that child only.

**Steps.**
1. `addWord`: insert like a trie, marking the end with the key `'$'`.
2. `search` runs `dfs(node, i)` over the characters.
3. If `i == len(word)`, the word matches when `'$'` is in the node.
4. A normal letter: follow that child, if it exists.
5. A `.`: try every child (except `'$'`); return `True` if any of them matches the rest.

```python
class WordDictionary:
    def __init__(self):
        self.root = {}

    def addWord(self, word: str) -> None:
        node = self.root
        for ch in word:
            node = node.setdefault(ch, {})
        node['$'] = True                 # end-of-word marker

    def search(self, word: str) -> bool:
        def dfs(node, i):
            if i == len(word):
                return '$' in node
            ch = word[i]
            if ch == '.':
                return any(dfs(child, i + 1) for key, child in node.items() if key != '$')
            return ch in node and dfs(node[ch], i + 1)
        return dfs(self.root, 0)
```

**Complexity.** Add O(L). Search O(L) without dots, up to O(26^dots · L) with dots.

**Watch out.** When iterating children for `.`, skip the `'$'` marker key (it isn't a child).

```test
w = WordDictionary(); w.addWord("bad"); w.addWord("dad"); w.addWord("mad")
assert not w.search("pad") and w.search("bad") and w.search(".ad") and w.search("b..") and not w.search("b.")
```

### 212. Word Search II
difficulty: Hard

**Problem.** Find all words from a list that can be formed on a letter grid by moving between adjacent cells (no cell reused in one word).

**Idea.** Put all words in a trie, then DFS from every cell, walking the grid and the trie **together**. A path stops as soon as the trie has no matching child, which prunes most of the search. Store the full word at its last trie node to collect it directly.

**Steps.**
1. Build the trie; at each word's end store `node['$'] = word`.
2. DFS(r, c, node): get the child for `board[r][c]`; if none, stop. If it has a word, record it and remove the marker (avoid duplicates). Mark the cell, explore 4 neighbours, restore the cell.
3. Optional pruning: delete empty trie nodes after use.

```python
class Solution:
    def findWords(self, board: List[List[str]], words: List[str]) -> List[str]:
        trie = {}
        for w in words:
            node = trie
            for ch in w:
                node = node.setdefault(ch, {})
            node['$'] = w

        m, n = len(board), len(board[0])
        found = []

        def dfs(r, c, parent):
            ch = board[r][c]
            node = parent[ch]
            if '$' in node:
                found.append(node.pop('$'))
            board[r][c] = '#'
            for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= nr < m and 0 <= nc < n and board[nr][nc] in node:
                    dfs(nr, nc, node)
            board[r][c] = ch
            if not node:                 # prune exhausted branches
                parent.pop(ch)

        for r in range(m):
            for c in range(n):
                if board[r][c] in trie:
                    dfs(r, c, trie)
        return found
```

**Complexity.** Roughly O(m·n·4·3^(L-1)) in the worst case for max word length L; pruning makes it much faster in practice.

**Watch out.** `'#'` marks the cell as used in the current path; restoring it after the recursion is the backtracking step. Popping `'$'` prevents adding the same word twice.

```test
b = [["o","a","a","n"],["e","t","a","e"],["i","h","k","r"],["i","f","l","v"]]
assert sorted(Solution().findWords(b, ["oath","pea","eat","rain"])) == ["eat","oath"]
assert Solution().findWords([["a","b"],["c","d"]], ["abcb"]) == []
```

# Backtracking

### 17. Letter Combinations of a Phone Number
difficulty: Medium

**Problem.** Given digits 2–9, return all letter combinations they could represent on a phone keypad.

**Example.** `"23"` → `["ad","ae","af","bd","be","bf","cd","ce","cf"]`.

**Idea.** Backtracking: choose one letter for each digit, position by position.

**Steps.**
1. Empty input → `[]`.
2. Map each digit to its letters.
3. `backtrack(i, path)`: if `i == len(digits)`, save the joined `path`.
4. Otherwise, for each letter of `digits[i]`: add it, recurse with `i + 1`, then remove it.

```python
class Solution:
    def letterCombinations(self, digits: str) -> List[str]:
        if not digits:
            return []
        keys = {'2': 'abc', '3': 'def', '4': 'ghi', '5': 'jkl',
                '6': 'mno', '7': 'pqrs', '8': 'tuv', '9': 'wxyz'}
        res = []

        def backtrack(i, path):
            if i == len(digits):
                res.append(''.join(path))
                return
            for ch in keys[digits[i]]:
                path.append(ch)
                backtrack(i + 1, path)
                path.pop()

        backtrack(0, [])
        return res
```

**Complexity.** O(4ⁿ · n).

**Watch out.** Empty input must return `[]`, not `[""]`. One-liner: `[''.join(p) for p in itertools.product(*(keys[d] for d in digits))]`.

```test
assert Solution().letterCombinations("23") == ["ad","ae","af","bd","be","bf","cd","ce","cf"]
assert Solution().letterCombinations("") == []
assert Solution().letterCombinations("2") == ["a","b","c"]
```

### 77. Combinations
difficulty: Medium

**Problem.** Return all combinations of `k` numbers chosen from `1..n`.

**Example.** `n = 4, k = 2` → `[[1,2],[1,3],[1,4],[2,3],[2,4],[3,4]]`.

**Idea.** Build each combination in increasing order: after picking `num`, the next pick starts at `num + 1`. That makes `[1,2]` and `[2,1]` the same and only one is produced. Prune when there aren't enough numbers left.

**Steps.**
1. `backtrack(start)`: if the path has `k` numbers, save a copy.
2. `need = k - len(path)`; try `num` from `start` to `n - need + 1`.
3. Append → recurse with `num + 1` → pop.

```python
class Solution:
    def combine(self, n: int, k: int) -> List[List[int]]:
        res, path = [], []

        def backtrack(start):
            if len(path) == k:
                res.append(path[:])
                return
            need = k - len(path)
            for num in range(start, n - need + 2):
                path.append(num)
                backtrack(num + 1)
                path.pop()

        backtrack(1)
        return res
```

**Complexity.** O(k · C(n, k)).

**Watch out.**
- `path[:]` saves a **copy**; appending `path` itself would leave every saved entry empty at the end.
- `n - need + 2` = (largest useful first number `n - need + 1`) + 1 because `range` excludes its end.

```test
assert Solution().combine(4, 2) == [[1,2],[1,3],[1,4],[2,3],[2,4],[3,4]]
assert Solution().combine(1, 1) == [[1]]
assert len(Solution().combine(9, 3)) == 84
```

### 46. Permutations
difficulty: Medium

**Problem.** Return all permutations of distinct integers.

**Example.** `[1,2,3]` → 6 orderings.

**Idea.** Backtracking with a `used` array: at each position, try every number not used yet.

**Steps.**
1. Keep `path` (the permutation being built) and `used` flags.
2. When `path` has all the numbers, save a copy.
3. Otherwise try every number not used yet: mark it, add it, recurse.
4. After returning, remove it and unmark it so other choices can use it.

```python
class Solution:
    def permute(self, nums: List[int]) -> List[List[int]]:
        res, path = [], []
        used = [False] * len(nums)

        def backtrack():
            if len(path) == len(nums):
                res.append(path[:])
                return
            for i, x in enumerate(nums):
                if not used[i]:
                    used[i] = True
                    path.append(x)
                    backtrack()
                    path.pop()
                    used[i] = False

        backtrack()
        return res
```

**Complexity.** O(n · n!).

**Watch out.** Unlike combinations, every position may use any unused number (order matters), so there's no `start` index.

```test
assert sorted(Solution().permute([1,2,3])) == [[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]
assert Solution().permute([1]) == [[1]]
```

### 39. Combination Sum
difficulty: Medium

**Problem.** Distinct positive `candidates`; return all unique combinations that sum to `target`. A number may be used **unlimited times**.

**Example.** `[2,3,6,7], 7` → `[[2,2,3],[7]]`.

**Idea.** Backtracking with a `start` index (to avoid permutations of the same combination). Since reuse is allowed, recurse with the **same** index `i`, not `i + 1`. Sort so you can stop when a candidate exceeds the remainder.

**Steps.**
1. Sort the candidates so the loop can stop early.
2. `backtrack(start, remaining)`: if `remaining == 0`, save a copy of `path`.
3. Try each candidate from index `start`; if it's bigger than `remaining`, stop (all the next ones are bigger too).
4. Add it and recurse with the **same** index `i` (it can be reused), then remove it.
5. Starting from `start` (never earlier) avoids the same combination in a different order.

```python
class Solution:
    def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
        candidates.sort()
        res, path = [], []

        def backtrack(start, remaining):
            if remaining == 0:
                res.append(path[:])
                return
            for i in range(start, len(candidates)):
                c = candidates[i]
                if c > remaining:
                    break
                path.append(c)
                backtrack(i, remaining - c)
                path.pop()

        backtrack(0, target)
        return res
```

**Complexity.** Exponential; roughly O(N^(T/M)) where T is the target and M the smallest candidate.

**Watch out.** `i` (not `i + 1`) allows reuse; `start` prevents `[3,2,2]` duplicating `[2,2,3]`.

```test
assert Solution().combinationSum([2,3,6,7], 7) == [[2,2,3],[7]]
assert Solution().combinationSum([2,3,5], 8) == [[2,2,2,2],[2,3,3],[3,5]]
assert Solution().combinationSum([2], 1) == []
```

### 52. N-Queens II
difficulty: Hard

**Problem.** Count the ways to place `n` queens on an `n × n` board so none attack each other.

**Idea.** Place one queen per row. A square `(r, c)` is attacked if its column, its `r - c` diagonal, or its `r + c` anti-diagonal is already taken. Keep three sets and backtrack row by row.

**Steps.**
1. Place queens row by row, starting at row 0.
2. For each column `c` in row `r`, skip it if `c`, `r - c` (diagonal) or `r + c` (anti-diagonal) is already taken.
3. Otherwise mark the three sets, count the solutions for row `r + 1`, then unmark.
4. When `r == n`, all queens are placed: that's one solution.

```python
class Solution:
    def totalNQueens(self, n: int) -> int:
        cols, diag, anti = set(), set(), set()

        def place(r):
            if r == n:
                return 1
            count = 0
            for c in range(n):
                if c in cols or r - c in diag or r + c in anti:
                    continue
                cols.add(c); diag.add(r - c); anti.add(r + c)
                count += place(r + 1)
                cols.remove(c); diag.remove(r - c); anti.remove(r + c)
            return count

        return place(0)
```

**Complexity.** O(n!) roughly; fine for n ≤ 9.

**Watch out.** All squares on one diagonal share `r - c`; on one anti-diagonal they share `r + c`. That's what makes the check O(1).

```test
assert Solution().totalNQueens(4) == 2
assert Solution().totalNQueens(1) == 1
assert Solution().totalNQueens(8) == 92
```

### 22. Generate Parentheses
difficulty: Medium

**Problem.** Return all valid strings of `n` pairs of parentheses.

**Example.** `n = 3` → `["((()))","(()())","(())()","()(())","()()()"]`.

**Idea.** Build the string character by character. You may add `(` while fewer than `n` are open, and `)` only while there are more opens than closes. Following these two rules always produces valid strings.

**Steps.**
1. Build the string one character at a time, tracking `opened` and `closed` counts.
2. If `opened < n`, add `(`, recurse, remove it.
3. If `closed < opened`, add `)`, recurse, remove it.
4. When the length is `2n`, the string is valid: save it.

```python
class Solution:
    def generateParenthesis(self, n: int) -> List[str]:
        res = []

        def backtrack(path, opened, closed):
            if len(path) == 2 * n:
                res.append(''.join(path))
                return
            if opened < n:
                path.append('(')
                backtrack(path, opened + 1, closed)
                path.pop()
            if closed < opened:
                path.append(')')
                backtrack(path, opened, closed + 1)
                path.pop()

        backtrack([], 0, 0)
        return res
```

**Complexity.** O(4ⁿ / √n) (the Catalan number of results).

**Watch out.** The rule `closed < opened` is what prevents invalid strings like `())(`.

```test
assert Solution().generateParenthesis(3) == ["((()))","(()())","(())()","()(())","()()()"]
assert Solution().generateParenthesis(1) == ["()"]
```

### 79. Word Search
difficulty: Medium

**Problem.** Can `word` be formed on the grid by moving between adjacent cells, using each cell at most once?

**Idea.** DFS from every cell matching the first letter. Mark the cell as used during the path and restore it when backtracking.

**Steps.**
1. `dfs(r, c, i)`: if `i == len(word)`, return true. Fail if out of bounds or `board[r][c] != word[i]`.
2. Mark the cell `'#'`, try the 4 neighbours with `i + 1`, restore the cell.

```python
class Solution:
    def exist(self, board: List[List[str]], word: str) -> bool:
        m, n = len(board), len(board[0])

        def dfs(r, c, i):
            if i == len(word):
                return True
            if not (0 <= r < m and 0 <= c < n) or board[r][c] != word[i]:
                return False
            ch, board[r][c] = board[r][c], '#'
            found = (dfs(r + 1, c, i + 1) or dfs(r - 1, c, i + 1) or
                     dfs(r, c + 1, i + 1) or dfs(r, c - 1, i + 1))
            board[r][c] = ch
            return found

        return any(dfs(r, c, 0) for r in range(m) for c in range(n))
```

**Complexity.** O(m·n·3^L) for word length L.

**Watch out.** Always restore the cell, even when the path succeeds, so the board is left unchanged. Pruning trick: if the board doesn't contain enough of each letter (`Counter`), return false immediately.

```test
b = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]]
assert Solution().exist([r[:] for r in b], "ABCCED") is True
assert Solution().exist([r[:] for r in b], "SEE") is True
assert Solution().exist([r[:] for r in b], "ABCB") is False
```

# Divide & Conquer

### 108. Convert Sorted Array to Binary Search Tree
difficulty: Easy

**Problem.** Turn a sorted array into a **height-balanced** BST.

**Idea.** The middle element becomes the root (smaller values to its left, larger to its right); repeat on each half. Halves differ in size by at most 1, so the tree is balanced.

**Steps.**
1. `build(l, r)` builds a tree from `nums[l..r]`; if `l > r`, return `None`.
2. Take the middle index `mid` as the root.
3. Build the left subtree from `l .. mid - 1` and the right from `mid + 1 .. r`.
4. The halves differ by at most one element, so the tree is balanced. Return the root.

```python
class Solution:
    def sortedArrayToBST(self, nums: List[int]) -> Optional[TreeNode]:
        def build(l, r):
            if l > r:
                return None
            mid = (l + r) // 2
            node = TreeNode(nums[mid])
            node.left = build(l, mid - 1)
            node.right = build(mid + 1, r)
            return node
        return build(0, len(nums) - 1)
```

**Complexity.** Time O(n), space O(log n) recursion.

**Watch out.** Pass indexes instead of slicing (slices copy and make it O(n log n)). Several answers are valid (lower or upper middle).

```test
def check(root, lo=float('-inf'), hi=float('inf')):
    if not root: return 0
    assert lo < root.val < hi
    a, b = check(root.left, lo, root.val), check(root.right, root.val, hi)
    assert abs(a - b) <= 1
    return 1 + max(a, b)
r = Solution().sortedArrayToBST([-10,-3,0,5,9]); check(r)
assert tree_to_list(r)[0] == 0
```

### 148. Sort List
difficulty: Medium

**Problem.** Sort a linked list in O(n log n) time.

**Idea.** **Merge sort** fits linked lists well: split in the middle with slow/fast pointers, sort each half recursively, merge the sorted halves (like #21).

**Steps.**
1. Base case: empty or single node.
2. Find the middle (`slow` stops at the end of the first half), cut the list.
3. Sort both halves, merge them.

```python
class Solution:
    def sortList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        if not head or not head.next:
            return head
        slow, fast = head, head.next
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
        second = slow.next
        slow.next = None
        left = self.sortList(head)
        right = self.sortList(second)
        dummy = tail = ListNode()
        while left and right:
            if left.val <= right.val:
                tail.next, left = left, left.next
            else:
                tail.next, right = right, right.next
            tail = tail.next
        tail.next = left or right
        return dummy.next
```

**Complexity.** Time O(n log n), space O(log n) recursion.

**Watch out.** Start `fast = head.next` so that for two nodes the split is 1 + 1 (with `fast = head`, a 2-node list never splits and recursion never ends). True O(1)-space version: bottom-up merge sort.

```test
assert to_list(Solution().sortList(build_list([4,2,1,3]))) == [1,2,3,4]
assert to_list(Solution().sortList(build_list([-1,5,3,4,0]))) == [-1,0,3,4,5]
assert to_list(Solution().sortList(None)) == []
```

### 427. Construct Quad Tree
difficulty: Medium

**Problem.** Build a quad tree from an `n × n` 0/1 grid: a node is a **leaf** if its whole square has one value; otherwise it has four children (top-left, top-right, bottom-left, bottom-right) for the four quarters.

**Idea.** Divide and conquer: build the four quarters recursively. If all four children are leaves with the same value, merge them into one leaf; otherwise return an internal node.

**Steps.**
1. `build(r, c, size)` handles the square with top-left `(r, c)`.
2. If `size == 1`, return a leaf with that cell's value.
3. Otherwise build the four quarters of size `size // 2`.
4. If all four are leaves with the same value, merge them into one leaf.
5. Otherwise return an internal node with the four children.

```python
class QNode:
    def __init__(self, val, isLeaf, topLeft=None, topRight=None, bottomLeft=None, bottomRight=None):
        self.val = val
        self.isLeaf = isLeaf
        self.topLeft = topLeft
        self.topRight = topRight
        self.bottomLeft = bottomLeft
        self.bottomRight = bottomRight

class Solution:
    def construct(self, grid: List[List[int]]) -> 'QNode':
        def build(r, c, size):
            if size == 1:
                return QNode(grid[r][c] == 1, True)
            h = size // 2
            tl = build(r, c, h)
            tr = build(r, c + h, h)
            bl = build(r + h, c, h)
            br = build(r + h, c + h, h)
            kids = (tl, tr, bl, br)
            if all(k.isLeaf for k in kids) and len({k.val for k in kids}) == 1:
                return QNode(tl.val, True)
            return QNode(True, False, tl, tr, bl, br)
        return build(0, 0, len(grid))
```

**Complexity.** Time O(n²), space O(log n) recursion (plus the tree).

**Watch out.** On LeetCode the class is called `Node`; it's renamed `QNode` here only to keep this page self-contained. For internal nodes `val` can be anything (use `True`).

```test
r = Solution().construct([[0,1],[1,0]])
assert not r.isLeaf and [r.topLeft.val, r.topRight.val, r.bottomLeft.val, r.bottomRight.val] == [False, True, True, False]
r = Solution().construct([[1,1],[1,1]]); assert r.isLeaf and r.val is True
```

### 23. Merge k Sorted Lists
difficulty: Hard

**Problem.** Merge `k` sorted linked lists into one sorted list.

**Idea.** A min-heap holds the current front node of each list. Pop the smallest, attach it, and push that node's `next`. The heap never has more than `k` entries.

**Steps.**
1. Push `(node.val, i, node)` for each non-empty list (`i` breaks ties, because nodes can't be compared).
2. Pop the smallest, attach, push its successor.

```python
class Solution:
    def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:
        heap = [(node.val, i, node) for i, node in enumerate(lists) if node]
        heapq.heapify(heap)
        dummy = tail = ListNode()
        while heap:
            val, i, node = heapq.heappop(heap)
            tail.next = node
            tail = node
            if node.next:
                heapq.heappush(heap, (node.next.val, i, node.next))
        return dummy.next
```

**Complexity.** Time O(N log k) for N total nodes, space O(k).

**Watch out.** Without the index `i` in the tuple, two equal values would make Python compare `ListNode` objects and crash. Divide-and-conquer alternative: merge lists in pairs (like merge sort), also O(N log k).

```test
r = Solution().mergeKLists([build_list([1,4,5]), build_list([1,3,4]), build_list([2,6])])
assert to_list(r) == [1,1,2,3,4,4,5,6]
assert to_list(Solution().mergeKLists([])) == []
assert to_list(Solution().mergeKLists([None])) == []
```

# Kadane's Algorithm

### 53. Maximum Subarray
difficulty: Medium

**Problem.** Return the largest sum of a non-empty contiguous subarray.

**Example.** `[-2,1,-3,4,-1,2,1,-5,4]` → `6` (`[4,-1,2,1]`).

**Idea: Kadane.** `cur` = best sum of a subarray **ending here**. At each number either extend (`cur + x`) or start fresh (`x`); a negative running sum only hurts, so starting fresh wins then. Track the overall best.

**Steps.**
1. Start `cur` and `best` at `nums[0]`.
2. For each next number `x`, `cur = max(x, cur + x)`: extend the current subarray, or start fresh at `x` if the old sum only hurts.
3. Update `best = max(best, cur)`.
4. Return `best`. Starting from `nums[0]` handles arrays that are all negative.

```python
class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        cur = best = nums[0]
        for x in nums[1:]:
            cur = max(x, cur + x)
            best = max(best, cur)
        return best
```

**Complexity.** Time O(n), space O(1).

**Watch out.**
- Start with `nums[0]`, not 0: an all-negative array must return its largest element.
- To return the indexes too: keep `temp_start` (reset to `i` when restarting) and copy it into `start, end` whenever `best` improves.
- Divide-and-conquer follow-up: best = max(left half, right half, best crossing the middle), O(n log n).

```test
assert Solution().maxSubArray([-2,1,-3,4,-1,2,1,-5,4]) == 6
assert Solution().maxSubArray([1]) == 1
assert Solution().maxSubArray([5,4,-1,7,8]) == 23
assert Solution().maxSubArray([-3,-1,-2]) == -1
```

### 918. Maximum Sum Circular Subarray
difficulty: Medium

**Problem.** Like #53, but the array is circular (a subarray may wrap from the end to the start; each element used at most once).

**Example.** `[5,-3,5]` → `10` (wraps: `5 + 5`).

**Idea.** The best subarray either doesn't wrap (normal Kadane max) or wraps. A wrapping subarray = the whole array **minus** a middle subarray, so it's best when that middle part is the **minimum** subarray: `total - min_sub`. Answer = `max(max_sub, total - min_sub)`, except when all numbers are negative (then `total - min_sub` would be an empty subarray, so return `max_sub`).

**Steps.**
1. In one pass keep: `total` (sum of all numbers), Kadane's best **maximum** subarray, and Kadane's best **minimum** subarray.
2. Max side: `cur_max = max(x, cur_max + x)`, `best_max = max(best_max, cur_max)`.
3. Min side: `cur_min = min(x, cur_min + x)`, `best_min = min(best_min, cur_min)`.
4. If `best_max < 0`, every number is negative: return `best_max` (the wrap formula would mean an empty subarray).
5. Otherwise return `max(best_max, total - best_min)`: the best non-wrapping vs the best wrapping subarray.

```python
class Solution:
    def maxSubarraySumCircular(self, nums: List[int]) -> int:
        total = 0
        cur_max = cur_min = 0
        best_max, best_min = float('-inf'), float('inf')
        for x in nums:
            cur_max = max(x, cur_max + x)
            best_max = max(best_max, cur_max)
            cur_min = min(x, cur_min + x)
            best_min = min(best_min, cur_min)
            total += x
        if best_max < 0:
            return best_max
        return max(best_max, total - best_min)
```

**Complexity.** Time O(n), space O(1).

**Watch out.** The all-negative check is the classic bug: `[-3,-2,-3]` must return `-2`, not `0`.

```test
assert Solution().maxSubarraySumCircular([1,-2,3,-2]) == 3
assert Solution().maxSubarraySumCircular([5,-3,5]) == 10
assert Solution().maxSubarraySumCircular([-3,-2,-3]) == -2
```

# Binary Search

### 35. Search Insert Position
difficulty: Easy

**Problem.** In a sorted array of distinct numbers, return the index of `target`, or the index where it would be inserted. O(log n).

**Example.** `[1,3,5,6], 2` → `1`; `7` → `4`.

**Idea.** Binary search. When the loop ends without finding it, `l` sits exactly between the smaller and the larger elements: that's the insertion point.

**Steps.**
1. Set `l = 0`, `r = len(nums) - 1`.
2. While `l <= r`: look at `mid`. Equal to target → return `mid`.
3. `nums[mid] < target` → the answer is to the right: `l = mid + 1`. Otherwise `r = mid - 1`.
4. If the loop ends, `l` is the first index with a value bigger than the target: return `l`, the insert position.

```python
class Solution:
    def searchInsert(self, nums: List[int], target: int) -> int:
        l, r = 0, len(nums) - 1
        while l <= r:
            mid = (l + r) // 2
            if nums[mid] == target:
                return mid
            if nums[mid] < target:
                l = mid + 1
            else:
                r = mid - 1
        return l
```

**Complexity.** Time O(log n), space O(1).

**Watch out.** Everything left of `l` is proven smaller, everything right of `r` is proven larger; when `l > r` there's nothing undecided, so `l` is the first larger position. Built-in: `bisect.bisect_left(nums, target)`.

```test
assert Solution().searchInsert([1,3,5,6], 5) == 2
assert Solution().searchInsert([1,3,5,6], 2) == 1
assert Solution().searchInsert([1,3,5,6], 7) == 4
assert Solution().searchInsert([1,3,5,6], 0) == 0
```

### 74. Search a 2D Matrix
difficulty: Medium

**Problem.** Each row is sorted and each row's first value is greater than the previous row's last. Is `target` in the matrix? O(log(m·n)).

**Idea.** Read row by row, the matrix is one sorted list of `m·n` values. Binary search on index `0..m·n-1`, converting `mid` to `(mid // n, mid % n)`.

**Steps.**
1. Treat the `m × n` matrix as one sorted list of length `m * n`.
2. Binary search on `l = 0`, `r = m * n - 1`.
3. Convert `mid` to a cell: row `mid // n`, column `mid % n`.
4. Equal → `True`; smaller → `l = mid + 1`; bigger → `r = mid - 1`. If the range empties → `False`.

```python
class Solution:
    def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:
        m, n = len(matrix), len(matrix[0])
        l, r = 0, m * n - 1
        while l <= r:
            mid = (l + r) // 2
            val = matrix[mid // n][mid % n]
            if val == target:
                return True
            if val < target:
                l = mid + 1
            else:
                r = mid - 1
        return False
```

**Complexity.** Time O(log(m·n)), space O(1).

**Watch out.** Divide by the number of **columns** `n` to get the row.

```test
m = [[1,3,5,7],[10,11,16,20],[23,30,34,60]]
assert Solution().searchMatrix(m, 3) is True
assert Solution().searchMatrix(m, 13) is False
```

### 162. Find Peak Element
difficulty: Medium

**Problem.** Return the index of any element strictly greater than its neighbours (outside the array counts as −∞; neighbours are never equal). O(log n).

**Idea.** Compare `nums[mid]` with `nums[mid + 1]`. If the right neighbour is bigger, you're on an upward slope and a peak must exist to the right; otherwise a peak exists at `mid` or to its left.

**Steps.**
1. Set `l = 0`, `r = len(nums) - 1`.
2. While `l < r`, compare `nums[mid]` with `nums[mid + 1]`.
3. If the right neighbour is bigger, the values go up, so a peak is on the right: `l = mid + 1`.
4. Otherwise `mid` could be the peak, or a peak is to its left: `r = mid`.
5. When `l == r`, that index is a peak.

```python
class Solution:
    def findPeakElement(self, nums: List[int]) -> int:
        l, r = 0, len(nums) - 1
        while l < r:
            mid = (l + r) // 2
            if nums[mid] < nums[mid + 1]:
                l = mid + 1
            else:
                r = mid
        return l
```

**Complexity.** Time O(log n), space O(1).

**Watch out.** Use `l < r` and `r = mid` (not `mid - 1`), because `mid` itself may be the peak. `mid + 1` is always valid since `mid < r`.

```test
assert Solution().findPeakElement([1,2,3,1]) == 2
assert Solution().findPeakElement([1,2,1,3,5,6,4]) in (1, 5)
assert Solution().findPeakElement([1]) == 0
```

### 33. Search in Rotated Sorted Array
difficulty: Medium

**Problem.** A sorted array of distinct values was rotated (e.g. `[4,5,6,7,0,1,2]`). Find `target`'s index or -1 in O(log n).

**Idea.** At any `mid`, at least one half (`l..mid` or `mid..r`) is normally sorted. Check if the target lies inside the sorted half's range; if so search there, else search the other half.

**Steps.**
1. If `nums[mid] == target`, return `mid`.
2. If `nums[l] <= nums[mid]` (left half sorted): if `nums[l] <= target < nums[mid]` go left, else go right.
3. Otherwise (right half sorted): if `nums[mid] < target <= nums[r]` go right, else go left.

```python
class Solution:
    def search(self, nums: List[int], target: int) -> int:
        l, r = 0, len(nums) - 1
        while l <= r:
            mid = (l + r) // 2
            if nums[mid] == target:
                return mid
            if nums[l] <= nums[mid]:
                if nums[l] <= target < nums[mid]:
                    r = mid - 1
                else:
                    l = mid + 1
            else:
                if nums[mid] < target <= nums[r]:
                    l = mid + 1
                else:
                    r = mid - 1
        return -1
```

**Complexity.** Time O(log n), space O(1).

**Watch out.** `nums[l] <= nums[mid]` uses `<=` so the case `l == mid` counts as the left half being sorted.

```test
assert Solution().search([4,5,6,7,0,1,2], 0) == 4
assert Solution().search([4,5,6,7,0,1,2], 3) == -1
assert Solution().search([1], 0) == -1
assert Solution().search([3,1], 1) == 1
```

### 34. Find First and Last Position of Element in Sorted Array
difficulty: Medium

**Problem.** Return `[first, last]` index of `target` in a sorted array, or `[-1,-1]`, in O(log n).

**Idea.** Two binary searches: the first index with value `>= target` (lower bound) and the first index with value `> target` (upper bound) minus 1.

**Steps.**
1. Write `lower_bound(x)`: the first index whose value is `>= x` (returns `len(nums)` if none).
2. `first = lower_bound(target)`.
3. If `first` is past the end or `nums[first] != target`, the target is missing → `[-1, -1]`.
4. `last = lower_bound(target + 1) - 1`: one before the first value bigger than the target.
5. Return `[first, last]`.

```python
class Solution:
    def searchRange(self, nums: List[int], target: int) -> List[int]:
        def lower_bound(x):
            l, r = 0, len(nums)
            while l < r:
                mid = (l + r) // 2
                if nums[mid] < x:
                    l = mid + 1
                else:
                    r = mid
            return l

        first = lower_bound(target)
        if first == len(nums) or nums[first] != target:
            return [-1, -1]
        return [first, lower_bound(target + 1) - 1]
```

**Complexity.** Time O(log n), space O(1).

**Watch out.** Built-ins: `bisect_left(nums, target)` and `bisect_right(nums, target) - 1`. The `lower_bound` template (`r = len(nums)`, `l < r`, `r = mid`) is worth memorizing.

```test
assert Solution().searchRange([5,7,7,8,8,10], 8) == [3,4]
assert Solution().searchRange([5,7,7,8,8,10], 6) == [-1,-1]
assert Solution().searchRange([], 0) == [-1,-1]
```

### 153. Find Minimum in Rotated Sorted Array
difficulty: Medium

**Problem.** Return the minimum of a rotated sorted array of distinct values in O(log n).

**Idea.** Compare `nums[mid]` with `nums[r]`. If `nums[mid] > nums[r]`, the drop (the minimum) is to the right of `mid`; otherwise the minimum is at `mid` or to its left.

**Steps.**
1. Set `l = 0`, `r = len(nums) - 1`.
2. While `l < r`, compare `nums[mid]` with `nums[r]`.
3. If `nums[mid] > nums[r]`, the rotation point (the minimum) is to the right of `mid`: `l = mid + 1`.
4. Otherwise `mid..r` is sorted, so the minimum is at `mid` or to its left: `r = mid`.
5. Return `nums[l]`.

```python
class Solution:
    def findMin(self, nums: List[int]) -> int:
        l, r = 0, len(nums) - 1
        while l < r:
            mid = (l + r) // 2
            if nums[mid] > nums[r]:
                l = mid + 1
            else:
                r = mid
        return nums[l]
```

**Complexity.** Time O(log n), space O(1).

**Watch out.** Compare with `nums[r]`, not `nums[l]`: with no rotation, comparing to the left end gives wrong moves.

```test
assert Solution().findMin([3,4,5,1,2]) == 1
assert Solution().findMin([4,5,6,7,0,1,2]) == 0
assert Solution().findMin([11,13,15,17]) == 11
```

### 4. Median of Two Sorted Arrays
difficulty: Hard

**Problem.** Return the median of two sorted arrays in O(log(m + n)).

**Example.** `[1,3], [2]` → `2.0`; `[1,2], [3,4]` → `2.5`.

**Idea.** Binary-search a **partition**: take `i` elements from the smaller array `A` and `j = half - i` from `B` for the left half. The partition is right when every left element ≤ every right element: `A[i-1] <= B[j]` and `B[j-1] <= A[i]`. Then the median comes from the max of the left side and min of the right side.

**Steps.**
1. Make `A` the shorter array; `half = (m + n + 1) // 2`.
2. Binary search `i` in `0..m`; `j = half - i`.
3. Use −∞ / +∞ for missing neighbours at the edges.
4. If `Aleft > Bright`, move `i` left; if `Bleft > Aright`, move `i` right; else compute the median.

```python
class Solution:
    def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
        A, B = nums1, nums2
        if len(A) > len(B):
            A, B = B, A
        m, n = len(A), len(B)
        half = (m + n + 1) // 2
        lo, hi = 0, m
        while lo <= hi:
            i = (lo + hi) // 2
            j = half - i
            a_left = A[i - 1] if i > 0 else float('-inf')
            a_right = A[i] if i < m else float('inf')
            b_left = B[j - 1] if j > 0 else float('-inf')
            b_right = B[j] if j < n else float('inf')
            if a_left > b_right:
                hi = i - 1
            elif b_left > a_right:
                lo = i + 1
            else:
                if (m + n) % 2:
                    return float(max(a_left, b_left))
                return (max(a_left, b_left) + min(a_right, b_right)) / 2
```

**Complexity.** Time O(log(min(m, n))), space O(1).

**Watch out.** Searching on the **shorter** array guarantees `j` stays in range. Merging both arrays is easier (O(m + n)) and fine to mention first.

```test
assert Solution().findMedianSortedArrays([1,3], [2]) == 2.0
assert Solution().findMedianSortedArrays([1,2], [3,4]) == 2.5
assert Solution().findMedianSortedArrays([], [1]) == 1.0
assert Solution().findMedianSortedArrays([2], []) == 2.0
```
