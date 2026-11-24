## Disjoint Set

### Merging Communities

**Problem.** People start in their own communities. `M i j` merges the communities of `i` and `j`; `Q i` prints the size of `i`'s community.

**Idea.** A **disjoint-set union** with union by size and path compression. Sizes live at the roots, so a query is one `find`.

**Steps.**
1. `find` with path halving; `union` attaches the smaller root under the larger and adds the sizes.
2. Answer `Q` with `size[find(i)]`.

```python
import sys


def main():
    data = sys.stdin.read().split()
    n, q = int(data[0]), int(data[1])
    parent = list(range(n + 1))
    size = [1] * (n + 1)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    out = []
    pos = 2
    for _ in range(q):
        if data[pos] == 'M':
            a, b = find(int(data[pos + 1])), find(int(data[pos + 2]))
            pos += 3
            if a != b:
                if size[a] < size[b]:
                    a, b = b, a
                parent[b] = a
                size[a] += size[b]
        else:
            out.append(size[find(int(data[pos + 1]))])
            pos += 2
    print('\n'.join(map(str, out)))


main()
```

**Watch out.** Merging two people already in the same community must not add the size twice; the `a != b` check prevents it.

```stdin
3 6
Q 1
M 1 2
Q 2
M 2 3
Q 3
Q 2
```

```stdout
1
2
3
3
```

### Components in a graph

**Problem.** A bipartite graph has `2N` nodes and `N` edges. Print the smallest and largest connected-component sizes, ignoring single nodes.

**Idea.** Union-find over all the edge endpoints, then look at the root sizes and keep only the components with at least 2 nodes.

**Steps.**
1. Union every edge (by size, with path compression).
2. Min and max of `size[root]` over the roots with size `≥ 2`.

```python
import os


def componentsInGraph(gb):
    n = 2 * len(gb)
    parent = list(range(n + 1))
    size = [1] * (n + 1)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in gb:
        ra, rb = find(a), find(b)
        if ra != rb:
            if size[ra] < size[rb]:
                ra, rb = rb, ra
            parent[rb] = ra
            size[ra] += size[rb]
    sizes = [size[v] for v in range(1, n + 1) if find(v) == v and size[v] >= 2]
    return [min(sizes), max(sizes)]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    gb = [list(map(int, input().rstrip().split())) for _ in range(n)]
    fptr.write(' '.join(map(str, componentsInGraph(gb))) + '\n')
    fptr.close()
```

**Watch out.** Isolated nodes are not components here. Only the roots carry valid sizes, so check `find(v) == v` before reading a size.

```stdin
5
1 6
2 7
3 8
4 9
2 6
```

```stdout
2 4
```

### Kundu and Tree

**Problem.** In a tree whose edges are red or black, count the triplets of nodes such that every pair's path contains at least one red edge. Answer modulo 10⁹+7.

**Idea.** Count the complement. A pair's path has no red edge exactly when both nodes are in the same **black component** (the components of the black edges only). A triplet is bad when some pair shares a black component. For a black component of size `s`, the bad triplets are:
- `C(s, 3)`, all three inside it;
- `C(s, 2)·(n − s)`, exactly two inside it.

Different components never overlap in these counts. So the answer is `C(n, 3) − Σ [C(s, 3) + C(s, 2)(n − s)]`.

**Steps.**
1. Union-find over the black edges; component sizes.
2. Subtract the bad counts from `C(n, 3)`.

```python
import sys

MOD = 10 ** 9 + 7


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    parent = list(range(n + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(n - 1):
        a, b, c = int(data[1 + 3 * i]), int(data[2 + 3 * i]), data[3 + 3 * i]
        if c == 'b':
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
    sizes = {}
    for v in range(1, n + 1):
        r = find(v)
        sizes[r] = sizes.get(r, 0) + 1
    total = n * (n - 1) * (n - 2) // 6
    for s in sizes.values():
        total -= s * (s - 1) * (s - 2) // 6 + s * (s - 1) // 2 * (n - s)
    print(total % MOD)


main()
```

**Watch out.** "At least one red edge on each pair's path" excludes any pair inside one black component. The complement count avoids enumerating triplets, which would be O(n³).

```stdin
5
1 2 b
2 3 r
3 4 r
4 5 b
```

```stdout
4
```

### Super Maximum Cost Queries

**Problem.** For a weighted tree, a path's cost is its largest edge weight. Each query `[L, R]` asks how many paths (unordered pairs of distinct nodes) have a cost within `[L, R]`.

**Idea.** Add the edges in increasing weight order with union-find (Kruskal style). When an edge of weight `w` joins components of sizes `a` and `b`, exactly `a·b` new paths get cost `w`. Accumulate the counts by weight, take prefix sums, and answer each query as `count(≤ R) − count(≤ L−1)` with binary search.

**Steps.**
1. Sort the edges; union them, recording `(w, cumulative pairs)`.
2. Per query, `bisect` on the weights.

```python
import os
from bisect import bisect_right


def solve(tree, queries):
    n = len(tree) + 1
    parent = list(range(n + 1))
    size = [1] * (n + 1)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    weights, cum = [], []
    total = 0
    for u, v, w in sorted(tree, key=lambda e: e[2]):
        ru, rv = find(u), find(v)
        total += size[ru] * size[rv]
        if size[ru] < size[rv]:
            ru, rv = rv, ru
        parent[rv] = ru
        size[ru] += size[rv]
        weights.append(w)
        cum.append(total)

    def upto(x):
        k = bisect_right(weights, x)
        return cum[k - 1] if k else 0

    return [upto(R) - upto(L - 1) for L, R in queries]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, q = map(int, input().split())
    tree = [list(map(int, input().rstrip().split())) for _ in range(n - 1)]
    queries = [list(map(int, input().rstrip().split())) for _ in range(q)]
    fptr.write('\n'.join(map(str, solve(tree, queries))) + '\n')
    fptr.close()
```

**Watch out.** Equal weights are fine: the cumulative count after the last edge of weight `w` is what `bisect_right` returns. Precomputing makes each query O(log n).

```stdin
5 5
1 2 3
1 4 2
2 5 6
3 4 1
1 1
1 2
2 3
2 5
1 6
```

```stdout
1
3
5
5
10
```
