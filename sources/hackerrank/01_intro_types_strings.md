## Introduction

### Say "Hello, World!" With Python

**Problem.** Print `Hello, World!`.

**Idea.** `print()` writes its argument followed by a newline.

**Steps.**
1. Call `print()` with the exact text `"Hello, World!"`.
2. `print` adds the newline at the end for you.

```python
print("Hello, World!")
```

**Watch out.** The text must match exactly, including the comma and the `!`.

```stdin
```

```stdout
Hello, World!
```

### Python If-Else

**Problem.** Read `n`. Print `Weird` if `n` is odd, `Not Weird` if it's even and in 2–5, `Weird` if even and in 6–20, `Not Weird` if even and greater than 20.

**Idea.** Check the odd case first; then the even ranges in order.

**Steps.**
1. Odd → `Weird`.
2. Even: 2–5 → `Not Weird`; 6–20 → `Weird`; above 20 → `Not Weird`.

```python
n = int(input().strip())

if n % 2 == 1:
    print("Weird")
elif 2 <= n <= 5:
    print("Not Weird")
elif 6 <= n <= 20:
    print("Weird")
else:
    print("Not Weird")
```

**Watch out.** Python allows chained comparisons like `2 <= n <= 5`.

```stdin
3
```

```stdout
Weird
```

### Arithmetic Operators

**Problem.** Read `a` and `b` (each on its own line). Print their sum, difference (`a - b`) and product on three lines.

**Idea.** Convert the input strings to integers with `int()`, then use `+`, `-`, `*`.

**Steps.**
1. Read the first line and convert it with `int()` → `a`.
2. Read the second line the same way → `b`.
3. Print `a + b`, then `a - b`, then `a * b`, each with its own `print` so each goes on its own line.

```python
a = int(input())
b = int(input())
print(a + b)
print(a - b)
print(a * b)
```

**Watch out.** Without `int()`, `input()` returns strings and `"3" + "2"` would be `"32"`.

```stdin
3
2
```

```stdout
5
1
6
```

### Python: Division

**Problem.** Read `a` and `b`. Print the integer division result, then the float division result.

**Idea.** `//` is floor (integer) division; `/` is true division and always returns a float.

**Steps.**
1. Read `a` and `b` as integers.
2. Print `a // b`: integer (floor) division, e.g. `4 // 3 = 1`.
3. Print `a / b`: true division, always a float, e.g. `4 / 3 = 1.3333333333333333`.

```python
a = int(input())
b = int(input())
print(a // b)
print(a / b)
```

**Watch out.** `//` floors toward negative infinity: `-7 // 2` is `-4`, not `-3`.

```stdin
4
3
```

```stdout
1
1.3333333333333333
```

### Loops

**Problem.** Read `n`. For every `i` from 0 to `n - 1`, print `i²`.

**Idea.** `range(n)` gives 0..n-1.

**Steps.**
1. Read `n` as an integer.
2. Loop `i` over `range(n)`, which gives `0, 1, ..., n-1`.
3. Print `i * i` on each pass.

```python
n = int(input())
for i in range(n):
    print(i * i)
```

**Watch out.** `range(n)` stops **before** `n`.

```stdin
5
```

```stdout
0
1
4
9
16
```

### Write a function

**Problem.** Complete `is_leap(year)`: divisible by 4 is a leap year, except years divisible by 100, unless they're also divisible by 400.

**Idea.** Check the rules from the most specific to the most general (400, then 100, then 4).

**Steps.**
1. If `year % 400 == 0` → leap (e.g. 2000).
2. Else if `year % 100 == 0` → not leap (e.g. 1900).
3. Else if `year % 4 == 0` → leap (e.g. 2024).
4. Otherwise → not leap. Return the result.

```python
def is_leap(year):
    leap = False
    if year % 400 == 0:
        leap = True
    elif year % 100 == 0:
        leap = False
    elif year % 4 == 0:
        leap = True
    return leap

year = int(input())
print(is_leap(year))
```

**Watch out.** Checking `% 4` first makes 1900 wrongly a leap year. One-line version: `return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)`.

```stdin
1990
```

```stdout
False
```

### Print Function

**Problem.** Read `n` and print `123...n` on one line, without using strings.

**Idea.** `print()` accepts several values and a separator; unpack `range(1, n + 1)` with `*` and use `sep=""`.

**Steps.**
1. Read `n`.
2. `range(1, n + 1)` produces `1, 2, ..., n`.
3. `*` unpacks it, so `print` receives each number as a separate argument.
4. `sep=""` joins them with nothing in between → `123...n`.

```python
n = int(input())
print(*range(1, n + 1), sep="")
```

**Watch out.** `*range(...)` passes each number as a separate argument; `sep=""` removes the default spaces between them.

```stdin
3
```

```stdout
123
```

## Basic Data Types

### List Comprehensions

**Problem.** Read `x, y, z, n`. Print all `[i, j, k]` with `0 <= i <= x`, `0 <= j <= y`, `0 <= k <= z` and `i + j + k != n`, in lexicographic order, using a list comprehension.

**Idea.** Several `for` clauses in one comprehension are nested loops in the same order; the `if` filters.

**Steps.**
1. Read `x`, `y`, `z`, `n` (one per line).
2. Write three `for` clauses: `i` in `range(x + 1)`, then `j`, then `k`. They act like nested loops, `i` outermost.
3. Add the filter `if i + j + k != n`.
4. Each surviving triple becomes `[i, j, k]`; print the whole list.

```python
if __name__ == '__main__':
    x = int(input())
    y = int(input())
    z = int(input())
    n = int(input())

    print([[i, j, k]
           for i in range(x + 1)
           for j in range(y + 1)
           for k in range(z + 1)
           if i + j + k != n])
```

**Watch out.** Use `range(x + 1)` because `x` itself is included. Keep `i` as the outer loop so the order is lexicographic.

```stdin
1
1
1
2
```

```stdout
[[0, 0, 0], [0, 0, 1], [0, 1, 0], [1, 0, 0], [1, 1, 1]]
```

### Find the Runner-Up Score!

**Problem.** Given `n` scores, print the second-highest **distinct** score.

**Idea.** Remove duplicates with `set`, sort, take the second from the end.

**Steps.**
1. Read the scores as integers.
2. `set(...)` removes repeated scores.
3. `sorted(...)` puts the distinct scores in ascending order.
4. `[-2]` is the second from the end, i.e. the second highest.

```python
if __name__ == '__main__':
    n = int(input())
    arr = map(int, input().split())
    print(sorted(set(arr))[-2])
```

**Watch out.** Without `set`, a repeated top score (`[2,3,6,6,5]`) would give 6 again. `map()` is an iterator: you can't index it, but passing it to `set()` is fine.

```stdin
5
2 3 6 6 5
```

```stdout
5
```

### Nested Lists

**Problem.** Read `N` students (name, then grade on the next line). Print the name(s) with the **second lowest** grade, alphabetically, one per line.

**Idea.** Store `[name, score]` pairs. The second lowest is the second item of the sorted **distinct** scores.

**Steps.**
1. Read each name and score and append `[name, score]` to `students`.
2. Collect the distinct scores with a `set` and sort them; index `[1]` is the second lowest.
3. Keep the names whose score equals that value.
4. Sort those names alphabetically and print one per line.

```python
if __name__ == '__main__':
    students = []
    for _ in range(int(input())):
        name = input()
        score = float(input())
        students.append([name, score])

    second_lowest = sorted(set(s[1] for s in students))[1]
    for name in sorted(s[0] for s in students if s[1] == second_lowest):
        print(name)
```

**Watch out.** The `set` matters when several students share the lowest grade.

```stdin
5
Harry
37.21
Berry
37.21
Tina
37.2
Akriti
41
Harsh
39
```

```stdout
Berry
Harry
```

### Finding the percentage

**Problem.** Read students and their marks into a dictionary, then print the average mark of the queried student with exactly 2 decimals.

**Idea.** Look up the marks list and format with `:.2f`.

**Steps.**
1. For each student line, `name, *line = input().split()` takes the first word as the name and the rest as marks.
2. Convert the marks to floats and store them: `student_marks[name] = scores`.
3. Read the query name and look up its marks.
4. Average = `sum(marks) / len(marks)`; print with `:.2f` to get exactly two decimals.

```python
if __name__ == '__main__':
    n = int(input())
    student_marks = {}
    for _ in range(n):
        name, *line = input().split()
        scores = list(map(float, line))
        student_marks[name] = scores
    query_name = input()

    marks = student_marks[query_name]
    print(f"{sum(marks) / len(marks):.2f}")
```

**Watch out.** `round(56.0, 2)` still prints `56.0`; only formatting (`:.2f`) prints `56.00`. `name, *line = ...` puts the first word in `name` and the rest in the list `line`.

```stdin
3
Krishna 67 68 69
Arjun 70 98 63
Malika 52 56 60
Malika
```

```stdout
56.00
```

### Lists

**Problem.** Start with an empty list and run `N` commands: `insert i e`, `print`, `remove e`, `append e`, `sort`, `pop`, `reverse`.

**Idea.** Split each line into the command and its arguments; call the matching list method with integer arguments.

**Steps.**
1. Start with an empty list `lst`.
2. For each of the `N` lines, split into the command and its arguments; convert the arguments to `int`.
3. Call the matching method: `insert(i, e)`, `remove(e)`, `append(e)`, `sort()`, `pop()`, `reverse()`.
4. On `print`, print the list as it is now.

```python
if __name__ == '__main__':
    N = int(input())
    lst = []
    for _ in range(N):
        cmd, *args = input().split()
        args = list(map(int, args))
        if cmd == "insert":
            lst.insert(args[0], args[1])
        elif cmd == "print":
            print(lst)
        elif cmd == "remove":
            lst.remove(args[0])
        elif cmd == "append":
            lst.append(args[0])
        elif cmd == "sort":
            lst.sort()
        elif cmd == "pop":
            lst.pop()
        elif cmd == "reverse":
            lst.reverse()
```

**Watch out.**
- `reverse` means `lst.reverse()` (flip the order), **not** `sort(reverse=True)`. The sample can't tell them apart, but hidden tests do.
- Don't name your list `list`: that hides the built-in.
- Shortcut: `getattr(lst, cmd)(*args)` for every command except `print`.

```stdin
12
insert 0 5
insert 1 10
insert 0 6
print
remove 6
append 9
append 1
sort
print
pop
reverse
print
```

```stdout
[6, 5, 10]
[1, 5, 9, 10]
[9, 5, 1]
```

### Tuples

**Problem.** Read `n` integers, make a tuple, and print `hash()` of it.

**Idea.** `tuple(map(int, input().split()))`, then `hash(t)`.

**Steps.**
1. Read `n`, then the line of integers.
2. `tuple(map(int, ...))` turns them into a tuple of ints.
3. Print `hash(t)`. Submit with **PyPy 3** selected.

```python
if __name__ == '__main__':
    n = int(input())
    t = tuple(map(int, input().split()))
    print(hash(t))
```

**Watch out.** Select **PyPy 3** as the language. The expected answers were produced by PyPy, which hashes tuples differently from normal Python 3 (CPython), so the same code gives a different number in "Python 3". If PyPy isn't available, reproduce the old tuple-hash formula:

```py
def old_tuple_hash(t):
    MASK = (1 << 64) - 1
    x, mult, length = 0x345678, 1000003, len(t)
    for item in t:
        length -= 1
        x = ((x ^ (hash(item) & MASK)) * mult) & MASK
        mult = (mult + 82520 + length + length) & MASK
    x = (x + 97531) & MASK
    if x == MASK:
        x = MASK - 1
    return x - (1 << 64) if x >= 1 << 63 else x

print(old_tuple_hash(t))   # 3713081631934410656 for (1, 2)
```

```stdin
2
1 2
```

## Strings

### sWAP cASE

**Problem.** Swap uppercase and lowercase letters in a string.

**Idea.** `str.swapcase()` does exactly this; the manual version flips each character.

**Steps.**
1. Call `s.swapcase()`: every uppercase letter becomes lowercase and vice versa.
2. Non-letters (digits, spaces, punctuation) stay the same.
3. Return the new string.

```python
def swap_case(s):
    return s.swapcase()

if __name__ == '__main__':
    s = input()
    result = swap_case(s)
    print(result)
```

**Watch out.** Manual version: `''.join(c.lower() if c.isupper() else c.upper() for c in s)`.

```stdin
HackerRank.com presents "Pythonist 2".
```

```stdout
hACKERrANK.COM PRESENTS "pYTHONIST 2".
```

### String Split and Join

**Problem.** Split a string on spaces and join it back with hyphens.

**Idea.** `split(" ")` makes a list; `"-".join(list)` glues it with `-`.

**Steps.**
1. `line.split(" ")` breaks the string into a list of words.
2. `"-".join(words)` glues the words back together with `-` between them.
3. Return the joined string.

```python
def split_and_join(line):
    return "-".join(line.split(" "))

if __name__ == '__main__':
    line = input()
    result = split_and_join(line)
    print(result)
```

**Watch out.** The separator goes before `.join`: `"-".join(words)`, not `words.join("-")`.

```stdin
this is a string
```

```stdout
this-is-a-string
```

### What's Your Name?

**Problem.** Read a first and last name and print `Hello firstname lastname! You just delved into python.`

**Idea.** Build the sentence with an f-string.

**Steps.**
1. Read the first name and the last name.
2. Insert both into the sentence with an f-string.
3. Print it, with `!` right after the last name.

```python
def print_full_name(first, last):
    print(f"Hello {first} {last}! You just delved into python.")

if __name__ == '__main__':
    first_name = input()
    last_name = input()
    print_full_name(first_name, last_name)
```

**Watch out.** The `!` comes right after the last name, with no space.

```stdin
Ross
Taylor
```

```stdout
Hello Ross Taylor! You just delved into python.
```

### Mutations

**Problem.** Replace the character at `position` with `character` and return the new string.

**Idea.** Strings are immutable, so build a new one from slices: before + new character + after.

**Steps.**
1. `string[:position]`: everything before the position.
2. Add the new `character`.
3. `string[position + 1:]`: everything after the replaced character.
4. Concatenate the three parts and return the new string.

```python
def mutate_string(string, position, character):
    return string[:position] + character + string[position + 1:]

if __name__ == '__main__':
    s = input()
    i, c = input().split()
    s_new = mutate_string(s, int(i), c)
    print(s_new)
```

**Watch out.** `string[5] = 'k'` raises `TypeError`. List version: `chars = list(string); chars[position] = character; return ''.join(chars)`.

```stdin
abracadabra
5 k
```

```stdout
abrackdabra
```

### Find a string

**Problem.** Count how many times `sub_string` occurs in `string`, **including overlapping** occurrences.

**Idea.** Check every start position where the substring fits.

**Steps.**
1. Let `m = len(sub_string)`.
2. Try every start `i` from `0` to `len(string) - m` (the last place the substring fits).
3. If `string[i:i + m] == sub_string`, add 1 to the count.
4. Return the count. Overlaps count because each start position is checked separately.

```python
def count_substring(string, sub_string):
    m = len(sub_string)
    count = 0
    for i in range(len(string) - m + 1):
        if string[i:i + m] == sub_string:
            count += 1
    return count

if __name__ == '__main__':
    string = input().strip()
    sub_string = input().strip()
    count = count_substring(string, sub_string)
    print(count)
```

**Watch out.** `string.count(sub)` counts **non-overlapping** matches (`"ABCDCDC".count("CDC")` is 1, the answer is 2).

```stdin
ABCDCDC
CDC
```

```stdout
2
```

### String Validators

**Problem.** Print five lines: does the string contain **any** alphanumeric, alphabetic, digit, lowercase, uppercase character?

**Idea.** The `str.isX()` methods check if **all** characters match, so apply them per character and use `any()`.

**Steps.**
1. For each check, test every character with a generator: `c.isalnum() for c in s`.
2. `any(...)` is True if at least one character passes.
3. Print the five results in order: alnum, alpha, digit, lower, upper.

```python
if __name__ == '__main__':
    s = input()
    print(any(c.isalnum() for c in s))
    print(any(c.isalpha() for c in s))
    print(any(c.isdigit() for c in s))
    print(any(c.islower() for c in s))
    print(any(c.isupper() for c in s))
```

**Watch out.** `s.isalpha()` on `"qA2"` is False (because of the 2), but the string **does** contain letters.

```stdin
qA2
```

```stdout
True
True
True
True
True
```

### Text Alignment

**Problem.** Replace the blanks in the given code with `rjust`, `ljust` or `center` to draw the HackerRank logo.

**Idea.** `s.rjust(w)` pads on the left, `s.ljust(w)` pads on the right, `s.center(w)` pads both sides. Each part of the logo needs one of them.

**Steps.**
1. Top cone: for each row `i`, the left part `c * i` is right-justified, then the middle `H`, then the right part left-justified.
2. Top pillars: two blocks of `c * thickness`, centered in widths `thickness * 2` and `thickness * 6`.
3. Middle belt: one wide block `c * thickness * 5`, centered in `thickness * 6`.
4. Bottom pillars: same as the top pillars.
5. Bottom cone: the top cone upside down, pushed right with `.rjust(thickness * 6)`.

```python
thickness = int(input())  # This must be an odd number
c = 'H'

# Top Cone
for i in range(thickness):
    print((c * i).rjust(thickness - 1) + c + (c * i).ljust(thickness - 1))

# Top Pillars
for i in range(thickness + 1):
    print((c * thickness).center(thickness * 2) + (c * thickness).center(thickness * 6))

# Middle Belt
for i in range((thickness + 1) // 2):
    print((c * thickness * 5).center(thickness * 6))

# Bottom Pillars
for i in range(thickness + 1):
    print((c * thickness).center(thickness * 2) + (c * thickness).center(thickness * 6))

# Bottom Cone
for i in range(thickness):
    print(((c * (thickness - i - 1)).rjust(thickness) + c + (c * (thickness - i - 1)).ljust(thickness)).rjust(thickness * 6))
```

**Watch out.** The order in the cones: the left half is right-justified (grows toward the center), the right half left-justified.

```stdin
5
```

### Text Wrap

**Problem.** Wrap a string into lines of at most `max_width` characters and return it as one string with newlines.

**Idea.** `textwrap.fill(text, width)` returns exactly that.

**Steps.**
1. Import `textwrap`.
2. `textwrap.fill(string, max_width)` cuts the text into lines of at most `max_width` characters.
3. It returns them joined with `\n`; return that string.

```python
import textwrap

def wrap(string, max_width):
    return textwrap.fill(string, max_width)

if __name__ == '__main__':
    string, max_width = input(), int(input())
    result = wrap(string, max_width)
    print(result)
```

**Watch out.** `textwrap.wrap` returns a **list**; `fill` returns the joined string. Manual version: `'\n'.join(string[i:i+max_width] for i in range(0, len(string), max_width))`.

```stdin
ABCDEFGHIJKLIMNOQRSTUVWXYZ
4
```

```stdout
ABCD
EFGH
IJKL
IMNO
QRST
UVWX
YZ
```

### Designer Door Mat

**Problem.** Draw a door mat of size `N × M` (N odd, M = 3N) with the `.|.` pattern and `WELCOME` in the center, using `-` as filler.

**Idea.** Row `i` of the top half has `2i + 1` copies of `.|.`, centered in width `M` with `-`. The bottom half mirrors the top.

**Steps.**
1. Read `n` (rows) and `m` (width).
2. Top half: for `i` in `0 .. n//2 - 1`, print `'.|.' * (2i + 1)` centered in width `m` with `-`.
3. Middle row: `'WELCOME'.center(m, '-')`.
4. Bottom half: the same rows as the top, with `i` going back down from `n//2 - 1` to `0`.

```python
n, m = map(int, input().split())

for i in range(n // 2):
    print(('.|.' * (2 * i + 1)).center(m, '-'))
print('WELCOME'.center(m, '-'))
for i in range(n // 2 - 1, -1, -1):
    print(('.|.' * (2 * i + 1)).center(m, '-'))
```

**Watch out.** `center(width, fill)` takes the fill character as its second argument.

```stdin
7 21
```

```stdout
---------.|.---------
------.|..|..|.------
---.|..|..|..|..|.---
-------WELCOME-------
---.|..|..|..|..|.---
------.|..|..|.------
---------.|.---------
```

### String Formatting

**Problem.** For `i` from 1 to `n`, print `i` in decimal, octal, uppercase hex and binary, each padded to the width of `n` in binary, separated by single spaces.

**Idea.** Format codes `d`, `o`, `X`, `b` with a width: `f"{i:{width}X}"`.

**Steps.**
1. `width = len(f"{number:b}")`: the length of `n` in binary is the column width.
2. Loop `i` from `1` to `n`.
3. Print `i` four times with codes `d` (decimal), `o` (octal), `X` (uppercase hex), `b` (binary), each right-aligned to `width`.
4. Separate the four columns with single spaces.

```python
def print_formatted(number):
    width = len(f"{number:b}")
    for i in range(1, number + 1):
        print(f"{i:{width}d} {i:{width}o} {i:{width}X} {i:{width}b}")

if __name__ == '__main__':
    n = int(input())
    print_formatted(n)
```

**Watch out.** Use capital `X` for uppercase hex. `bin()`, `oct()`, `hex()` add prefixes (`0b`, `0o`, `0x`); format codes don't.

```stdin
17
```

```stdout
    1     1     1     1
    2     2     2    10
    3     3     3    11
    4     4     4   100
    5     5     5   101
    6     6     6   110
    7     7     7   111
    8    10     8  1000
    9    11     9  1001
   10    12     A  1010
   11    13     B  1011
   12    14     C  1100
   13    15     D  1101
   14    16     E  1110
   15    17     F  1111
   16    20    10 10000
   17    21    11 10001
```

### Alphabet Rangoli

**Problem.** Print an alphabet rangoli of size `n` (letters `a`.. joined with `-`, a diamond shape).

**Idea.** Row `i` (distance from the center row) uses the letters from the `n`-th letter down to the `(i+1)`-th and back up. Join them with `-` and center in width `4n - 3`.

**Steps.**
1. `letters = 'abcdefghijklmnopqrstuvwxyz'[:n]`, `width = 4n - 3`.
2. For `i` in `n-1 .. 0 .. n-1`: `s = letters[n-1:i:-1] + letters[i:n]`; print `'-'.join(s).center(width, '-')`.

```python
import string

def print_rangoli(size):
    letters = string.ascii_lowercase[:size]
    width = 4 * size - 3
    rows = []
    for i in range(size - 1, -1, -1):
        part = letters[size - 1:i:-1] + letters[i:size]
        rows.append('-'.join(part).center(width, '-'))
    print('\n'.join(rows + rows[-2::-1]))

if __name__ == '__main__':
    n = int(input())
    print_rangoli(n)
```

**Watch out.** `letters[size-1:i:-1]` walks backward from the last letter and stops **before** index `i`; `letters[i:size]` adds `letters[i]` (the smallest of the row) and goes back up. `rows[-2::-1]` mirrors the top half without repeating the middle row.

```stdin
3
```

```stdout
----c----
--c-b-c--
c-b-a-b-c
--c-b-c--
----c----
```

### Capitalize!

**Problem.** Capitalize the first letter of each word in a full name, keeping the original spacing.

**Idea.** Split on single spaces (keeps empty pieces between repeated spaces), uppercase only the first character of each piece, join with single spaces.

**Steps.**
1. `s.split(' ')` splits on every single space, so repeated spaces leave empty pieces and are not lost.
2. For each piece: `word[:1].upper() + word[1:]` uppercases only the first character (a digit stays a digit).
3. Join the pieces back with `' '`.

```python
def solve(s):
    return ' '.join(word[:1].upper() + word[1:] for word in s.split(' '))

if __name__ == '__main__':
    s = input()
    print(solve(s))
```

**Watch out.**
- `s.title()` is wrong: `"12abc"` would become `"12Abc"`.
- `s.split()` (no argument) loses repeated spaces.
- `word[:1]` is safe on empty pieces; `word[0]` would crash.

```stdin
chris alan
```

```stdout
Chris Alan
```

### The Minion Game

**Problem.** Kevin scores with substrings starting with a vowel, Stuart with consonants; each substring scores as many points as times it appears. Print the winner and score, or `Draw`.

**Idea.** A substring starting at index `i` can end at any of the `len - i` positions after it, and counting all of those is exactly the occurrence count. So each start position gives `len(s) - i` points to whoever owns that letter.

**Steps.**
1. Let `n = len(string)`.
2. For each index `i`, there are `n - i` substrings that start there.
3. If `string[i]` is a vowel, add `n - i` to Kevin; otherwise add it to Stuart.
4. Compare the totals and print the winner with the score, or `Draw`.

```python
def minion_game(string):
    n = len(string)
    kevin = stuart = 0
    for i, ch in enumerate(string):
        if ch in 'AEIOU':
            kevin += n - i
        else:
            stuart += n - i
    if kevin > stuart:
        print("Kevin", kevin)
    elif stuart > kevin:
        print("Stuart", stuart)
    else:
        print("Draw")

if __name__ == '__main__':
    s = input()
    minion_game(s)
```

**Watch out.** Generating all substrings is O(n²) memory and times out (n up to 10⁶). This is O(n).

```stdin
BANANA
```

```stdout
Stuart 12
```

### Merge the Tools!

**Problem.** Split `string` into `n / k` pieces of length `k`. For each piece, print it with repeated characters removed (keep first occurrences, in order).

**Idea.** `dict.fromkeys(piece)` keeps the first occurrence of each character in order.

**Steps.**
1. Loop `i` over `0, k, 2k, ...` and take the piece `string[i:i + k]`.
2. `dict.fromkeys(piece)` keeps each character once, in the order it first appears.
3. `''.join(...)` turns the keys back into a string; print it.

```python
def merge_the_tools(string, k):
    for i in range(0, len(string), k):
        print(''.join(dict.fromkeys(string[i:i + k])))

if __name__ == '__main__':
    string, k = input(), int(input())
    merge_the_tools(string, k)
```

**Watch out.** A `set` would remove duplicates but lose the order.

```stdin
AABCAAADA
3
```

```stdout
AB
CA
AD
```
