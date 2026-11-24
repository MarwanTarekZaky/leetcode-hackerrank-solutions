## Strings

### Count Strings

**Problem.** A regular expression over `a`, `b` uses fully parenthesised concatenation `(R1R2)`, alternation `(R1|R2)` and star `(R1*)`. Count the strings of length `L` (up to 10⁹) it matches, modulo 10⁹+7.

**Idea.** Turn the regex into an automaton, then count paths. Build an NFA with Thompson's construction, convert it into a DFA (subset construction) so every string has exactly one path, then the number of accepted strings of length `L` is the number of length-`L` paths from the start to an accepting state: a row of `M^L`, where `M[i][j]` counts the letters going from state `i` to `j`. Matrix exponentiation handles `L = 10⁹` in about 30 squarings.

**Steps.**
1. Parse recursively: a letter is a 2-state NFA; `(R1R2)` links `R1`'s end to `R2`'s start; `(R1|R2)` and `(R1*)` add new start/end states with ε-moves.
2. Subset construction from the ε-closure of the start state, over letters `a` and `b`.
3. `M` = transition-count matrix of the DFA; compute `M^L` by repeated squaring (mod `p`).
4. Sum the entries of the start row for the DFA states that contain the NFA's accept state.

```python
import os

MOD = 10 ** 9 + 7


def countStrings(r, l):
    trans = []

    def new():
        trans.append({})
        return len(trans) - 1

    def add(u, label, v):
        trans[u].setdefault(label, []).append(v)

    pos = 0

    def parse():
        nonlocal pos
        if r[pos] in "ab":
            s, t = new(), new()
            add(s, r[pos], t)
            pos += 1
            return s, t
        pos += 1                       # '('
        s1, t1 = parse()
        if r[pos] == "*":
            pos += 2                   # '*)'
            s, t = new(), new()
            for u, v in ((s, s1), (s, t), (t1, s1), (t1, t)):
                add(u, "", v)
            return s, t
        if r[pos] == "|":
            pos += 1
            s2, t2 = parse()
            pos += 1                   # ')'
            s, t = new(), new()
            for u, v in ((s, s1), (s, s2), (t1, t), (t2, t)):
                add(u, "", v)
            return s, t
        s2, t2 = parse()
        pos += 1                       # ')'
        add(t1, "", s2)
        return s1, t2

    start, accept = parse()

    def closure(states):
        seen, stack = set(states), list(states)
        while stack:
            for v in trans[stack.pop()].get("", []):
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        return frozenset(seen)

    order = [closure([start])]
    index = {order[0]: 0}
    edges = []
    for cur in order:
        row = []
        for ch in "ab":
            nxt = closure([v for u in cur for v in trans[u].get(ch, [])])
            if nxt:
                if nxt not in index:
                    index[nxt] = len(order)
                    order.append(nxt)
                row.append(index[nxt])
        edges.append(row)

    k = len(order)
    M = [[0] * k for _ in range(k)]
    for u, row in enumerate(edges):
        for v in row:
            M[u][v] += 1

    def mul(A, B):
        cols = list(zip(*B))
        return [[sum(x * y for x, y in zip(row, col)) % MOD for col in cols] for row in A]

    result = [[int(i == j) for j in range(k)] for i in range(k)]
    while l:
        if l & 1:
            result = mul(result, M)
        M = mul(M, M)
        l >>= 1
    return sum(result[0][j] for j, st in enumerate(order) if accept in st) % MOD


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        r, l = input().split()
        fptr.write(str(countStrings(r, int(l))) + '\n')
    fptr.close()
```

**Watch out.** Counting paths in the **NFA** overcounts strings that have several accepting paths (`((a|a)*)`); converting to a DFA first makes each string correspond to exactly one path.

```stdin
3
((ab)|(ba)) 2
((a|b)*) 5
((a*)(b(a*))) 100
```

```stdout
2
32
100
```

### String Function Calculation

**Problem.** For a string `t`, maximize `f(s) = |s| × (number of occurrences of s in t)` over all substrings `s`.

**Idea.** A **suffix automaton** groups all substrings by their set of end positions. Every state's strings occur the same number of times, and its longest string is the best choice for that state. Occurrence counts are found by pushing counts up the suffix-link tree.

**Steps.**
1. Build the suffix automaton; each non-clone state starts with count 1.
2. Process states by decreasing length and add each state's count to its suffix link's count.
3. Answer = max over states of `len(state) × count(state)`.

```python
import os


def maxValue(t):
    length, link, nxt, cnt = [0], [-1], [{}], [0]
    last = 0
    for ch in t:
        cur = len(length)
        length.append(length[last] + 1)
        link.append(-1)
        nxt.append({})
        cnt.append(1)
        p = last
        while p != -1 and ch not in nxt[p]:
            nxt[p][ch] = cur
            p = link[p]
        if p == -1:
            link[cur] = 0
        else:
            q = nxt[p][ch]
            if length[p] + 1 == length[q]:
                link[cur] = q
            else:
                clone = len(length)
                length.append(length[p] + 1)
                link.append(link[q])
                nxt.append(dict(nxt[q]))
                cnt.append(0)
                while p != -1 and nxt[p].get(ch) == q:
                    nxt[p][ch] = clone
                    p = link[p]
                link[q] = link[cur] = clone
        last = cur
    for v in sorted(range(1, len(length)), key=length.__getitem__, reverse=True):
        cnt[link[v]] += cnt[v]
    return max(length[v] * cnt[v] for v in range(1, len(length)))


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = input()
    result = maxValue(t)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Clones start with count 0: they represent existing occurrences, so giving them 1 would double count.

```stdin
aaaaaa
```

```stdout
12
```

### Build a Palindrome

**Problem.** Find the longest palindrome `sa + sb` where `sa` is a non-empty substring of `a` and `sb` a non-empty substring of `b`; break ties by the alphabetically smallest; print `-1` if impossible.

**Idea.** Any answer looks like `X + P + reverse(X)`, where `X` is non-empty, `P` is a palindrome (possibly empty), and either `X + P` comes from `a` (with `reverse(X)` from `b`) or `X` comes from `a` (with `P + reverse(X)` from `b`). For the first case, at every end position `i` in `a`, take the longest `X` ending at `i` whose reverse occurs in `b` (a suffix automaton of `reverse(b)` gives this for all `i` in one pass) and the longest palindrome starting at `i + 1` (Manacher). The second case is the first case applied to `(reverse(b), reverse(a))`.

**Steps.**
1. `L[i]` = longest suffix of `a[:i+1]` that occurs in `reverse(b)` (match `a` against the suffix automaton of `reverse(b)`).
2. `pal[j]` = longest palindrome starting at `j` in `a` (Manacher radii, then `pal[j] >= pal[j-1] - 2`).
3. Candidate length at `i`: `2·L[i] + pal[i+1]` when `L[i] > 0`.
4. Repeat with `(reverse(b), reverse(a))`, keep the maximum length, and build only the candidate strings of that length to pick the smallest.

```python
import os


def build_sam(s):
    length, link, nxt = [0], [-1], [{}]
    last = 0
    for ch in s:
        cur = len(length)
        length.append(length[last] + 1)
        link.append(-1)
        nxt.append({})
        p = last
        while p != -1 and ch not in nxt[p]:
            nxt[p][ch] = cur
            p = link[p]
        if p == -1:
            link[cur] = 0
        else:
            q = nxt[p][ch]
            if length[p] + 1 == length[q]:
                link[cur] = q
            else:
                clone = len(length)
                length.append(length[p] + 1)
                link.append(link[q])
                nxt.append(dict(nxt[q]))
                while p != -1 and nxt[p].get(ch) == q:
                    nxt[p][ch] = clone
                    p = link[p]
                link[q] = link[cur] = clone
        last = cur
    return length, link, nxt


def match_lengths(a, sam):
    length, link, nxt = sam
    v = l = 0
    out = []
    for ch in a:
        while v and ch not in nxt[v]:
            v = link[v]
            l = length[v]
        if ch in nxt[v]:
            v = nxt[v][ch]
            l += 1
        else:
            l = 0
        out.append(l)
    return out


def palindrome_starts(s):
    t = "#" + "#".join(s) + "#"
    rad = [0] * len(t)
    c = r = 0
    for i in range(len(t)):
        if i < r:
            rad[i] = min(r - i, rad[2 * c - i])
        while i - rad[i] - 1 >= 0 and i + rad[i] + 1 < len(t) and t[i - rad[i] - 1] == t[i + rad[i] + 1]:
            rad[i] += 1
        if i + rad[i] > r:
            c, r = i, i + rad[i]
    best = [0] * (len(s) + 1)
    for i, p in enumerate(rad):
        if p:
            start = (i - p) // 2
            best[start] = max(best[start], p)
    for j in range(1, len(s)):
        best[j] = max(best[j], best[j - 1] - 2)
    return best


def candidates(a, b):
    L = match_lengths(a, build_sam(b[::-1]))
    pal = palindrome_starts(a)
    return [(2 * L[i] + pal[i + 1], i, L[i], pal[i + 1], a) for i in range(len(a)) if L[i]]


def buildPalindrome(a, b):
    cands = candidates(a, b) + candidates(b[::-1], a[::-1])
    if not cands:
        return "-1"
    best = max(c[0] for c in cands)
    words = []
    for total, i, l, p, s in cands:
        if total == best:
            x = s[i - l + 1:i + 1]
            words.append(x + s[i + 1:i + 1 + p] + x[::-1])
    return min(words)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        a = input()
        b = input()
        fptr.write(buildPalindrome(a, b) + '\n')
    fptr.close()
```

**Watch out.**
- Taking `X` as long as possible is always right for length (each extra character adds 2), so only one candidate per position is needed.
- Ties are broken by building the tied strings; with very many ties (`aaaa…`) that part can become quadratic.

```stdin
3
bac
bac
abc
def
jdfh
fds
```

```stdout
aba
-1
dfhfd
```

### Build a String

**Problem.** Build `S` from an empty string: appending a character costs `A`, appending a copy of any substring of what's already built costs `B`. Return the minimum cost.

**Idea.** `dp[j]` = cost to build the prefix of length `j`. Either append one character (`dp[j-1] + A`), or finish with a copy `S[i:j]` that already occurs in `S[:i]` (`dp[i] + B`). `dp` never decreases with `j`, so the best copy starts at the **smallest** such `i`. With `reach[i]` = the furthest `j` copyable from `i`, `reach` never decreases either, so a single pointer finds that smallest `i`.

**Steps.**
1. `k(i)` = longest `k` with `S[i:i+k]` inside `S[:i]`; since `k(i+1) >= k(i) - 1`, extend `k` incrementally. `reach[i] = i + k(i)`.
2. For `j = 1..n`: `dp[j] = dp[j-1] + A`; move pointer `p` forward while `reach[p] < j`; if `p < j`, `dp[j] = min(dp[j], dp[p] + B)`.

```python
import os


def buildString(a, b, s):
    n = len(s)
    reach, k = [], 0
    for i in range(n):
        k = max(k - 1, 0)
        while i + k < n and s[i:i + k + 1] in s[:i]:
            k += 1
        reach.append(i + k)
    dp = [0] * (n + 1)
    p = 0
    for j in range(1, n + 1):
        dp[j] = dp[j - 1] + a
        while p < j and reach[p] < j:
            p += 1
        if p < j:
            dp[j] = min(dp[j], dp[p] + b)
    return dp[n]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        n, a, b = map(int, input().split())
        s = input()
        fptr.write(str(buildString(a, b, s)) + '\n')
    fptr.close()
```

**Watch out.** The copied substring must already exist **before** position `i` (`S[:i]`), not overlap with what you're writing.

```stdin
2
9 4 5
aabaacaba
9 8 9
bacbacacb
```

```stdout
26
42
```

### Gridland Provinces

**Problem.** A province is a 2 × N grid of letters. A knight visits every cell exactly once, moving to side-adjacent cells, and writes down the letters. Count the distinct strings he can produce.

**Idea.** Every such path has the same shape (up to mirroring left/right): start at column `c`, loop through all columns to the left (along one row to the edge and back along the other), zig-zag column by column to some column `j`, then loop through all columns to the right. That's O(N²) paths per direction. Hash each path's string in O(1) by combining precomputed substring hashes, and count distinct hashes.

**Steps.**
1. Precompute rolling hashes of each row, each reversed row, and the two zig-zag orders (which row is entered first in each column).
2. For each start column `c`, start row `r`, and switch column `j`: hash = left loop (`c+1` columns) + zig-zag (`c+1 … j-1`) + right loop (`j … N-1`).
3. Do the same on the mirrored grid; the answer is the number of distinct hashes.

```python
import os

MOD = (1 << 61) - 1
BASE = 1_000_003


def gridlandProvinces(s1, s2):
    n = len(s1)
    pw = [1] * (2 * n + 1)
    for i in range(1, len(pw)):
        pw[i] = pw[i - 1] * BASE % MOD

    def prefix(s):
        h = [0]
        for ch in s:
            h.append((h[-1] * BASE + ord(ch)) % MOD)
        return h

    def sub(h, l, r):
        return (h[r] - h[l] * pw[r - l]) % MOD

    seen = set()
    for g in ((s1, s2), (s1[::-1], s2[::-1])):
        row = [prefix(g[0]), prefix(g[1])]
        rev = [prefix(g[0][::-1]), prefix(g[1][::-1])]
        zig = [prefix("".join(g[(t + k) % 2][k] + g[1 - (t + k) % 2][k] for k in range(n))) for t in (0, 1)]
        for c in range(n):
            for r in (0, 1):
                left = (sub(rev[r], n - 1 - c, n) * pw[c + 1] + sub(row[1 - r], 0, c + 1)) % MOD
                t = (1 - r - (c + 1)) % 2
                for j in range(c + 1, n + 1):
                    x = (t + j) % 2
                    middle = sub(zig[t], 2 * (c + 1), 2 * j)
                    right = (sub(row[x], j, n) * pw[n - j] + sub(rev[1 - x], 0, n - j)) % MOD
                    h = (left * pw[2 * (j - c - 1)] + middle) % MOD
                    seen.add((h * pw[2 * (n - j)] + right) % MOD)
    return len(seen)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    p = int(input().strip())
    for _ in range(p):
        n = int(input().strip())
        s1 = input()
        s2 = input()
        fptr.write(str(gridlandProvinces(s1, s2)) + '\n')
    fptr.close()
```

**Watch out.**
- Building every path string explicitly is O(N³) characters; hashing keeps each path O(1).
- It is still about 1.4 million hashes for N = 600; choose PyPy 3 on HackerRank for the larger tests.

```stdin
3
1
a
a
3
dab
abd
5
ababa
babab
```

```stdout
1
8
2
```

### Cards Permutation

**Problem.** Some entries of a permutation of `1..n` are 0 (forgotten). Sum the lexicographic line numbers (1-based ranks) of all permutations consistent with it, modulo 10⁹+7. `n` up to 3·10⁵.

**Idea.** The rank of a permutation is `Σ_i (n-1-i)! · #{j > i : p_j < p_i}`. Sum each term over all `m!` completions (`m` = number of zeros) by linearity, using counting arguments:
- known `p_i = v`: known values to the right that are smaller (count × `m!`), plus zeros to the right times missing values below `v`, each pairing appearing in `(m-1)!` completions;
- unknown `p_i`: known values to the right paired with larger missing values (`(m-1)!` each), plus zero pairs to the right, which are inverted in exactly half of the completions.

**Steps.**
1. `less[v]` = number of missing values below `v`; factorials mod `p`.
2. Scan from right to left with a Fenwick tree over known values, the number of zeros to the right, and `G` = Σ over known values to the right of (missing values greater than them).
3. Add `(n-1-i)! × term_i` for each position, plus `m!` for the 1-based ranks.

```python
import os

MOD = 10 ** 9 + 7


def solve(x):
    n = len(x)
    present = [False] * (n + 2)
    for v in x:
        present[v] = True
    missing = [v for v in range(1, n + 1) if not present[v]]
    m = len(missing)
    less = [0] * (n + 2)
    for v in range(1, n + 2):
        less[v] = less[v - 1] + (1 if v - 1 >= 1 and not present[v - 1] else 0)
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = fact[i - 1] * i % MOD
    fm, fm1, inv2 = fact[m], fact[m - 1] if m else 0, (MOD + 1) // 2
    tree = [0] * (n + 1)
    total = fm
    zeros_right = greater_sum = 0
    for i in range(n - 1, -1, -1):
        v = x[i]
        if v:
            smaller_known, j = 0, v - 1
            while j > 0:
                smaller_known += tree[j]
                j -= j & -j
            term = fm * smaller_known + fm1 * zeros_right * less[v]
            j = v
            while j <= n:
                tree[j] += 1
                j += j & -j
            greater_sum += m - less[v]
        else:
            term = fm1 * greater_sum + fm * zeros_right % MOD * inv2
            zeros_right += 1
        total = (total + fact[n - 1 - i] * (term % MOD)) % MOD
    return total


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    a = list(map(int, input().rstrip().split()))
    result = solve(a)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** "Half of the completions" uses the modular inverse of 2, `(p + 1) // 2`, not integer division.

```stdin
4
0 2 3 0
```

```stdout
23
```

### Ashton and String

**Problem.** Sort all distinct substrings, concatenate them, and print the `k`-th character.

**Idea.** In suffix-array order, suffix `sa[i]` contributes exactly the new substrings that are its prefixes longer than `lcp[i]` (the common prefix with the previous suffix), already in sorted order. Each length `L` contributes `L` characters, so skip whole suffixes with the arithmetic-series total, then find the length and character inside the right one.

**Steps.**
1. Build the suffix array (prefix doubling) and the LCP array (Kasai).
2. For each suffix, new lengths are `lcp+1 .. n-sa`; their character total is an arithmetic series.
3. Skip suffixes while `k` is larger; inside the right one, skip lengths `L = lo, lo+1, …` until `k <= L`; answer `s[sa + k - 1]`.

```python
import os


def suffix_array(s):
    n = len(s)
    rank = [ord(c) for c in s]
    sa = list(range(n))
    k = 1
    while True:
        key = [(rank[i], rank[i + k] if i + k < n else -1) for i in range(n)]
        sa.sort(key=key.__getitem__)
        new = [0] * n
        for a, b in zip(sa, sa[1:]):
            new[b] = new[a] + (key[a] != key[b])
        rank = new
        if rank[sa[-1]] == n - 1:
            return sa
        k *= 2


def lcp_array(s, sa):
    n = len(s)
    rank = [0] * n
    for i, p in enumerate(sa):
        rank[p] = i
    lcp, h = [0] * n, 0
    for p in range(n):
        if rank[p]:
            q = sa[rank[p] - 1]
            while p + h < n and q + h < n and s[p + h] == s[q + h]:
                h += 1
            lcp[rank[p]] = h
            h = max(h - 1, 0)
        else:
            h = 0
    return lcp


def ashtonString(s, k):
    n = len(s)
    sa = suffix_array(s)
    lcp = lcp_array(s, sa)
    for i, p in enumerate(sa):
        lo, hi = lcp[i] + 1, n - p
        if lo > hi:
            continue
        block = (lo + hi) * (hi - lo + 1) // 2
        if k > block:
            k -= block
            continue
        length = lo
        while k > length:
            k -= length
            length += 1
        return s[p + k - 1]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        s = input()
        k = int(input().strip())
        fptr.write(str(ashtonString(s, k)) + '\n')
    fptr.close()
```

**Watch out.** The concatenated string has up to ~n³/6 characters; never build it. `k` fits Python's integers fine.

```stdin
1
dbac
3
```

```stdout
c
```

### String Similarity

**Problem.** Sum, over all suffixes of `s`, the length of their longest common prefix with `s`.

**Idea.** That's exactly the sum of the **Z-function** (`z[i]` = LCP of `s` and `s[i:]`), plus `n` for the whole string itself.

**Steps.**
1. Compute `z` in O(n) with the usual `[l, r]` window.
2. Return `n + sum(z[1:])`.

```python
import os


def stringSimilarity(s):
    n = len(s)
    z = [0] * n
    l = r = 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    return n + sum(z)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        fptr.write(str(stringSimilarity(input().strip())) + '\n')
    fptr.close()
```

**Watch out.** Comparing every suffix character by character is O(n²); the Z-function reuses work inside the window and is O(n).

```stdin
2
ababaa
aa
```

```stdout
11
3
```

### Super Functional Strings

**Problem.** Sum `length^(distinct letters)` over all distinct substrings, modulo 10⁹+7.

**Idea.** Use the suffix array: suffix `p` brings the new substrings `s[p:p+L]` for `L = lcp+1 … n-p`. Along one suffix, the number of distinct letters changes at most 26 times (at the first occurrence of each letter after `p`), so the lengths split into ≤ 26 ranges with a fixed exponent `d`. Each range adds `Σ L^d`, read from precomputed prefix sums of powers.

**Steps.**
1. Suffix array + LCP.
2. `firsts[p]` = sorted first positions of each letter at or after `p` (built right to left).
3. Prefix sums `S[d][x] = Σ_{L ≤ x} L^d` for `d` up to the number of distinct letters.
4. For each suffix, intersect its new length range with each fixed-`d` range and add the sums.

```python
import os

MOD = 10 ** 9 + 7


def suffix_array(s):
    n = len(s)
    rank = [ord(c) for c in s]
    sa = list(range(n))
    k = 1
    while True:
        key = [(rank[i], rank[i + k] if i + k < n else -1) for i in range(n)]
        sa.sort(key=key.__getitem__)
        new = [0] * n
        for a, b in zip(sa, sa[1:]):
            new[b] = new[a] + (key[a] != key[b])
        rank = new
        if rank[sa[-1]] == n - 1:
            return sa
        k *= 2


def lcp_array(s, sa):
    n = len(s)
    rank = [0] * n
    for i, p in enumerate(sa):
        rank[p] = i
    lcp, h = [0] * n, 0
    for p in range(n):
        if rank[p]:
            q = sa[rank[p] - 1]
            while p + h < n and q + h < n and s[p + h] == s[q + h]:
                h += 1
            lcp[rank[p]] = h
            h = max(h - 1, 0)
        else:
            h = 0
    return lcp


def superFunctionalStrings(s):
    n = len(s)
    sa = suffix_array(s)
    lcp = lcp_array(s, sa)
    distinct = len(set(s))
    power = [1] * (n + 1)
    sums = [None]
    for d in range(1, distinct + 1):
        row, acc = [0] * (n + 1), 0
        for x in range(1, n + 1):
            power[x] = power[x] * x % MOD
            acc += power[x]
            row[x] = acc % MOD
        sums.append(row)
    firsts, last = [None] * n, {}
    for p in range(n - 1, -1, -1):
        last[s[p]] = p
        firsts[p] = sorted(last.values())
    total = 0
    for i, p in enumerate(sa):
        lo, hi = lcp[i] + 1, n - p
        occ = firsts[p] + [n]
        for d in range(1, len(occ)):
            a = max(lo, occ[d - 1] - p + 1)
            b = min(hi, occ[d] - p)
            if a <= b:
                total += sums[d][b] - sums[d][a - 1]
    return total % MOD


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        fptr.write(str(superFunctionalStrings(input())) + '\n')
    fptr.close()
```

**Watch out.** The distinct count for length `L` is the number of first occurrences at offsets `< L`, so a letter first seen at offset `q - p` joins for lengths `>= q - p + 1`.

```stdin
3
aa
aba
abc
```

```stdout
3
19
38
```

### Circular Palindromes

**Problem.** For every rotation of `s` (`N` up to 5·10⁵), print the length of its longest palindromic substring.

**Idea.** Rotation `k` is the window `D[k : k+N]` of `D = s + s`. Inside a window, the longest palindrome is either (1) a maximal palindrome of `D` that fits entirely inside, (2) the longest palindrome starting at the window's first character, or (3) the longest one ending at its last character (palindromes cut by an edge shrink to these). With Manacher's radii on `D`, each center contributes to (1), (2) or (3) for a contiguous range of `k`, so all three reduce to "maximum over active intervals", handled by a sweep with lazy-deletion heaps.

**Steps.**
1. Manacher on `T = #D[0]#D[1]#…#`; center `i` has radius `P[i]`; window `k` is `T[2k … 2k+2N]`.
2. Inside: center `i` fits for `k` in `[ceil((i+P-2N)/2), floor((i-P)/2)]`, value `P[i]`.
3. Prefix: valid for `k` in `[max(ceil((i-P)/2), ceil((i-N)/2)), floor((i-1)/2)]`, value `i - 2k` (largest `i` wins).
4. Suffix: valid for `k` in `[floor((i-2N)/2) + 1, min(floor((i+P-2N)/2), floor((i-N)/2))]`, value `2k+2N-i` (smallest `i` wins).
5. Sweep `k = 0 … N-1`, pushing intervals as they start and discarding expired heap tops.

```python
import heapq
import os


def circularPalindromes(s):
    n = len(s)
    t = "#" + "#".join(s + s) + "#"
    m = len(t)
    P = [0] * m
    c = r = 0
    for i in range(m):
        if i < r:
            P[i] = min(r - i, P[2 * c - i])
        while i - P[i] - 1 >= 0 and i + P[i] + 1 < m and t[i - P[i] - 1] == t[i + P[i] + 1]:
            P[i] += 1
        if i + P[i] > r:
            c, r = i, i + P[i]

    def ceil2(x):
        return -((-x) // 2)

    starts = [[] for _ in range(n)]
    for i in range(1, m - 1):
        p = P[i]
        if not p:
            continue
        ranges = (
            (0, ceil2(i + p - 2 * n), (i - p) // 2, -p),
            (1, max(ceil2(i - p), ceil2(i - n)), (i - 1) // 2, -i),
            (2, (i - 2 * n) // 2 + 1, min((i + p - 2 * n) // 2, (i - n) // 2), i),
        )
        for kind, lo, hi, key in ranges:
            lo, hi = max(lo, 0), min(hi, n - 1)
            if lo <= hi:
                starts[lo].append((kind, key, hi))
    heaps = ([], [], [])
    out = []
    for k in range(n):
        for kind, key, hi in starts[k]:
            heapq.heappush(heaps[kind], (key, hi))
        best = 1
        for kind, h in enumerate(heaps):
            while h and h[0][1] < k:
                heapq.heappop(h)
            if h:
                key = h[0][0]
                best = max(best, -key if kind == 0 else -key - 2 * k if kind == 1 else 2 * k + 2 * n - key)
        out.append(best)
    return out


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    s = input()
    result = circularPalindromes(s)
    fptr.write('\n'.join(map(str, result)))
    fptr.write('\n')
    fptr.close()
```

**Watch out.** Running Manacher once per rotation is O(N²). This version is O(N log N), but with ~6 million heap operations at the limit, choose PyPy 3 on HackerRank.

```stdin
13
aaaaabbbbaaaa
```

```stdout
12
12
10
8
8
9
11
13
11
9
8
8
10
```

### Similar Strings

**Problem.** Two equal-length strings are similar if equal positions in one are exactly the equal positions in the other (a consistent letter renaming, with letters `a`–`j`). For each query `[l, r]`, count the substrings of `S` similar to `S[l..r]`.

**Idea.** Rename the letters of a substring in order of first appearance (`giggab` → `abaacd`); two substrings are similar exactly when these normalized forms are equal. The hash of the normalized form is `Σ label(c) · hash(positions of c)`, which uses 10 precomputed indicator hashes and the first occurrence of each letter, so every window's hash costs O(10). Count windows per length once, then answer all queries of that length from the counter.

**Steps.**
1. For each letter, prefix hashes of its indicator string (1 where the letter occurs).
2. `next_occ[i][c]` = first position ≥ `i` of letter `c`.
3. `window_hash(i, L)`: letters with `next_occ < i + L`, labeled 1, 2, … by first occurrence, combined with their indicator hashes.
4. For each distinct query length, count all window hashes once; answer `count[hash of the query window]`.

```python
import os
from collections import Counter

MOD = (1 << 61) - 1
BASE = 1_000_003


def similarStrings(s, queries):
    n = len(s)
    letters = sorted(set(s))
    pw = [1] * (n + 1)
    for i in range(1, n + 1):
        pw[i] = pw[i - 1] * BASE % MOD
    hashes = {}
    for c in letters:
        h = [0]
        for ch in s:
            h.append((h[-1] * BASE + (ch == c)) % MOD)
        hashes[c] = h
    next_occ = [None] * (n + 1)
    cur = {c: n for c in letters}
    next_occ[n] = dict(cur)
    for i in range(n - 1, -1, -1):
        cur[s[i]] = i
        next_occ[i] = dict(cur)

    def window_hash(i, L):
        firsts = sorted((pos, c) for c, pos in next_occ[i].items() if pos < i + L)
        total = 0
        for label, (_, c) in enumerate(firsts, 1):
            h = hashes[c]
            total += label * ((h[i + L] - h[i] * pw[L]) % MOD)
        return total % MOD

    by_length = {}
    out = []
    for l, r in queries:
        L = r - l + 1
        if L not in by_length:
            by_length[L] = Counter(window_hash(i, L) for i in range(n - L + 1))
        out.append(by_length[L][window_hash(l - 1, L)])
    return out


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, q = map(int, input().split())
    s = input().strip()
    queries = [list(map(int, input().rstrip().split())) for _ in range(q)]
    result = similarStrings(s, queries)
    fptr.write('\n'.join(map(str, result)))
    fptr.write('\n')
    fptr.close()
```

**Watch out.** Work is O(10·n) per **distinct** query length. That's fast when lengths repeat, but tests with many different lengths need a parameterized suffix structure, which is beyond what Python handles in time.

```stdin
8 4
giggabaj
1 1
1 2
1 3
2 4
```

```stdout
8
6
2
1
```

### Save Humanity

**Problem.** Print every start index where the virus `v` occurs in the patient DNA `p` with at most one mismatched character, or `No Match!`.

**Idea.** A window starting at `i` matches with ≤ 1 mismatch when the longest common prefix with `v` plus the longest common suffix with `v` covers at least `|v| - 1` characters. The Z-function gives all prefix lengths at once (`v + sep + p`), and running it on the reversed strings gives all suffix lengths.

**Steps.**
1. `pre[i]` = LCP of `p[i:]` and `v` (Z of `v + '\0' + p`).
2. `suf` = the same on reversed strings; the window ending at `i + m - 1` uses `suf[n - i - m]`.
3. Report `i` when `pre[i] + suf[n - i - m] >= m - 1`.

```python
def z_function(s):
    n = len(s)
    z = [0] * n
    l = r = 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    return z


def virusIndices(p, v):
    n, m = len(p), len(v)
    if m > n:
        print("No Match!")
        return
    pre = z_function(v + "\0" + p)[m + 1:]
    suf = z_function(v[::-1] + "\0" + p[::-1])[m + 1:]
    hits = [i for i in range(n - m + 1) if pre[i] + suf[n - i - m] >= m - 1]
    print(" ".join(map(str, hits)) if hits else "No Match!")


if __name__ == '__main__':
    t = int(input().strip())
    for _ in range(t):
        p, v = input().split()
        virusIndices(p, v)
```

**Watch out.** The separator `\0` keeps each Z value from running past the virus into the DNA.

```stdin
3
abbab ba
hello world
banana nan
```

```stdout
1 2
No Match!
0 2
```

### Find Strings

**Problem.** Take the union of the distinct substrings of several words, sort it, and answer queries "what is the `k`-th string?" (`INVALID` if there are fewer).

**Idea.** Build one suffix automaton over all words (joined with distinct separator characters). Every distinct substring is a path from the start state using only letters. Count, for every state, the number of letter-paths that start there (`1 +` the sum over its children). Then walk from the start, trying letters `a` to `z` and skipping whole subtrees by their counts, exactly like finding the `k`-th word in a trie.

**Steps.**
1. Suffix automaton of `w1 + sep1 + w2 + sep2 + …` with separators below `'a'`.
2. `paths[v] = 1 + Σ paths[child]` over letter transitions, in decreasing-length order.
3. For each `k`: if `k > paths[root] - 1`, answer `INVALID`; otherwise descend letter by letter, subtracting skipped subtree sizes.

```python
import os
import string


def findStrings(w, queries):
    text = "".join(word + chr(i + 1) for i, word in enumerate(w))
    length, link, nxt = [0], [-1], [{}]
    last = 0
    for ch in text:
        cur = len(length)
        length.append(length[last] + 1)
        link.append(-1)
        nxt.append({})
        p = last
        while p != -1 and ch not in nxt[p]:
            nxt[p][ch] = cur
            p = link[p]
        if p == -1:
            link[cur] = 0
        else:
            q = nxt[p][ch]
            if length[p] + 1 == length[q]:
                link[cur] = q
            else:
                clone = len(length)
                length.append(length[p] + 1)
                link.append(link[q])
                nxt.append(dict(nxt[q]))
                while p != -1 and nxt[p].get(ch) == q:
                    nxt[p][ch] = clone
                    p = link[p]
                link[q] = link[cur] = clone
        last = cur
    paths = [1] * len(length)
    for v in sorted(range(len(length)), key=length.__getitem__, reverse=True):
        paths[v] = 1 + sum(paths[u] for c, u in nxt[v].items() if c in string.ascii_lowercase)
    out = []
    for k in queries:
        if k > paths[0] - 1:
            out.append("INVALID")
            continue
        v, res = 0, []
        while k > 0:
            for c in string.ascii_lowercase:
                u = nxt[v].get(c)
                if u is None:
                    continue
                if k <= paths[u]:
                    res.append(c)
                    k -= 1
                    v = u
                    break
                k -= paths[u]
        out.append("".join(res))
    return out


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    w = [input() for _ in range(int(input().strip()))]
    queries = [int(input().strip()) for _ in range(int(input().strip()))]
    result = findStrings(w, queries)
    fptr.write('\n'.join(result))
    fptr.write('\n')
    fptr.close()
```

**Watch out.** Only follow `a`–`z` transitions: paths through a separator are not real substrings of any word.

```stdin
2
aab
aac
3
3
8
23
```

```stdout
aab
c
INVALID
```

### Palindromic Border

**Problem.** A palindromic border of `t` is a proper prefix of `t` that is also a suffix and a palindrome. Sum the number of palindromic borders over all substrings of `s` (by position), modulo 10⁹+7.

**Idea.** Choose a palindrome `X` and two different occurrences of it, at start positions `i < j`. The substring from `i` to the end of the second occurrence has `X` as a palindromic border, and every (substring, border) pair arises exactly once this way. So the answer is `Σ_X C(occ(X), 2)` over distinct palindromes. A **palindromic tree** (eertree) lists all distinct palindromes and their occurrence counts in O(n).

**Steps.**
1. Build the eertree; each time a palindrome is the longest suffix palindrome at some position, add 1 to its count.
2. Push counts to suffix links (from newest node to oldest) to get full occurrence counts.
3. Sum `c·(c-1)/2` over all palindromes.

```python
import os

MOD = 10 ** 9 + 7


def palindromicBorder(s):
    length, link, nxt, occ = [-1, 0], [0, 0], [{}, {}], [0, 0]
    last = 1
    for i, ch in enumerate(s):
        cur = last
        while not (i - length[cur] - 1 >= 0 and s[i - length[cur] - 1] == ch):
            cur = link[cur]
        if ch in nxt[cur]:
            last = nxt[cur][ch]
            occ[last] += 1
            continue
        node = len(length)
        length.append(length[cur] + 2)
        nxt.append({})
        occ.append(1)
        if length[node] == 1:
            link.append(1)
        else:
            p = link[cur]
            while not (i - length[p] - 1 >= 0 and s[i - length[p] - 1] == ch):
                p = link[p]
            link.append(nxt[p][ch])
        nxt[cur][ch] = node
        last = node
    for v in range(len(length) - 1, 1, -1):
        occ[link[v]] += occ[v]
    return sum(c * (c - 1) // 2 for c in occ[2:]) % MOD


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    s = input()
    result = palindromicBorder(s)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** The eertree has two roots (lengths −1 and 0). Nodes are created in increasing order and every suffix link points to an older node, so a single reverse pass propagates counts correctly.

```stdin
ababa
```

```stdout
5
```

### Two Two

**Problem.** Count the substrings of a digit string that are powers of two (`2^0 … 2^800`) written in decimal, without leading zeros.

**Idea.** There are only 801 patterns (the longest has 241 digits). Build an **Aho–Corasick** automaton over them once; then a single left-to-right pass over each string counts all occurrences: at every position add how many patterns end there (precomputed per state through the failure links).

**Steps.**
1. Insert `str(2**e)` for `e = 0..800` into a trie over digits.
2. BFS: compute failure links, complete the transition table, and `out[v]` = patterns ending at `v` + `out[fail[v]]`.
3. For each string, walk the automaton and sum `out[state]`.

```python
import os
from collections import deque


def build():
    goto, fail, out = [[-1] * 10], [0], [0]
    for e in range(801):
        node = 0
        for ch in str(2 ** e):
            d = ord(ch) - 48
            if goto[node][d] == -1:
                goto[node][d] = len(goto)
                goto.append([-1] * 10)
                fail.append(0)
                out.append(0)
            node = goto[node][d]
        out[node] += 1
    queue = deque()
    for d in range(10):
        if goto[0][d] == -1:
            goto[0][d] = 0
        else:
            queue.append(goto[0][d])
    while queue:
        u = queue.popleft()
        out[u] += out[fail[u]]
        for d in range(10):
            v = goto[u][d]
            if v == -1:
                goto[u][d] = goto[fail[u]][d]
            else:
                fail[v] = goto[fail[u]][d]
                queue.append(v)
    return goto, out


GOTO, OUT = build()


def twoTwo(a):
    node = total = 0
    for ch in a:
        node = GOTO[node][ord(ch) - 48]
        total += OUT[node]
    return total


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        fptr.write(str(twoTwo(input().strip())) + '\n')
    fptr.close()
```

**Watch out.** Powers of two never start with `0`, so the "no leading zero" rule is satisfied automatically by matching the patterns exactly.

```stdin
5
2222222
24256
65536
023223
33579
```

```stdout
7
4
1
4
0
```

### Two Strings Game

**Problem.** A position is a pair `(A', B')` of substrings of `A` and `B`. A move appends a letter to one of them so it stays a substring; a player with no move loses. Among the positions where the first player wins, sorted by `A'` then `B'`, print the `k`-th (or `no solution`).

**Idea.** Each string's moves form a game on its suffix automaton (a state's moves are its transitions), so each substring has a Grundy value: the mex of its children's values. The position is a sum of two games, so it's a first-player win exactly when `g(A') != g(B')`. Count, for every state, how many winning pairs start with a string in its subtree. Then walk the automaton of `A` in alphabetical order to find `A'`, and walk `B`'s automaton the same way to find `B'`.

**Steps.**
1. Build both suffix automata; compute Grundy values in decreasing-length order.
2. `cntB[g]` = number of substrings of `B` (including the empty one) with Grundy value `g`; a state holds `len[v] - len[link[v]]` substrings.
3. For `A`: `win(v) = |B'| total - cntB[g(v)]`; `T[v] = win(v) + Σ T[child]`.
4. Walk `A` with `k`, choosing "stop here" (if `k <= win(v)`) or descending into a child. Then, with `g = g(A')`, count the paths of `B` whose state has Grundy value ≠ `g` and walk `B` the same way.

```python
import os
import string


def sam(s):
    length, link, nxt = [0], [-1], [{}]
    last = 0
    for ch in s:
        cur = len(length)
        length.append(length[last] + 1)
        link.append(-1)
        nxt.append({})
        p = last
        while p != -1 and ch not in nxt[p]:
            nxt[p][ch] = cur
            p = link[p]
        if p == -1:
            link[cur] = 0
        else:
            q = nxt[p][ch]
            if length[p] + 1 == length[q]:
                link[cur] = q
            else:
                clone = len(length)
                length.append(length[p] + 1)
                link.append(link[q])
                nxt.append(dict(nxt[q]))
                while p != -1 and nxt[p].get(ch) == q:
                    nxt[p][ch] = clone
                    p = link[p]
                link[q] = link[cur] = clone
        last = cur
    order = sorted(range(len(length)), key=length.__getitem__, reverse=True)
    grundy = [0] * len(length)
    for v in order:
        seen = {grundy[u] for u in nxt[v].values()}
        g = 0
        while g in seen:
            g += 1
        grundy[v] = g
    return length, link, nxt, order, grundy


def twoStrings(k, a, b):
    la, _, na, oa, ga = sam(a)
    lb, linkb, nb, ob, gb = sam(b)
    cnt_b = {}
    for v in range(len(lb)):
        size = 1 if v == 0 else lb[v] - lb[linkb[v]]
        cnt_b[gb[v]] = cnt_b.get(gb[v], 0) + size
    total_b = sum(cnt_b.values())
    win = [total_b - cnt_b.get(g, 0) for g in ga]
    tree = win[:]
    for v in oa:
        tree[v] += sum(tree[u] for u in na[v].values())
    if k > tree[0]:
        return ["no solution"]
    v, a_res = 0, []
    while k > win[v]:
        k -= win[v]
        for c in string.ascii_lowercase:
            u = na[v].get(c)
            if u is None:
                continue
            if k <= tree[u]:
                a_res.append(c)
                v = u
                break
            k -= tree[u]
    target = ga[v]
    paths = [int(g != target) for g in gb]
    for w in ob:
        paths[w] += sum(paths[u] for u in nb[w].values())
    w, b_res = 0, []
    while True:
        if gb[w] != target:
            if k == 1:
                break
            k -= 1
        for c in string.ascii_lowercase:
            u = nb[w].get(c)
            if u is None:
                continue
            if k <= paths[u]:
                b_res.append(c)
                w = u
                break
            k -= paths[u]
    return ["".join(a_res), "".join(b_res)]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, m, k = map(int, input().split())
    a = input()
    b = input()
    result = twoStrings(k, a, b)
    fptr.write('\n'.join(result))
    fptr.write('\n')
    fptr.close()
```

**Watch out.** The empty string is a valid `A'` or `B'` (the game can start from it), and it comes first in the order. Counts reach 10¹⁸, which Python's integers handle directly.

```stdin
2 1 3
ab
c
```

```stdout
a
c
```

### Letter Islands

**Problem.** A substring `p` marks every position covered by one of its occurrences; the marked positions form "islands". Count the distinct substrings that produce exactly `k` islands.

**Idea.** In a suffix automaton, all strings of one state share the same end positions `E`; a string of length `L` has occurrences `[e-L+1, e]`. Two consecutive occurrences merge when their end positions differ by at most `L`, so `islands(L) = |E| - (number of gaps <= L)`. For the state's length range, the lengths giving exactly `k` islands form one interval between two consecutive sorted gaps. Build `E` and the sorted gaps bottom-up over the suffix-link tree, merging smaller sets into larger ones.

**Steps.**
1. Build the suffix automaton; each non-clone state starts with its own end position.
2. Process states by decreasing length: with `t = |E| - k`, the valid lengths are `[gaps[t-1], gaps[t] - 1]` ∩ `[len(link)+1, len(v)]`; add that count.
3. Merge the state's sorted end positions into its link (small into large), updating the sorted gap list on each insertion.

```python
import os
from bisect import bisect_left, insort


def letterIslands(s, k):
    length, link, nxt, endpos = [0], [-1], [{}], [None]
    last = 0
    for i, ch in enumerate(s):
        cur = len(length)
        length.append(length[last] + 1)
        link.append(-1)
        nxt.append({})
        endpos.append(i)
        p = last
        while p != -1 and ch not in nxt[p]:
            nxt[p][ch] = cur
            p = link[p]
        if p == -1:
            link[cur] = 0
        else:
            q = nxt[p][ch]
            if length[p] + 1 == length[q]:
                link[cur] = q
            else:
                clone = len(length)
                length.append(length[p] + 1)
                link.append(link[q])
                nxt.append(dict(nxt[q]))
                endpos.append(None)
                while p != -1 and nxt[p].get(ch) == q:
                    nxt[p][ch] = clone
                    p = link[p]
                link[q] = link[cur] = clone
        last = cur
    E = [[e] if e is not None else [] for e in endpos]
    G = [[] for _ in endpos]

    def insert(es, gs, x):
        i = bisect_left(es, x)
        if 0 < i < len(es):
            gs.pop(bisect_left(gs, es[i] - es[i - 1]))
        if i > 0:
            insort(gs, x - es[i - 1])
        if i < len(es):
            insort(gs, es[i] - x)
        es.insert(i, x)

    total = 0
    for v in sorted(range(1, len(length)), key=length.__getitem__, reverse=True):
        es, gs = E[v], G[v]
        t = len(es) - k
        if 0 <= t <= len(gs):
            lo = max(gs[t - 1] if t > 0 else 1, length[link[v]] + 1)
            hi = min(gs[t] - 1 if t < len(gs) else length[v], length[v])
            if lo <= hi:
                total += hi - lo + 1
        p = link[v]
        if p > 0:
            if len(E[p]) < len(es):
                E[p], E[v], G[p], G[v] = es, E[p], gs, G[p]
                es, gs = E[v], G[v]
            for x in es:
                insert(E[p], G[p], x)
        E[v] = G[v] = None
    return total


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    s = input()
    k = int(input().strip())
    result = letterIslands(s, k)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Occurrences that merely touch (gap exactly `L`) also join into one island; that's why the condition is `gap <= L`.

```stdin
abaab
2
```

```stdout
3
```

### Pseudo-Isomorphic Substrings

**Problem.** Two strings are pseudo-isomorphic if they have the same pattern of equal letters (a consistent renaming). For every prefix of `S`, print how many substrings of that prefix are pairwise non-isomorphic (the number of different patterns).

**Idea.** Encode a substring by, for each position, the distance back to the previous occurrence of the same letter **inside the substring** (0 if none). Isomorphic strings have identical encodings. Hash the encodings of all substrings, extending each start position to the right, and record for each pattern the earliest end position where it first appears; the answer for a prefix is the number of patterns whose first end is inside it.

**Steps.**
1. `prev[j]` = previous index of `s[j]` (or −1).
2. For each start `i`, extend `j` rightwards, appending `j - prev[j]` if `prev[j] >= i` else 0 to a rolling hash (with the length in the key).
3. Keep the minimum end `j` per pattern; prefix-sum those first-ends.

```python
import os

MOD = (1 << 61) - 1
BASE = 1_000_003


def pseudoIsomorphicSubstrings(s):
    n = len(s)
    prev, last = [-1] * n, {}
    for j, ch in enumerate(s):
        prev[j] = last.get(ch, -1)
        last[ch] = j
    first_end = {}
    for i in range(n):
        h = 0
        for j in range(i, n):
            h = (h * BASE + (j - prev[j] if prev[j] >= i else 0) + 1) % MOD
            key = (h, j - i)
            if first_end.get(key, n) > j:
                first_end[key] = j
    counts = [0] * n
    for j in first_end.values():
        counts[j] += 1
    out, running = [], 0
    for c in counts:
        running += c
        out.append(running)
    return out


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    s = input().strip()
    result = pseudoIsomorphicSubstrings(s)
    fptr.write('\n'.join(map(str, result)))
    fptr.write('\n')
    fptr.close()
```

**Watch out.** This is O(n²) time and memory, so it handles strings of a few thousand characters. The full limit (10⁵) needs a parameterized suffix tree, which is not practical in Python.

```stdin
abbabab
```

```stdout
1
2
4
6
9
12
15
```

### How Many Substrings?

**Problem.** For many queries `[left, right]`, count the distinct substrings of `s[left..right]`.

**Idea.** The number of distinct substrings of a string equals `Σ (len[v] - len[link[v]])` over the states of its suffix automaton. Build the automaton of each queried substring (caching repeated queries).

**Steps.**
1. For a query, build the suffix automaton of `s[left:right+1]`.
2. Return the sum of `len[v] - len[link[v]]` over non-root states.

```python
import os


def distinct_substrings(t):
    length, link, nxt = [0], [-1], [{}]
    last = 0
    for ch in t:
        cur = len(length)
        length.append(length[last] + 1)
        link.append(-1)
        nxt.append({})
        p = last
        while p != -1 and ch not in nxt[p]:
            nxt[p][ch] = cur
            p = link[p]
        if p == -1:
            link[cur] = 0
        else:
            q = nxt[p][ch]
            if length[p] + 1 == length[q]:
                link[cur] = q
            else:
                clone = len(length)
                length.append(length[p] + 1)
                link.append(link[q])
                nxt.append(dict(nxt[q]))
                while p != -1 and nxt[p].get(ch) == q:
                    nxt[p][ch] = clone
                    p = link[p]
                link[q] = link[cur] = clone
        last = cur
    return sum(length[v] - length[link[v]] for v in range(1, len(length)))


def countSubstrings(s, queries):
    cache = {}
    out = []
    for left, right in queries:
        key = (left, right)
        if key not in cache:
            cache[key] = distinct_substrings(s[left:right + 1])
        out.append(cache[key])
    return out


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, q = map(int, input().split())
    s = input()
    queries = [list(map(int, input().rstrip().split())) for _ in range(q)]
    result = countSubstrings(s, queries)
    fptr.write('\n'.join(map(str, result)))
    fptr.write('\n')
    fptr.close()
```

**Watch out.** Each query is O(length), so the worst case is O(n·q). The full constraints need an offline sweep over right ends with a link-cut tree on the suffix tree, which is very hard to make fast in Python.

```stdin
5 5
aabaa
1 1
1 4
1 1
1 4
0 2
```

```stdout
1
8
1
8
5
```
