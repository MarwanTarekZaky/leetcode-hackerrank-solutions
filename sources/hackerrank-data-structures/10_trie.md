## Trie

### Contacts

**Problem.** Process `add name` and `find partial`, where `find` counts the stored names that start with `partial`.

**Idea.** Since names are at most 21 characters, adding a name increments a counter for **each of its prefixes**, using a dictionary as a flattened trie. A `find` is then a single lookup.

**Steps.**
1. `add`: for every prefix length, `count[name[:k]] += 1`.
2. `find`: print `count.get(partial, 0)`.

```python
import os


def contacts(queries):
    count = {}
    out = []
    for op, s in queries:
        if op == 'add':
            for k in range(1, len(s) + 1):
                p = s[:k]
                count[p] = count.get(p, 0) + 1
        else:
            out.append(count.get(s, 0))
    return out


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n = int(input().strip())
    queries = [input().rstrip().split() for _ in range(n)]
    fptr.write('\n'.join(map(str, contacts(queries))) + '\n')
    fptr.close()
```

**Watch out.** Scanning all names for each `find` is O(n) per query, which is too slow for 10⁵ operations. The prefix counter moves the work to `add`, where it is bounded by the name length.

```stdin
4
add hack
add hackerrank
find hac
find hak
```

```stdout
2
0
```

### No Prefix Set

**Problem.** Insert the words in order. If some word is a prefix of another (in either direction), print `BAD SET` and the **first word at which this is detected**; otherwise print `GOOD SET`.

**Idea.** Use a trie with end-of-word markers. While inserting a word, it is bad when:
- the path passes through a node that ends an earlier word (an earlier word is a prefix of this one); or
- the word ends at a node that already exists, meaning a longer word went through it (this word is a prefix of an earlier one), or the same word came before.

**Steps.**
1. Walk and create the nodes, checking the end markers along the way.
2. At the end, check that the final node is newly created; then mark it as an end.

```python
def noPrefix(words):
    root = {}
    END = '$'
    for w in words:
        node = root
        created = False
        for ch in w:
            if END in node:
                print('BAD SET')
                print(w)
                return
            if ch not in node:
                node[ch] = {}
                created = True
            node = node[ch]
        if not created or END in node:
            print('BAD SET')
            print(w)
            return
        node[END] = True
    print('GOOD SET')


if __name__ == '__main__':
    n = int(input().strip())
    words = [input().strip() for _ in range(n)]
    noPrefix(words)
```

**Watch out.** "Not created" covers both a duplicate word and a word that is a prefix of an earlier, longer word. In both cases the last node already existed.

```stdin
7
aab
defgab
abcde
aabcde
cedaaa
bbbbbbbbbb
jabjjjad
```

```stdout
BAD SET
aabcde
```
