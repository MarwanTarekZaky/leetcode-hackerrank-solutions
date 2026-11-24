## Strings

### Super Reduced String

**Problem.** Repeatedly delete pairs of equal adjacent letters. Return what's left, or `Empty String`.

**Idea.** A stack does all the deletions in one pass: if the new letter equals the top, both disappear (pop); otherwise push it.

**Steps.**
1. For each letter: pop if it matches the top, else push.
2. Join the stack, or return `Empty String` if it's empty.

```python
import os


def superReducedString(s):
    stack = []
    for ch in s:
        if stack and stack[-1] == ch:
            stack.pop()
        else:
            stack.append(ch)
    return "".join(stack) or "Empty String"


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    s = input()
    result = superReducedString(s)
    fptr.write(result + '\n')
    fptr.close()
```

**Watch out.** Deleting and rescanning the string is O(n²); the stack makes it O(n), and it handles chains like `abba` automatically.

```stdin
aaabccddd
```

```stdout
abd
```

### CamelCase

**Problem.** Count the words in a camelCase string.

**Idea.** Every word after the first starts with an uppercase letter.

**Steps.**
1. Return `1 + number of uppercase letters`.

```python
import os


def camelcase(s):
    return 1 + sum(ch.isupper() for ch in s)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    s = input()
    result = camelcase(s)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** The first word is all lowercase, hence the `1 +`.

```stdin
saveChangesInTheEditor
```

```stdout
5
```

### Strong Password

**Problem.** A strong password has length ≥ 6 and at least one digit, lowercase letter, uppercase letter and special character. Return the minimum number of characters to add.

**Idea.** Each missing character type needs one added character, and the length must reach 6. Added characters can serve both purposes, so the answer is the larger of the two needs.

**Steps.**
1. `missing` = number of the four types not present.
2. Return `max(missing, 6 - n)`.

```python
import os


def minimumNumber(n, password):
    groups = ["0123456789", "abcdefghijklmnopqrstuvwxyz", "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "!@#$%^&*()-+"]
    missing = sum(not any(ch in g for ch in password) for g in groups)
    return max(missing, 6 - n)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    password = input()
    answer = minimumNumber(n, password)
    fptr.write(str(answer) + '\n')
    fptr.close()
```

**Watch out.** Don't add the two needs together: one added `!` can fix both a missing special character and a short length.

```stdin
3
Ab1
```

```stdout
3
```

### Two Characters

**Problem.** Delete all occurrences of some letters so that only two letters remain and they alternate (`abab...`). Return the longest possible length, or 0.

**Idea.** The two letters that remain decide everything. Try every pair of distinct letters in the string, keep only those two, and check that no two neighbours are equal.

**Steps.**
1. For each pair `(x, y)` of distinct letters: `t` = the letters of `s` that are `x` or `y`.
2. If no two adjacent letters of `t` are equal, `len(t)` is a candidate.
3. Return the best candidate (0 if none).

```python
import os
from itertools import combinations


def alternate(s):
    best = 0
    for x, y in combinations(set(s), 2):
        t = [ch for ch in s if ch == x or ch == y]
        if all(a != b for a, b in zip(t, t[1:])):
            best = max(best, len(t))
    return best


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    l = int(input().strip())
    s = input()
    result = alternate(s)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** At most 26·25/2 = 325 pairs, each checked in O(n): fast enough.

```stdin
10
beabeefeab
```

```stdout
5
```

### Caesar Cipher

**Problem.** Shift every letter `k` places forward in the alphabet (wrapping around), keeping case; leave other characters unchanged.

**Idea.** Map a letter to `0..25`, add `k`, take `% 26`, map back. Build a translation table once with `str.maketrans`.

**Steps.**
1. Rotate the lowercase and uppercase alphabets by `k % 26`.
2. Translate the string with that table.

```python
import os
import string


def caesarCipher(s, k):
    k %= 26
    low, up = string.ascii_lowercase, string.ascii_uppercase
    table = str.maketrans(low + up, low[k:] + low[:k] + up[k:] + up[:k])
    return s.translate(table)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    s = input()
    k = int(input().strip())
    result = caesarCipher(s, k)
    fptr.write(result + '\n')
    fptr.close()
```

**Watch out.** `k` can be up to 100, so reduce it with `% 26` first.

```stdin
11
middle-Outz
2
```

```stdout
okffng-Qwvb
```

### Mars Exploration

**Problem.** The message should be `SOS` repeated. Count the letters that differ.

**Idea.** Compare position `i` with `"SOS"[i % 3]`.

**Steps.**
1. Count `i` where `s[i] != "SOS"[i % 3]`.

```python
import os


def marsExploration(s):
    return sum(ch != "SOS"[i % 3] for i, ch in enumerate(s))


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    s = input()
    result = marsExploration(s)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Count changed **letters**, not changed `SOS` blocks.

```stdin
SOSSPSSQSSOR
```

```stdout
3
```

### HackerRank in a String!

**Problem.** Does the string contain `hackerrank` as a subsequence?

**Idea.** Walk through the string once, matching the letters of `hackerrank` in order.

**Steps.**
1. Make an iterator over `s`.
2. `all(ch in it for ch in "hackerrank")`: each `in` consumes the iterator up to the match, so order is respected.

```python
import os


def hackerrankInString(s):
    it = iter(s)
    return "YES" if all(ch in it for ch in "hackerrank") else "NO"


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        fptr.write(hackerrankInString(input()) + '\n')
    fptr.close()
```

**Watch out.** `ch in it` on an **iterator** consumes it, which is exactly what makes this a subsequence check. With the plain string it would ignore order.

```stdin
2
hereiamstackerrank
hackerworld
```

```stdout
YES
NO
```

### Pangrams

**Problem.** Does a sentence contain every letter of the alphabet (ignoring case)?

**Idea.** Collect the lowercase letters in a set and check that all 26 are there.

**Steps.**
1. Return `pangram` if `set(string.ascii_lowercase) <= set(s.lower())`, else `not pangram`.

```python
import os
import string


def pangrams(s):
    return "pangram" if set(string.ascii_lowercase) <= set(s.lower()) else "not pangram"


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    s = input()
    result = pangrams(s)
    fptr.write(result + '\n')
    fptr.close()
```

**Watch out.** Spaces end up in the set too; the subset test (`<=`) ignores them.

```stdin
We promptly judged antique ivory buckles for the next prize
```

```stdout
pangram
```

### Weighted Uniform Strings

**Problem.** Letter weights are `a = 1 ... z = 26`. A uniform substring is one letter repeated; its weight is the sum. For each query, say whether some uniform substring has that weight.

**Idea.** For a run of `c` repeated `k` times, the possible weights are `w, 2w, ..., kw`. Put all of them in a set, then answer each query in O(1).

**Steps.**
1. Walk the string; track the current run length; add `weight(c) * run_length` to a set at every character.
2. For each query, return `Yes` if it's in the set.

```python
import os


def weightedUniformStrings(s, queries):
    weights, run, prev = set(), 0, ""
    for ch in s:
        run = run + 1 if ch == prev else 1
        prev = ch
        weights.add((ord(ch) - 96) * run)
    return ["Yes" if q in weights else "No" for q in queries]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    s = input()
    queries_count = int(input().strip())
    queries = [int(input().strip()) for _ in range(queries_count)]
    result = weightedUniformStrings(s, queries)
    fptr.write('\n'.join(result))
    fptr.write('\n')
    fptr.close()
```

**Watch out.** Only **contiguous** runs count: `aba` gives weights 1 and 2, but not 2 for `aa`.

```stdin
abccddde
6
1
3
12
5
9
10
```

```stdout
Yes
Yes
Yes
Yes
No
No
```

### Separate the Numbers

**Problem.** Can a digit string be split into two or more increasing consecutive numbers (`1, 2, 3` or `99, 100`) without leading zeros? Print `YES x` with the first number, or `NO`.

**Idea.** The first number decides the whole sequence. Try every possible first number (length 1 up to half the string), build `x, x+1, x+2, ...` as text until it's at least as long as `s`, and compare.

**Steps.**
1. For each length `L` from 1 to `len(s) // 2`: `x = int(s[:L])`.
2. Concatenate `x, x+1, ...` until the result is at least `len(s)` long.
3. If it equals `s` (and `s` has no leading zero), print `YES x` and stop. Otherwise print `NO`.

```python
def separateNumbers(s):
    if s[0] != "0":
        for length in range(1, len(s) // 2 + 1):
            first = int(s[:length])
            built, nxt = "", first
            while len(built) < len(s):
                built += str(nxt)
                nxt += 1
            if built == s:
                print("YES", first)
                return
    print("NO")


if __name__ == '__main__':
    q = int(input().strip())
    for _ in range(q):
        separateNumbers(input())
```

**Watch out.** Building with `str(x)` handles digit-count changes (`99 → 100`) and rejects leading zeros automatically, since `str` never produces them.

```stdin
7
1234
91011
99100
101103
010203
13
1
```

```stdout
YES 1
YES 9
YES 99
NO
NO
NO
NO
```

### Funny String

**Problem.** A string is funny if the absolute differences between neighbouring ASCII codes are the same as for its reverse.

**Idea.** The reverse's difference list is the original list reversed, so the string is funny exactly when its difference list is a palindrome.

**Steps.**
1. `d = [abs(ord(s[i+1]) - ord(s[i]))]`.
2. Return `Funny` if `d == d[::-1]`.

```python
import os


def funnyString(s):
    d = [abs(ord(a) - ord(b)) for a, b in zip(s, s[1:])]
    return "Funny" if d == d[::-1] else "Not Funny"


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        fptr.write(funnyString(input()) + '\n')
    fptr.close()
```

**Watch out.** You don't need to build the reversed string at all.

```stdin
2
acxz
bcxz
```

```stdout
Funny
Not Funny
```

### Gemstones

**Problem.** A mineral is a gemstone if it appears in every rock. Count the gemstones.

**Idea.** Intersect the sets of letters of all rocks.

**Steps.**
1. Return `len(set.intersection(*map(set, arr)))`.

```python
import os


def gemstones(arr):
    return len(set.intersection(*map(set, arr)))


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    arr = [input() for _ in range(n)]
    result = gemstones(arr)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Duplicates inside one rock don't matter; sets ignore them.

```stdin
3
abcdde
baccd
eeabg
```

```stdout
2
```

### Alternating Characters

**Problem.** Delete the minimum number of characters from a string of `A`s and `B`s so that no two neighbours are equal.

**Idea.** Inside each run of equal letters you keep one and delete the rest, which is the number of positions equal to the previous one.

**Steps.**
1. Count `i` with `s[i] == s[i - 1]`.

```python
import os


def alternatingCharacters(s):
    return sum(a == b for a, b in zip(s, s[1:]))


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        fptr.write(str(alternatingCharacters(input())) + '\n')
    fptr.close()
```

**Watch out.** No need to actually delete anything; just count.

```stdin
5
AAAA
BBBBB
ABABABAB
BABABA
AAABBB
```

```stdout
3
4
0
0
4
```

### Beautiful Binary String

**Problem.** Flip the fewest bits so the string no longer contains `010`.

**Idea.** Scan left to right; each time you meet `010`, flip its last `0` to `1`. That breaks this occurrence and any that would overlap it, so each non-overlapping occurrence costs exactly one flip.

**Steps.**
1. Return `b.count("010")` (`str.count` counts non-overlapping occurrences).

```python
import os


def beautifulBinaryString(b):
    return b.count("010")


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    b = input()
    result = beautifulBinaryString(b)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** `01010` contains two overlapping `010`s but one flip (the middle `0`) fixes both, and `count` returns 1 here as well.

```stdin
7
0101010
```

```stdout
2
```

### The Love-Letter Mystery

**Problem.** Make the string a palindrome; each operation lowers one letter by 1. Return the minimum number of operations.

**Idea.** For each mirrored pair, lower the bigger letter to match the smaller one: cost `|difference|`.

**Steps.**
1. Sum `abs(ord(s[i]) - ord(s[-1 - i]))` over the first half.

```python
import os


def theLoveLetterMystery(s):
    return sum(abs(ord(s[i]) - ord(s[-1 - i])) for i in range(len(s) // 2))


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        fptr.write(str(theLoveLetterMystery(input())) + '\n')
    fptr.close()
```

**Watch out.** Only the first half is needed; summing the whole string counts each pair twice.

```stdin
4
abc
abcba
abcd
cba
```

```stdout
2
0
4
2
```

### Determining DNA Health

**Problem.** Genes `g[i]` have health `h[i]`. For each DNA strand, only genes with index in `[first, last]` count; its health is the sum of the health of every occurrence of those genes as substrings. Print the minimum and maximum strand health.

**Idea.** Searching every gene in every strand is too slow. Build an **Aho–Corasick** automaton over the distinct gene strings, so one pass over a strand finds all gene occurrences. For each distinct gene string, keep the sorted list of its indices and prefix sums of their health; a binary search then gives the health of the indices inside `[first, last]` in O(log n).

**Steps.**
1. Build a trie of the distinct gene strings, then BFS to set failure links and "dictionary links" (the nearest suffix that is a whole gene).
2. For each gene string, store its indices and the prefix sums of their health.
3. For each strand, walk the automaton; at every position follow the dictionary links and add `prefix[hi] - prefix[lo]` for each gene found (`lo`, `hi` from `bisect`).
4. Print the minimum and maximum totals.

```python
import sys
from bisect import bisect_left, bisect_right
from collections import deque


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    genes = data[1:1 + n]
    health = list(map(int, data[1 + n:1 + 2 * n]))
    s = int(data[1 + 2 * n])
    queries = data[2 + 2 * n:]

    info = {}
    for i, g in enumerate(genes):
        info.setdefault(g, ([], [0]))
        idx, pref = info[g]
        idx.append(i)
        pref.append(pref[-1] + health[i])

    goto, fail, word, dict_link = [{}], [0], [None], [0]
    for g in info:
        node = 0
        for ch in g:
            if ch not in goto[node]:
                goto[node][ch] = len(goto)
                goto.append({})
                fail.append(0)
                word.append(None)
                dict_link.append(0)
            node = goto[node][ch]
        word[node] = g
    queue = deque(goto[0].values())
    while queue:
        u = queue.popleft()
        for ch, v in goto[u].items():
            f = fail[u]
            while f and ch not in goto[f]:
                f = fail[f]
            fail[v] = goto[f].get(ch, 0) if goto[f].get(ch, 0) != v else 0
            dict_link[v] = fail[v] if word[fail[v]] is not None else dict_link[fail[v]]
            queue.append(v)

    totals = []
    for q in range(s):
        first, last, dna = int(queries[3 * q]), int(queries[3 * q + 1]), queries[3 * q + 2]
        node, total = 0, 0
        for ch in dna:
            while node and ch not in goto[node]:
                node = fail[node]
            node = goto[node].get(ch, 0)
            t = node if word[node] is not None else dict_link[node]
            while t:
                idx, pref = info[word[t]]
                total += pref[bisect_right(idx, last)] - pref[bisect_left(idx, first)]
                t = dict_link[t]
        totals.append(total)
    print(min(totals), max(totals))


if __name__ == '__main__':
    main()
```

**Watch out.**
- The same gene string can appear at several indices with different health values; group them by string, not by index.
- Total input is up to 2·10⁶ characters: read everything at once with `sys.stdin.read()`, and choose PyPy 3 on HackerRank for the heaviest tests.

```stdin
6
a b c aa d b
1 2 3 4 5 6
3
1 5 caaab
0 4 xyz
2 4 bcdybc
```

```stdout
0 19
```

### Palindrome Index

**Problem.** Return the index of one character whose removal makes the string a palindrome, or `-1` if it's already a palindrome (or impossible).

**Idea.** Move two pointers inward until the first mismatch `(i, j)`. The removed character must be `s[i]` or `s[j]`: check whether skipping `i` leaves a palindrome; if so answer `i`, otherwise try `j`.

**Steps.**
1. Find the first mismatch from both ends. None → `-1`.
2. If `s[i+1 .. j]` is a palindrome → `i`; elif `s[i .. j-1]` is → `j`; else `-1`.

```python
import os


def palindromeIndex(s):
    i, j = 0, len(s) - 1
    while i < j and s[i] == s[j]:
        i += 1
        j -= 1
    if i >= j:
        return -1
    if s[i + 1:j + 1] == s[i + 1:j + 1][::-1]:
        return i
    if s[i:j] == s[i:j][::-1]:
        return j
    return -1


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        fptr.write(str(palindromeIndex(input())) + '\n')
    fptr.close()
```

**Watch out.** Checking only `s[i+1] == s[j]` isn't enough (`aaab...` patterns); verify the whole remaining middle.

```stdin
3
aaab
baa
aaa
```

```stdout
3
0
-1
```

### Anagram

**Problem.** Split a string into two equal halves. How many characters of the first half must change to make the halves anagrams? Return `-1` for odd length.

**Idea.** Count the letters of both halves; every letter the first half has in excess must be changed.

**Steps.**
1. Odd length → `-1`.
2. Return `sum((Counter(first) - Counter(second)).values())`.

```python
import os
from collections import Counter


def anagram(s):
    if len(s) % 2:
        return -1
    half = len(s) // 2
    return sum((Counter(s[:half]) - Counter(s[half:])).values())


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        fptr.write(str(anagram(input())) + '\n')
    fptr.close()
```

**Watch out.** `Counter` subtraction drops non-positive counts, which is exactly "the excess".

```stdin
6
aaabbb
ab
abc
mnop
xyyx
xaxbbbxx
```

```stdout
3
1
-1
2
0
1
```

### Making Anagrams

**Problem.** Delete the fewest characters from two strings so that they become anagrams.

**Idea.** For every letter, delete the difference between its counts in the two strings.

**Steps.**
1. Return `sum((c1 - c2).values()) + sum((c2 - c1).values())`.

```python
import os
from collections import Counter


def makingAnagrams(s1, s2):
    c1, c2 = Counter(s1), Counter(s2)
    return sum((c1 - c2).values()) + sum((c2 - c1).values())


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    s1 = input()
    s2 = input()
    result = makingAnagrams(s1, s2)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** Unlike *Anagram*, you delete from **both** strings, so count both differences.

```stdin
cde
abc
```

```stdout
4
```

### Game of Thrones - I

**Problem.** Can the string be rearranged into a palindrome?

**Idea.** A palindrome pairs up letters around the centre, so at most one letter may appear an odd number of times.

**Steps.**
1. Count letters with odd frequency; return `YES` if there is at most one.

```python
import os
from collections import Counter


def gameOfThrones(s):
    odd = sum(c % 2 for c in Counter(s).values())
    return "YES" if odd <= 1 else "NO"


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    s = input()
    result = gameOfThrones(s)
    fptr.write(result + '\n')
    fptr.close()
```

**Watch out.** This works for both even and odd lengths.

```stdin
aaabbbb
```

```stdout
YES
```

### Two Strings

**Problem.** Do two strings share a common substring?

**Idea.** Any common substring contains a common single letter, so just check whether they share a letter.

**Steps.**
1. Return `YES` if the letter sets intersect.

```python
import os


def twoStrings(s1, s2):
    return "YES" if set(s1) & set(s2) else "NO"


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        s1 = input()
        s2 = input()
        fptr.write(twoStrings(s1, s2) + '\n')
    fptr.close()
```

**Watch out.** Comparing all substrings is a trap; the one-letter observation makes it O(n).

```stdin
2
hello
world
hi
world
```

```stdout
YES
NO
```

### String Construction

**Problem.** Build a string by appending one character (cost 1) or copying any existing substring to the end (free). Return the minimum cost.

**Idea.** Each distinct letter must be typed once; after that, any letter already present can be copied for free.

**Steps.**
1. Return `len(set(s))`.

```python
import os


def stringConstruction(s):
    return len(set(s))


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        fptr.write(str(stringConstruction(input())) + '\n')
    fptr.close()
```

**Watch out.** Copying a single letter is a valid "substring copy", which is why the answer is just the number of distinct letters.

```stdin
2
abcd
abab
```

```stdout
4
2
```

### Sherlock and the Valid String

**Problem.** A string is valid if all letters occur equally often, or if removing one single character makes that true.

**Idea.** Look at the frequencies of the frequencies. Valid cases: all equal; or two frequency values where one letter appears exactly once (remove it), or one letter appears exactly one time more than all others (remove one of it).

**Steps.**
1. `freq = Counter(Counter(s).values())` (frequency → how many letters have it).
2. One key → `YES`.
3. Two keys `a < b`: `YES` if (`a == 1` and one letter has it) or (`b == a + 1` and one letter has it).
4. Otherwise `NO`.

```python
import os
from collections import Counter


def isValid(s):
    freq = Counter(Counter(s).values())
    if len(freq) == 1:
        return "YES"
    if len(freq) == 2:
        (a, count_a), (b, count_b) = sorted(freq.items())
        if (a == 1 and count_a == 1) or (b == a + 1 and count_b == 1):
            return "YES"
    return "NO"


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    s = input()
    result = isValid(s)
    fptr.write(result + '\n')
    fptr.close()
```

**Watch out.** The tricky case is a single letter that appears once among letters that appear many times (`aabbccd`): removing it is valid.

```stdin
aabbcd
```

```stdout
NO
```

### Highest Value Palindrome

**Problem.** Change at most `k` digits to make the number a palindrome with the largest possible value. Return `-1` if impossible.

**Idea.** First, make it a palindrome cheaply: for each mismatched pair, change the smaller digit to the larger (1 change each). If that already needs more than `k`, it's impossible. Then spend what's left from the outside in, upgrading pairs to `9`: a pair already changed costs 1 more, an untouched pair costs 2. A leftover change can upgrade the middle digit.

**Steps.**
1. Pass 1: fix mismatches with the larger digit; remember which pairs were changed.
2. If changes > `k` → `-1`.
3. Pass 2 from the outside: for a pair not already `9`, use 1 change if it was changed in pass 1, else 2 if available.
4. If the length is odd and a change remains, set the middle to `9`.

```python
import os


def highestValuePalindrome(s, n, k):
    s = list(s)
    changed = [False] * n
    used = 0
    for i in range(n // 2):
        j = n - 1 - i
        if s[i] != s[j]:
            s[i] = s[j] = max(s[i], s[j])
            changed[i] = True
            used += 1
    if used > k:
        return "-1"
    left = k - used
    for i in range(n // 2):
        j = n - 1 - i
        if s[i] != "9":
            if changed[i] and left >= 1:
                s[i] = s[j] = "9"
                left -= 1
            elif not changed[i] and left >= 2:
                s[i] = s[j] = "9"
                left -= 2
    if n % 2 and left >= 1:
        s[n // 2] = "9"
    return "".join(s)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, k = map(int, input().split())
    s = input()
    result = highestValuePalindrome(s, n, k)
    fptr.write(result + '\n')
    fptr.close()
```

**Watch out.** A pair fixed in pass 1 already used one change; upgrading it to `9` only costs one more, not two. Forgetting this is the classic bug.

```stdin
4 1
3943
```

```stdout
3993
```

### Maximum Palindromes

**Problem.** For many queries `[l, r]`, count the maximum-length palindromes that can be made from the letters of `s[l..r]`, modulo 10⁹+7.

**Idea.** A longest palindrome uses `c // 2` pairs of each letter on the left half (and mirrors them), plus one odd letter in the middle if any. The count is the number of arrangements of the left half (a multinomial), times the number of choices for the middle letter.

**Steps.**
1. Prefix counts per letter give the letter counts of any range in O(26).
2. Precompute factorials and inverse factorials mod `p`.
3. Answer = `(Σ pairs)! / Π (pairs!)` × `max(1, number of letters with odd count)`.

```python
import os

MOD = 10 ** 9 + 7


def initialize(s):
    global prefix, fact, inv_fact
    n = len(s)
    prefix = [[0] * 26]
    for ch in s:
        row = prefix[-1][:]
        row[ord(ch) - 97] += 1
        prefix.append(row)
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = fact[i - 1] * i % MOD
    inv_fact = [1] * (n + 1)
    inv_fact[n] = pow(fact[n], MOD - 2, MOD)
    for i in range(n, 0, -1):
        inv_fact[i - 1] = inv_fact[i] * i % MOD


def answerQuery(l, r):
    counts = [b - a for a, b in zip(prefix[l - 1], prefix[r])]
    pairs = [c // 2 for c in counts]
    odd = sum(c % 2 for c in counts)
    result = fact[sum(pairs)]
    for p in pairs:
        result = result * inv_fact[p] % MOD
    return result * max(1, odd) % MOD


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    s = input()
    initialize(s)
    q = int(input().strip())
    for _ in range(q):
        l, r = map(int, input().split())
        fptr.write(str(answerQuery(l, r)) + '\n')
    fptr.close()
```

**Watch out.** Division modulo a prime uses the modular inverse (Fermat: `x^(p-2)`), precomputed once for all factorials.

```stdin
week
2
1 4
2 3
```

```stdout
2
1
```

### Sherlock and Anagrams

**Problem.** Count pairs of substrings (at different positions) that are anagrams of each other.

**Idea.** Two substrings are anagrams when their sorted letters are equal. Group all substrings by that signature; a group of size `c` gives `c·(c-1)/2` pairs.

**Steps.**
1. For every substring, add `''.join(sorted(sub))` to a counter.
2. Sum `c * (c - 1) // 2` over the counts.

```python
import os
from collections import Counter


def sherlockAndAnagrams(s):
    groups = Counter("".join(sorted(s[i:j])) for i in range(len(s)) for j in range(i + 1, len(s) + 1))
    return sum(c * (c - 1) // 2 for c in groups.values())


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    q = int(input().strip())
    for _ in range(q):
        fptr.write(str(sherlockAndAnagrams(input())) + '\n')
    fptr.close()
```

**Watch out.** `n <= 100` gives about 5,000 substrings, so sorting each is fine. Pairs only form between substrings of the same length, which the signature already guarantees.

```stdin
2
abba
abcd
```

```stdout
4
0
```

### Common Child

**Problem.** Return the length of the longest common subsequence of two strings (up to 5000 characters each).

**Idea.** Classic LCS dynamic programming: `dp[i][j]` = LCS of the first `i` and `j` characters. Only the previous row is needed.

**Steps.**
1. `prev` = row of zeros.
2. For each character `a` of `s1`, build `cur`: on a match `prev[j] + 1`, otherwise `max(prev[j + 1], cur[j])`.
3. Return the last value.

```python
import os


def commonChild(s1, s2):
    prev = [0] * (len(s2) + 1)
    for a in s1:
        cur = [0]
        for j, b in enumerate(s2):
            cur.append(prev[j] + 1 if a == b else max(prev[j + 1], cur[j]))
        prev = cur
    return prev[-1]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    s1 = input()
    s2 = input()
    result = commonChild(s1, s2)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** 5000 × 5000 = 25 million steps is slow in CPython; select **PyPy 3** on HackerRank to pass the large tests.

```stdin
HARRY
SALLY
```

```stdout
2
```

### Bear and Steady Gene

**Problem.** A gene of length `n` (letters `ACGT`) is steady if each letter appears `n/4` times. Replace one substring (with anything of the same length) to make it steady. Return the shortest such substring.

**Idea.** Outside the replaced window, no letter may exceed `n/4`. So the window must contain the "excess" of every letter. Find the shortest window that does, with two pointers.

**Steps.**
1. Count letters; already steady → 0.
2. Move `right` across the gene, removing each letter from the "outside" counts.
3. While every outside count is `<= n/4`, record the window length and move `left` forward, putting its letter back outside.

```python
import os
from collections import Counter


def steadyGene(gene):
    n, target = len(gene), len(gene) // 4
    outside = Counter(gene)
    if all(outside[c] <= target for c in "ACGT"):
        return 0
    best, left = n, 0
    for right, ch in enumerate(gene):
        outside[ch] -= 1
        while left <= right and all(outside[c] <= target for c in "ACGT"):
            best = min(best, right - left + 1)
            outside[gene[left]] += 1
            left += 1
    return best


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    gene = input()
    result = steadyGene(gene)
    fptr.write(str(result) + '\n')
    fptr.close()
```

**Watch out.** The window can contain any letters; you only need what's **outside** it to be within the limit.

```stdin
8
GAAATAAA
```

```stdout
5
```

### Morgan and a String

**Problem.** Two stacks of letters; repeatedly take the top letter of either stack. Build the lexicographically smallest string.

**Idea.** Take from the stack whose **remaining suffix** is smaller. Append a sentinel larger than every letter (`z`) to both, so that when one suffix is a prefix of the other, the longer one is preferred. To compare suffixes in O(1), rank all suffixes of `a + 'z' + b + 'z'` with a suffix array.

**Steps.**
1. Build `t = a + 'z' + b + 'z'` and its suffix ranks (prefix doubling).
2. Two pointers `i` in `a` and `j` in `b`: take from `a` if `rank[i] < rank[len(a) + 1 + j]`, else from `b`.
3. When one side is used up, append the rest of the other.

```python
import os


def suffix_ranks(t):
    n = len(t)
    rank = [ord(c) for c in t]
    k = 1
    while True:
        key = [(rank[i], rank[i + k] if i + k < n else -1) for i in range(n)]
        order = sorted(range(n), key=key.__getitem__)
        new = [0] * n
        for a, b in zip(order, order[1:]):
            new[b] = new[a] + (key[a] != key[b])
        rank = new
        if rank[order[-1]] == n - 1:
            return rank
        k *= 2


def morganAndString(a, b):
    t = a + "z" + b + "z"
    rank = suffix_ranks(t)
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        if rank[i] < rank[len(a) + 1 + j]:
            out.append(a[i])
            i += 1
        else:
            out.append(b[j])
            j += 1
    return "".join(out) + a[i:] + b[j:]


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input().strip())
    for _ in range(t):
        a = input()
        b = input()
        fptr.write(morganAndString(a, b) + '\n')
    fptr.close()
```

**Watch out.** Comparing only the next letters fails on ties (`CAB` vs `CAA`); comparing slices `a[i:] < b[j:]` is correct but O(n) per step, which is O(n²) overall on inputs like `AAAA...`.

```stdin
2
JACK
DANIEL
ABACABA
ABACABA
```

```stdout
DAJACKNIEL
AABABACABACABA
```
