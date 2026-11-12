## Sets

### Introduction to Sets

**Problem.** Return the average of the **distinct** plant heights, rounded to 3 decimals.

**Idea.** `set(array)` removes repeated heights; then sum / count.

**Steps.**
1. `distinct = set(array)` keeps each height once.
2. Average = `sum(distinct) / len(distinct)`.
3. Round to 3 decimals with `round(..., 3)` and return it.

```python
def average(array):
    distinct = set(array)
    return round(sum(distinct) / len(distinct), 3)

if __name__ == '__main__':
    n = int(input())
    arr = list(map(int, input().split()))
    result = average(arr)
    print(result)
```

**Watch out.** Averaging the full list (with duplicates) gives a different number.

```stdin
10
161 182 161 154 176 170 167 171 170 174
```

```stdout
169.375
```

### No Idea!

**Problem.** For each number in the array: +1 happiness if it's in set A, −1 if it's in set B. Print the final happiness.

**Idea.** Store A and B as sets so each membership check is O(1); loop over the array (which can contain duplicates, each counted).

**Steps.**
1. Read the array as a list (keep duplicates).
2. Read A and B as sets so `x in A` is fast.
3. For each `x` in the array: in A → `+1`; in B → `-1`; otherwise nothing.
4. Print the final happiness.

```python
n, m = map(int, input().split())
arr = input().split()
A = set(input().split())
B = set(input().split())

happiness = 0
for x in arr:
    if x in A:
        happiness += 1
    elif x in B:
        happiness -= 1
print(happiness)
```

**Watch out.** Don't turn `arr` into a set: repeated numbers must count every time. Keeping values as strings is fine since you only compare them.

```stdin
3 2
1 5 3
3 1
5 7
```

```stdout
1
```

### Symmetric Difference

**Problem.** Print the values that are in exactly one of the two sets, in ascending order, one per line.

**Idea.** `a ^ b` (symmetric difference), then `sorted`.

**Steps.**
1. Read both lines of numbers as sets of `int`.
2. `a ^ b` keeps the values that are in exactly one of the sets.
3. Sort them and print one per line.

```python
m = int(input())
a = set(map(int, input().split()))
n = int(input())
b = set(map(int, input().split()))

for x in sorted(a ^ b):
    print(x)
```

**Watch out.** Convert to `int` before sorting, otherwise `"11"` sorts before `"5"`.

```stdin
4
2 4 5 9
4
2 4 11 12
```

```stdout
5
9
11
12
```

### Set .add()

**Problem.** Count distinct country names among `N` stamps.

**Idea.** Add each name to a set; duplicates are ignored. Print the size.

**Steps.**
1. Start with an empty set.
2. Read each country name as a whole line and `add` it. A name that's already there is ignored.
3. Print `len(countries)`.

```python
n = int(input())
countries = set()
for _ in range(n):
    countries.add(input())
print(len(countries))
```

**Watch out.** Read whole lines (`input()`), not `input().split()`: names like `New Zealand` contain spaces.

```stdin
7
UK
China
USA
France
New Zealand
UK
France
```

```stdout
5
```

### Set .discard(), .remove() & .pop()

**Problem.** Apply `pop`, `remove x`, `discard x` commands to a set and print the sum of what remains.

**Idea.** Parse each command; `pop` has no argument.

**Steps.**
1. Read the set as integers.
2. For each command, split the line: `parts[0]` is the command, `parts[1]` (if any) is the value.
3. `pop` → `s.pop()`; `remove` → `s.remove(int(v))`; `discard` → `s.discard(int(v))`.
4. Print `sum(s)` at the end.

```python
n = int(input())
s = set(map(int, input().split()))

for _ in range(int(input())):
    parts = input().split()
    if parts[0] == "pop":
        s.pop()
    elif parts[0] == "remove":
        s.remove(int(parts[1]))
    elif parts[0] == "discard":
        s.discard(int(parts[1]))

print(sum(s))
```

**Watch out.** `remove(x)` raises `KeyError` when `x` is missing; `discard(x)` doesn't. Convert the argument to `int` or nothing matches.

```stdin
9
1 2 3 4 5 6 7 8 9
10
pop
remove 9
discard 9
discard 8
remove 7
pop
discard 6
remove 5
pop
discard 5
```

```stdout
4
```

### Set .union() Operation

**Problem.** Count students subscribed to **at least one** of two newspapers.

**Idea.** Union of the two sets: `a | b`.

**Steps.**
1. Skip the count line, read the English roll numbers into a set.
2. Skip the next count line, read the French roll numbers into a set.
3. `english | french` has everyone in at least one set; print its length.

```python
input()
english = set(input().split())
input()
french = set(input().split())
print(len(english | french))
```

**Watch out.** A bare `input()` reads and discards the count lines.

```stdin
9
1 2 3 4 5 6 7 8 9
9
10 1 2 3 11 21 55 6 8
```

```stdout
13
```

### Set .intersection() Operation

**Problem.** Count students subscribed to **both** newspapers.

**Idea.** Intersection: `a & b`.

**Steps.**
1. Read both sets (skipping the count lines).
2. `english & french` keeps students that appear in both.
3. Print its length.

```python
input()
english = set(input().split())
input()
french = set(input().split())
print(len(english & french))
```

**Watch out.** `a.intersection(any_iterable)` accepts lists too; `&` needs two sets.

```stdin
9
1 2 3 4 5 6 7 8 9
9
10 1 2 3 11 21 55 6 8
```

```stdout
5
```

### Set .difference() Operation

**Problem.** Count students subscribed **only** to the English newspaper.

**Idea.** Difference: `english - french`.

**Steps.**
1. Read both sets (skipping the count lines).
2. `english - french` keeps students in English but not in French.
3. Print its length.

```python
input()
english = set(input().split())
input()
french = set(input().split())
print(len(english - french))
```

**Watch out.** Difference is not symmetric: `a - b` and `b - a` are different.

```stdin
9
1 2 3 4 5 6 7 8 9
9
10 1 2 3 11 21 55 6 8
```

```stdout
4
```

### Set .symmetric_difference() Operation

**Problem.** Count students subscribed to **exactly one** of the two newspapers.

**Idea.** Symmetric difference: `a ^ b`.

**Steps.**
1. Read both sets (skipping the count lines).
2. `english ^ french` keeps students in exactly one of the two.
3. Print its length.

```python
input()
english = set(input().split())
input()
french = set(input().split())
print(len(english ^ french))
```

**Watch out.** `a ^ b` equals `(a - b) | (b - a)`.

```stdin
9
1 2 3 4 5 6 7 8 9
9
10 1 2 3 11 21 55 6 8
```

```stdout
8
```

### Set Mutations

**Problem.** Apply `N` in-place operations to set A (`update`, `intersection_update`, `difference_update`, `symmetric_difference_update`), each followed by a line with the other set. Print the sum of A.

**Idea.** The operation name is exactly a set method name, so call it with `getattr`.

**Steps.**
1. Read set A.
2. For each operation: read the line `op size`, then the next line as the other set.
3. `getattr(A, op)(other)` calls the method named `op` on A, e.g. `A.update(other)`. It changes A in place.
4. After all operations, print `sum(A)`.

```python
input()
A = set(map(int, input().split()))

for _ in range(int(input())):
    op, _size = input().split()
    other = set(map(int, input().split()))
    getattr(A, op)(other)

print(sum(A))
```

**Watch out.** Each operation line is followed by a **separate** line with the other set's elements. The `_update` methods change A in place and return `None`.

```stdin
16
1 2 3 4 5 6 7 8 9 10 11 12 13 14 24 52
4
intersection_update 10
2 3 5 6 8 9 1 4 7 11
update 2
55 66
symmetric_difference_update 5
22 7 35 62 58
difference_update 7
11 22 35 55 58 62 66
```

```stdout
38
```

### The Captain's Room

**Problem.** Every family room number appears `K` times; the captain's room appears once. Find it.

**Idea.** If every number appeared `K` times, the sum would be `K * sum(set)`. The difference from the actual sum is `(K - 1) * captain`.

**Steps.**
1. `sum(set(rooms))` is the sum of each room number once.
2. Multiply it by `k`: that would be the total if the captain's room also appeared `k` times.
3. Subtract the real `sum(rooms)`: the difference is `(k - 1) * captain`.
4. Divide by `k - 1` and print the captain's room.

```python
k = int(input())
rooms = list(map(int, input().split()))
print((sum(set(rooms)) * k - sum(rooms)) // (k - 1))
```

**Watch out.** O(n) without sorting. Alternative: `Counter(rooms)` and pick the key with count 1.

```stdin
5
1 2 3 6 5 4 4 2 5 3 6 1 6 5 3 2 4 1 2 5 1 4 3 6 8 4 3 1 5 6 2
```

```stdout
8
```

### Check Subset

**Problem.** For each test case, print whether set A is a subset of set B.

**Idea.** `a <= b` (or `a.issubset(b)`).

**Steps.**
1. Read the number of test cases.
2. For each case, read A (skip its count line) and B (skip its count line).
3. Print `a <= b`, which is True when every element of A is in B.

```python
for _ in range(int(input())):
    input()
    a = set(input().split())
    input()
    b = set(input().split())
    print(a <= b)
```

**Watch out.** Read all four lines of each test case even when you already know the answer.

```stdin
3
5
1 2 3 5 6
9
9 8 5 6 3 2 1 4 7
1
2
5
3 6 5 4 1
7
1 2 3 5 6 8 9
3
9 8 2
```

```stdout
True
False
False
```

### Check Strict Superset

**Problem.** Is set A a **strict** superset of every one of the `n` other sets?

**Idea.** `a > b` means A contains B and has at least one extra element. Check all with `all()`.

**Steps.**
1. Read set A and the number `n` of other sets.
2. For each other set B, check `a > b`: A contains all of B **and** has something extra.
3. `all(...)` is True only if every check passes; print it.

```python
a = set(input().split())
n = int(input())
print(all(a > set(input().split()) for _ in range(n)))
```

**Watch out.** `all()` with a generator stops reading input early on the first `False`. That's fine here because the program ends right after, but in general read all input first if more follows.

```stdin
1 2 3 4 5 6 7 8 9 10 11 12 23 45 84 78
2
1 2 3 4 5
100 11 12
```

```stdout
False
```

## Math

### Polar Coordinates

**Problem.** Read a complex number and print its modulus `r` and phase angle `φ`.

**Idea.** `complex(input())` parses `1+2j`; `abs(z)` is the modulus; `cmath.phase(z)` is the angle.

**Steps.**
1. `complex(input())` turns text like `1+2j` into a complex number `z`.
2. `abs(z)` is the modulus `r` (distance from the origin).
3. `cmath.phase(z)` is the angle `φ` in radians.
4. Print `r`, then `φ`.

```python
import cmath

z = complex(input())
print(abs(z))
print(cmath.phase(z))
```

**Watch out.** `cmath.polar(z)` returns both at once as a tuple.

```stdin
1+2j
```

```stdout
2.23606797749979
1.1071487177940904
```

### Find Angle MBC

**Problem.** Triangle ABC has a right angle at B; M is the midpoint of the hypotenuse AC. Given AB and BC, print angle MBC in degrees, rounded to the nearest integer, followed by `°`.

**Idea.** M is the center of the circumscribed circle, so MB = MC and angle MBC = angle MCB = `atan(AB / BC)`.

**Steps.**
1. Read `AB` and `BC`.
2. Angle MBC equals angle ACB (M is the midpoint of the hypotenuse, so MB = MC).
3. In the right triangle, `tan(ACB) = AB / BC`, so the angle is `atan2(AB, BC)` in radians.
4. Convert to degrees, round to the nearest integer, and print it followed by `°`.

```python
import math

ab = int(input())
bc = int(input())
angle = round(math.degrees(math.atan2(ab, bc)))
print(f"{angle}\N{DEGREE SIGN}")
```

**Watch out.** `atan2(y, x)` avoids division by zero; `\N{DEGREE SIGN}` is the `°` character.

```stdin
10
10
```

```stdout
45°
```

### Triangle Quest 2

**Problem.** Print the palindromic triangle `1, 121, 12321, ...` of size `N` using a single `for` line with arithmetic only (no strings).

**Idea.** `(10**i - 1) // 9` is the repunit `11...1` (i ones), and `111² = 12321`.

**Steps.**
1. For `i` from 1 to `N`, `(10**i - 1) // 9` is the number made of `i` ones (`1`, `11`, `111`, ...).
2. Squaring it gives the palindrome: `11² = 121`, `111² = 12321`.
3. Print each square.

```python
for i in range(1, int(input()) + 1):
    print(((10 ** i - 1) // 9) ** 2)
```

**Watch out.** This identity holds only up to 9 ones, which is why `N` is at most 9.

```stdin
5
```

```stdout
1
121
12321
1234321
123454321
```

### Mod Divmod

**Problem.** Read `a` and `b`; print `a // b`, `a % b`, and `divmod(a, b)`.

**Idea.** `divmod` returns both as a tuple.

**Steps.**
1. Read `a` and `b`.
2. Print `a // b` (quotient) and `a % b` (remainder).
3. Print `divmod(a, b)`, which is the tuple `(quotient, remainder)`.

```python
a = int(input())
b = int(input())
print(a // b)
print(a % b)
print(divmod(a, b))
```

**Watch out.** The tuple prints with parentheses and a space: `(17, 7)`.

```stdin
177
10
```

```stdout
17
7
(17, 7)
```

### Power - Mod Power

**Problem.** Print `a ** b`, then `a ** b mod m`.

**Idea.** `pow(a, b, m)` computes the modular power efficiently.

**Steps.**
1. Read `a`, `b`, `m`.
2. Print `pow(a, b)`, i.e. `a ** b`.
3. Print `pow(a, b, m)`, the remainder of `a ** b` divided by `m`, computed without building the huge number.

```python
a = int(input())
b = int(input())
m = int(input())
print(pow(a, b))
print(pow(a, b, m))
```

**Watch out.** `pow(a, b) % m` gives the same answer but builds the huge number first.

```stdin
3
4
5
```

```stdout
81
1
```

### Integers Come In All Sizes

**Problem.** Print `a**b + c**d` for large values.

**Idea.** Python integers have no size limit.

**Steps.**
1. Read `a`, `b`, `c`, `d` as integers.
2. Compute `a ** b + c ** d`. Python ints grow as large as needed, so the result is exact.
3. Print it.

```python
a, b, c, d = (int(input()) for _ in range(4))
print(a ** b + c ** d)
```

**Watch out.** In C/Java this would overflow; in Python it's exact.

```stdin
9
29
7
27
```

```stdout
4710194409608608369201743232
```

### Triangle Quest

**Problem.** Print rows `1, 22, 333, ...` up to `N - 1` using one `for` line and only arithmetic (no strings).

**Idea.** `i * repunit(i)`: `(10**i // 9)` is `11...1`, times `i` gives `ii...i`.

**Steps.**
1. For `i` from 1 to `N - 1`, `10 ** i // 9` is the number made of `i` ones.
2. Multiply by `i`: `111 * 3 = 333`.
3. Print it.

```python
for i in range(1, int(input())):
    print(10 ** i // 9 * i)
```

**Watch out.** The loop runs to `N - 1`, not `N`.

```stdin
5
```

```stdout
1
22
333
4444
```

## Itertools

### itertools.product()

**Problem.** Print the Cartesian product A × B, space-separated.

**Idea.** `product(A, B)` yields every pair in order.

**Steps.**
1. Read A and B as lists of ints.
2. `product(A, B)` gives every pair `(a, b)`, with `a` from A and `b` from B, in order.
3. `print(*...)` prints all the pairs on one line separated by spaces.

```python
from itertools import product

A = list(map(int, input().split()))
B = list(map(int, input().split()))
print(*product(A, B))
```

**Watch out.** `print(*...)` prints the tuples separated by spaces.

```stdin
1 2
3 4
```

```stdout
(1, 3) (1, 4) (2, 3) (2, 4)
```

### itertools.permutations()

**Problem.** Print all permutations of size `k` of a string, in lexicographic order, one per line.

**Idea.** Sort the string first so `permutations` produces them in sorted order.

**Steps.**
1. Read the string and `k`.
2. Sort the characters so the output comes out in lexicographic order.
3. For each tuple from `permutations(sorted(s), k)`, join it into a string and print it.

```python
from itertools import permutations

s, k = input().split()
for p in permutations(sorted(s), int(k)):
    print(''.join(p))
```

**Watch out.** `permutations` returns tuples of characters; join them.

```stdin
HACK 2
```

```stdout
AC
AH
AK
CA
CH
CK
HA
HC
HK
KA
KC
KH
```

### itertools.combinations()

**Problem.** Print all combinations of sizes 1 to `k` of a string, in lexicographic order.

**Idea.** Sort the string; for each size `r`, print `combinations(sorted_s, r)`.

**Steps.**
1. Read the string and `k`; sort the characters.
2. For each size `r` from 1 to `k`, loop over `combinations(s, r)`.
3. Join each tuple into a string and print it.

```python
from itertools import combinations

s, k = input().split()
s = sorted(s)
for r in range(1, int(k) + 1):
    for c in combinations(s, r):
        print(''.join(c))
```

**Watch out.** All size-1 combinations come before size-2 ones.

```stdin
HACK 2
```

```stdout
A
C
H
K
AC
AH
AK
CH
CK
HK
```

### itertools.combinations_with_replacement()

**Problem.** Print all size-`k` combinations **with replacement** in lexicographic order.

**Idea.** Same as above with `combinations_with_replacement`.

**Steps.**
1. Read the string and `k`; sort the characters.
2. Loop over `combinations_with_replacement(sorted(s), k)`: like combinations, but a character can be picked again.
3. Join each tuple and print it.

```python
from itertools import combinations_with_replacement

s, k = input().split()
for c in combinations_with_replacement(sorted(s), int(k)):
    print(''.join(c))
```

**Watch out.** Elements can repeat (`AA`), but order still doesn't matter (`AC` but no `CA`).

```stdin
HACK 2
```

```stdout
AA
AC
AH
AK
CC
CH
CK
HH
HK
KK
```

### Compress the String!

**Problem.** Replace each run of the same digit with `(count, digit)`.

**Idea.** `groupby` groups consecutive equal characters.

**Steps.**
1. `groupby(s)` splits the string into runs of the same character: `1`, `222`, `3`, `11`.
2. For each run, the key `k` is the digit and `g` is the run; `len(list(g))` is its length.
3. Build the tuple `(count, int(k))` for each run and print them all separated by spaces.

```python
from itertools import groupby

s = input()
print(*((len(list(g)), int(k)) for k, g in groupby(s)))
```

**Watch out.** `groupby` only groups **consecutive** equal items (it doesn't sort).

```stdin
1222311
```

```stdout
(1, 1) (3, 2) (1, 3) (2, 1)
```

### Iterables and Iterators

**Problem.** From `N` letters, choose `K` indexes uniformly at random. What is the probability that at least one chosen letter is `a`? Print with 3 decimals.

**Idea.** Enumerate all combinations of the letters and count those containing `a`.

**Steps.**
1. Read `n`, the letters, and `k`.
2. List every way to pick `k` of the letters: `combinations(letters, k)`.
3. Count the picks that contain at least one `'a'`.
4. Probability = that count / total picks; print with `:.3f`.

```python
from itertools import combinations

n = int(input())
letters = input().split()
k = int(input())

combos = list(combinations(letters, k))
with_a = sum('a' in c for c in combos)
print(f"{with_a / len(combos):.3f}")
```

**Watch out.** Combine positions, not distinct letters: `combinations` on the list treats repeated letters as different items, which is what the problem means. Closed form: `1 - C(n - count_a, k) / C(n, k)`.

```stdin
4
a a c d
2
```

```stdout
0.833
```

### Maximize It!

**Problem.** Pick one number from each of `K` lists to maximize `S = (x1² + x2² + ... + xK²) % M`.

**Idea.** The lists are small, so try every choice with `product` (squaring each element first).

**Steps.**
1. Read `k` and `m`, then each list, dropping its first number (the length).
2. `product(*lists)` gives every way to choose one number from each list.
3. For each choice, compute `sum(x * x) % m`.
4. Print the largest value.

```python
from itertools import product

k, m = map(int, input().split())
lists = [list(map(int, input().split()))[1:] for _ in range(k)]

print(max(sum(x * x for x in choice) % m for choice in product(*lists)))
```

**Watch out.** The first number on each list line is its length, so skip it with `[1:]`. Greedily taking the largest of each list fails because of the modulo.

```stdin
3 1000
2 5 4
3 7 8 9
5 5 7 8 9 10
```

```stdout
206
```

## Collections

### collections.Counter()

**Problem.** A shop has shoes of given sizes. Each customer wants a size and pays a price if it's in stock. Print the total earned.

**Idea.** `Counter` holds how many shoes of each size remain.

**Steps.**
1. Count the shoe sizes in stock with `Counter`.
2. For each customer, read `size` and `price`.
3. If `stock[size] > 0`, sell it: decrease that count by 1 and add `price` to the total.
4. Print the total.

```python
from collections import Counter

input()
stock = Counter(map(int, input().split()))
total = 0
for _ in range(int(input())):
    size, price = map(int, input().split())
    if stock[size] > 0:
        stock[size] -= 1
        total += price
print(total)
```

**Watch out.** `Counter` returns 0 for unknown sizes instead of raising `KeyError`.

```stdin
10
2 3 4 5 6 8 7 6 5 18
6
6 55
6 45
6 55
4 40
18 60
10 50
```

```stdout
200
```

### DefaultDict Tutorial

**Problem.** For each word of group B, print the 1-based positions where it appears in group A, or `-1`.

**Idea.** `defaultdict(list)` maps each word of A to its list of positions.

**Steps.**
1. Read the `n` words of group A; append each word's 1-based position to `positions[word]`.
2. For each of the `m` words of group B, check whether it's in `positions`.
3. If yes, print its positions separated by spaces; if not, print `-1`.

```python
from collections import defaultdict

n, m = map(int, input().split())
positions = defaultdict(list)
for i in range(1, n + 1):
    positions[input()].append(i)

for _ in range(m):
    word = input()
    print(' '.join(map(str, positions[word])) if word in positions else -1)
```

**Watch out.** Check `word in positions` **before** reading `positions[word]`; reading a missing key in a `defaultdict` creates it.

```stdin
5 2
a
a
b
a
b
a
b
```

```stdout
1 2 4
3 5
```

### Collections.namedtuple()

**Problem.** Read a table with columns `ID, MARKS, NAME, CLASS` in **any order**, and print the average of `MARKS` with 2 decimals.

**Idea.** Create a namedtuple from the header row, so `student.MARKS` works whatever the column order.

**Steps.**
1. Read `n`, then the header line; `namedtuple('Student', header.split())` makes a type with those column names.
2. For each student line, build `Student(*line.split())`.
3. Add up `int(student.MARKS)`; this works whatever position MARKS has.
4. Print `total / n` with two decimals.

```python
from collections import namedtuple

n = int(input())
Student = namedtuple('Student', input().split())
total = sum(int(Student(*input().split()).MARKS) for _ in range(n))
print(f"{total / n:.2f}")
```

**Watch out.** The header can have extra spaces; `split()` handles that.

```stdin
5
ID         MARKS      NAME       CLASS
1          97         Raymond    7
2          50         Steven     4
3          91         Adrian     9
4          72         Stewart    5
5          80         Peter      6
```

```stdout
78.00
```

### Collections.OrderedDict()

**Problem.** Print each item's name and total net price, in the order of first purchase.

**Idea.** Item names can contain spaces, so split off the last word as the price. Python dicts keep insertion order (OrderedDict does too).

**Steps.**
1. For each line, `rsplit(' ', 1)` separates the item name from the price at the last space.
2. Add the price to `totals[name]` (start at 0 for a new item). The first time a name is seen fixes its position.
3. Print every name with its total, in that order.

```python
from collections import OrderedDict

totals = OrderedDict()
for _ in range(int(input())):
    name, price = input().rsplit(' ', 1)
    totals[name] = totals.get(name, 0) + int(price)

for name, price in totals.items():
    print(name, price)
```

**Watch out.** `rsplit(' ', 1)` splits only at the **last** space.

```stdin
9
BANANA FRIES 12
POTATO CHIPS 30
APPLE JUICE 10
CANDY 5
APPLE JUICE 10
CANDY 5
CANDY 5
CANDY 5
POTATO CHIPS 30
```

```stdout
BANANA FRIES 12
POTATO CHIPS 60
APPLE JUICE 20
CANDY 20
```

### Word Order

**Problem.** Print the number of distinct words, then each word's count in order of first appearance.

**Idea.** `Counter` keeps first-appearance order (it's a dict).

**Steps.**
1. Read all the words into a list.
2. `Counter(words)` counts them and keeps the order in which each word first appeared.
3. Print the number of distinct words, then all the counts on one line.

```python
from collections import Counter

words = [input() for _ in range(int(input()))]
counts = Counter(words)
print(len(counts))
print(*counts.values())
```

**Watch out.** Read with `input()` per line; don't sort the words.

```stdin
4
bcdef
abcdefg
bcde
bcdef
```

```stdout
3
2 1 1
```

### Collections.deque()

**Problem.** Apply `append`, `appendleft`, `pop`, `popleft` operations to an empty deque and print it.

**Idea.** The operation name is the deque method name; call it with `getattr`.

**Steps.**
1. Start with an empty `deque`.
2. For each line, split into the method name and its arguments.
3. `getattr(d, op)(*args)` calls that method, e.g. `d.appendleft('4')`.
4. Print the deque's items separated by spaces.

```python
from collections import deque

d = deque()
for _ in range(int(input())):
    op, *args = input().split()
    getattr(d, op)(*args)
print(*d)
```

**Watch out.** Values stay as strings, which is fine because they're only printed.

```stdin
6
append 1
append 2
append 3
appendleft 4
pop
popleft
```

```stdout
1 2
```

### Company Logo

**Problem.** Print the 3 most common characters with their counts, sorted by count descending, ties broken alphabetically.

**Idea.** Count with `Counter`, then sort by `(-count, char)`.

**Steps.**
1. Count every character with `Counter(s)`.
2. Sort the `(char, count)` pairs by `(-count, char)`: highest count first, ties in alphabetical order.
3. Print the first three pairs.

```python
from collections import Counter

if __name__ == '__main__':
    s = input()
    for ch, cnt in sorted(Counter(s).items(), key=lambda x: (-x[1], x[0]))[:3]:
        print(ch, cnt)
```

**Watch out.** `most_common(3)` alone doesn't break ties alphabetically.

```stdin
aabbbccde
```

```stdout
b 3
a 2
c 2
```

### Piling Up!

**Problem.** Cubes in a row; you may only take the leftmost or rightmost cube and stack it. Each cube must be no bigger than the one below. Print `Yes` or `No`.

**Idea.** Greedy: always take the **larger** end (taking the smaller one first would make the larger one impossible later). If the taken cube is bigger than the top of the pile, it fails.

**Steps.**
1. Put the cubes in a `deque` so both ends can be removed quickly.
2. Each turn, take the **larger** of the two end cubes.
3. If it's bigger than the cube on top of the pile, stacking is impossible → `No`.
4. Otherwise it becomes the new top. If all cubes are taken → `Yes`.

```python
from collections import deque

for _ in range(int(input())):
    input()
    d = deque(map(int, input().split()))
    top = float('inf')
    ok = True
    while d:
        cube = d.popleft() if d[0] >= d[-1] else d.pop()
        if cube > top:
            ok = False
            break
        top = cube
    print("Yes" if ok else "No")
```

**Watch out.** Equivalent check: the sequence must decrease to a minimum and then increase (a "valley" shape).

```stdin
2
6
4 3 2 1 3 4
3
1 3 2
```

```stdout
Yes
No
```
