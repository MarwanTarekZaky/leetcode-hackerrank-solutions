## Date and Time

### Calendar Module

**Problem.** Given a date `MM DD YYYY`, print the weekday name in capitals.

**Idea.** `calendar.weekday(year, month, day)` returns 0 (Monday) to 6 (Sunday); `calendar.day_name` maps it to a name.

**Steps.**
1. Read the input as `month, day, year` integers.
2. `calendar.weekday(year, month, day)` gives 0 for Monday up to 6 for Sunday.
3. `calendar.day_name[...]` turns that number into the name, e.g. `Wednesday`.
4. `.upper()` → `WEDNESDAY`; print it.

```python
import calendar

month, day, year = map(int, input().split())
print(calendar.day_name[calendar.weekday(year, month, day)].upper())
```

**Watch out.** The input order is month, day, year, but `weekday` takes year, month, day.

```stdin
08 05 2015
```

```stdout
WEDNESDAY
```

### Time Delta

**Problem.** For each pair of timestamps like `Sun 10 May 2015 13:54:36 -0700`, print the absolute difference in seconds.

**Idea.** Parse with `datetime.strptime` and the format `%a %d %b %Y %H:%M:%S %z` (`%z` handles the timezone offset), subtract, take `abs(total_seconds())`.

**Steps.**
1. Define the format `'%a %d %b %Y %H:%M:%S %z'`: weekday, day, month, year, time, timezone offset.
2. Parse both timestamps with `datetime.strptime(t, FMT)`.
3. Subtract them; Python converts both to the same timezone first.
4. `abs(...total_seconds())` is the difference in seconds; return it as a string of an int.

```python
#!/bin/python3
import os
from datetime import datetime

FMT = '%a %d %b %Y %H:%M:%S %z'

def time_delta(t1, t2):
    d1 = datetime.strptime(t1, FMT)
    d2 = datetime.strptime(t2, FMT)
    return str(int(abs((d1 - d2).total_seconds())))

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    t = int(input())
    for t_itr in range(t):
        t1 = input()
        t2 = input()
        delta = time_delta(t1, t2)
        fptr.write(delta + '\n')
    fptr.close()
```

**Watch out.** The function must return a **string** (the stub writes `delta + '\n'`). Timezone-aware datetimes subtract correctly across offsets.

```stdin
2
Sun 10 May 2015 13:54:36 -0700
Sun 10 May 2015 13:54:36 -0000
Sat 02 May 2015 19:54:36 +0530
Fri 01 May 2015 13:54:36 -0000
```

```stdout
25200
88200
```

## Errors and Exceptions

### Exceptions

**Problem.** For each pair `a b`, print `a // b`, or `Error Code: <message>` if a `ZeroDivisionError` or `ValueError` occurs.

**Idea.** Wrap the conversion and division in `try`/`except`, catching both error types and printing their message.

**Steps.**
1. For each test case, split the line into `a` and `b` (still strings).
2. Inside `try`, convert both with `int()` and print `a // b`.
3. If `int()` fails → `ValueError`; if `b` is 0 → `ZeroDivisionError`.
4. Catch both in one `except` and print `Error Code:` followed by the error message.

```python
for _ in range(int(input())):
    a, b = input().split()
    try:
        print(int(a) // int(b))
    except (ZeroDivisionError, ValueError) as e:
        print("Error Code:", e)
```

**Watch out.** `print("Error Code:", e)` prints the exception's message after a space, e.g. `Error Code: integer division or modulo by zero`.

```stdin
3
1 0
2 $
3 1
```

```stdout
Error Code: integer division or modulo by zero
Error Code: invalid literal for int() with base 10: '$'
3
```

### Incorrect Regex

**Problem.** For each pattern, print `True` if it's a valid regex, else `False`.

**Idea.** Try to compile it; `re.error` means it's invalid.

**Steps.**
1. For each pattern, try `re.compile(pattern)`.
2. If it compiles, print `True`.
3. If it raises `re.error`, print `False`.

```python
import re

for _ in range(int(input())):
    try:
        re.compile(input())
        print(True)
    except re.error:
        print(False)
```

**Watch out.** On HackerRank's Python, `.*+` is invalid ("multiple repeat"), so the sample prints `True` then `False`. Python 3.11 and newer added possessive quantifiers, so on your own computer `.*+` may compile and print `True`. That's a Python version difference, not a bug in the code.

```stdin
2
.*\+
.*+
```

## Classes

### Classes: Dealing with Complex Numbers

**Problem.** Implement a `Complex` class with `+`, `-`, `*`, `/` and `mod()`, and print the results for two given numbers.

**Idea.** Write the formulas with operator methods (`__add__`, `__sub__`, `__mul__`, `__truediv__`). Division: multiply by the conjugate, `(a+bi)/(c+di) = ((ac+bd) + (bc−ad)i) / (c²+d²)`. `mod` returns `sqrt(a²+b²)` as a complex with 0 imaginary part.

**Steps.**
1. `__add__` / `__sub__`: add or subtract the real parts and the imaginary parts separately.
2. `__mul__`: `(a+bi)(c+di) = (ac − bd) + (ad + bc)i`.
3. `__truediv__`: divide by `d = c² + d²`: real `(ac + bd)/d`, imaginary `(bc − ad)/d`.
4. `mod`: return `Complex(sqrt(a² + b²), 0)`.
5. The stub's `__str__` prints each result with two decimals.

```python
import math

class Complex(object):
    def __init__(self, real, imaginary):
        self.real = real
        self.imaginary = imaginary

    def __add__(self, no):
        return Complex(self.real + no.real, self.imaginary + no.imaginary)

    def __sub__(self, no):
        return Complex(self.real - no.real, self.imaginary - no.imaginary)

    def __mul__(self, no):
        return Complex(self.real * no.real - self.imaginary * no.imaginary,
                       self.real * no.imaginary + self.imaginary * no.real)

    def __truediv__(self, no):
        d = no.real ** 2 + no.imaginary ** 2
        return Complex((self.real * no.real + self.imaginary * no.imaginary) / d,
                       (self.imaginary * no.real - self.real * no.imaginary) / d)

    def mod(self):
        return Complex(math.sqrt(self.real ** 2 + self.imaginary ** 2), 0)

    def __str__(self):
        if self.imaginary == 0:
            result = "%.2f+0.00i" % (self.real)
        elif self.real == 0:
            if self.imaginary >= 0:
                result = "0.00+%.2fi" % (self.imaginary)
            else:
                result = "0.00-%.2fi" % (abs(self.imaginary))
        elif self.imaginary > 0:
            result = "%.2f+%.2fi" % (self.real, self.imaginary)
        else:
            result = "%.2f-%.2fi" % (self.real, abs(self.imaginary))
        return result

if __name__ == '__main__':
    c = map(float, input().split())
    d = map(float, input().split())
    x = Complex(*c)
    y = Complex(*d)
    print(*map(str, [x + y, x - y, x * y, x / y, x.mod(), y.mod()]), sep='\n')
```

**Watch out.** `__str__` is given in the stub; you only write the arithmetic methods. In Python 3 division is `__truediv__` (not `__div__`).

```stdin
2 1
5 6
```

```stdout
7.00+7.00i
-3.00-5.00i
4.00+17.00i
0.26-0.11i
2.24+0.00i
7.81+0.00i
```

### Class 2 - Find the Torsional Angle

**Problem.** Given points A, B, C, D in 3D, compute the angle between the planes ABC and BCD in degrees (2 decimals).

**Idea.** Complete the `Points` class: subtraction (vector between points), dot product, cross product. The stub then computes `X = AB × BC`, `Y = BC × CD` and the angle `acos(X·Y / (|X||Y|))`.

**Steps.**
1. `__sub__`: subtract the coordinates, giving the vector from one point to another.
2. `dot`: `x1·x2 + y1·y2 + z1·z2`.
3. `cross`: `(y1z2 − z1y2, z1x2 − x1z2, x1y2 − y1x2)`.
4. `absolute`: the length `sqrt(x² + y² + z²)`.
5. The stub computes `X = AB × BC`, `Y = BC × CD`, and the angle `acos(X·Y / (|X|·|Y|))` in degrees.

```python
import math

class Points(object):
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def __sub__(self, no):
        return Points(self.x - no.x, self.y - no.y, self.z - no.z)

    def dot(self, no):
        return self.x * no.x + self.y * no.y + self.z * no.z

    def cross(self, no):
        return Points(self.y * no.z - self.z * no.y,
                      self.z * no.x - self.x * no.z,
                      self.x * no.y - self.y * no.x)

    def absolute(self):
        return pow((self.x ** 2 + self.y ** 2 + self.z ** 2), 0.5)

if __name__ == '__main__':
    points = list()
    for i in range(4):
        a = list(map(float, input().split()))
        points.append(a)

    a, b, c, d = Points(*points[0]), Points(*points[1]), Points(*points[2]), Points(*points[3])
    x = (b - a).cross(c - b)
    y = (c - b).cross(d - c)
    angle = math.acos(x.dot(y) / (x.absolute() * y.absolute()))

    print("%.2f" % math.degrees(angle))
```

**Watch out.** Cross product order: `(y1z2 − z1y2, z1x2 − x1z2, x1y2 − y1x2)`.

```stdin
0 4 5
1 7 6
0 5 9
1 7 2
```

```stdout
8.19
```

## Built-Ins

### Zipped!

**Problem.** `X` subjects, each with marks for `N` students. Print each student's average.

**Idea.** The input is subject-by-subject; `zip(*rows)` turns it into student-by-student.

**Steps.**
1. Read `n` (students) and `x` (subjects).
2. Read `x` lines; each line has one subject's marks for every student.
3. `zip(*rows)` regroups them so each item holds one student's marks across all subjects.
4. For each student, print `sum(marks) / x`.

```python
n, x = map(int, input().split())
rows = [map(float, input().split()) for _ in range(x)]
for marks in zip(*rows):
    print(sum(marks) / x)
```

**Watch out.** Divide by the number of subjects `X`, not students.

```stdin
5 3
89 90 78 93 80
90 91 85 88 86
91 92 83 89 90.5
```

```stdout
90.0
91.0
82.0
90.0
85.5
```

### Input()

**Problem.** Given `x` and `k`, read a polynomial `P` in `x` and print whether `P(x) == k`.

**Idea.** `eval()` evaluates the polynomial string using the variable `x` that exists in the program.

**Steps.**
1. Read `x` and `k` as integers. The variable `x` now exists in the program.
2. Read the polynomial as text, e.g. `x**3 + x**2 + x + 1`.
3. `eval(...)` computes it using the current `x`.
4. Print whether the result equals `k`.

```python
x, k = map(int, input().split())
print(eval(input()) == k)
```

**Watch out.** In Python 2, `input()` itself evaluated the text; in Python 3 use `eval(input())`. Never `eval` untrusted input in real programs.

```stdin
1 4
x**3 + x**2 + x + 1
```

```stdout
True
```

### Python Evaluation

**Problem.** Read one line of Python code (like `print(2 + 3)`) and run it.

**Idea.** `eval()` runs an expression; `print(...)` is a function call, so it's an expression.

**Steps.**
1. Read the line of code as a string.
2. `eval(...)` runs it as Python. `print(2 + 3)` prints `5` by itself, so no extra `print` is needed.

```python
eval(input())
```

**Watch out.** For statements (like `x = 5`), you'd need `exec()` instead.

```stdin
print(2 + 3)
```

```stdout
5
```

### Athlete Sort

**Problem.** Sort the rows of a table by the `K`-th attribute (0-indexed), keeping the original order for ties, and print them.

**Idea.** `sorted` is stable, so `key=lambda row: row[k]` keeps ties in input order.

**Steps.**
1. Read the `n` rows as lists of integers, then `k`.
2. `sorted(arr, key=lambda row: row[k])` sorts by column `k`.
3. The sort is stable, so rows with equal values keep their input order.
4. Print each row with its values separated by spaces.

```python
if __name__ == '__main__':
    n, m = map(int, input().split())
    arr = [list(map(int, input().split())) for _ in range(n)]
    k = int(input())

    for row in sorted(arr, key=lambda row: row[k]):
        print(*row)
```

**Watch out.** Values must be integers so `10` sorts after `9`.

```stdin
5 3
10 2 5
7 1 0
9 9 9
1 23 12
6 5 9
1
```

```stdout
7 1 0
10 2 5
6 5 9
9 9 9
1 23 12
```

### Any or All

**Problem.** Print `True` if all integers are positive **and** at least one is a palindrome.

**Idea.** `all()` for the first condition, `any()` with `s == s[::-1]` for the second.

**Steps.**
1. Read the numbers as strings.
2. `all(int(x) > 0 for x in nums)`: are all of them positive?
3. `any(x == x[::-1] for x in nums)`: is at least one a palindrome (same when reversed)?
4. Print the two results combined with `and`.

```python
input()
nums = input().split()
print(all(int(x) > 0 for x in nums) and any(x == x[::-1] for x in nums))
```

**Watch out.** Keep the numbers as strings for the palindrome check; convert to `int` for the sign check. HackerRank expects this as few lines as possible, but readability is fine too.

```stdin
5
12 9 61 5 14
```

```stdout
True
```

### ginortS

**Problem.** Sort a string so that lowercase letters come first, then uppercase, then odd digits, then even digits (each group sorted).

**Idea.** Sort with a tuple key: Python compares tuples element by element, and `False < True`.

**Steps.**
1. Give each character a sort key tuple: `(is digit, is upper, is even digit, the character)`.
2. Python compares tuples left to right and `False < True`, so lowercase letters come first, then uppercase, then odd digits, then even digits.
3. The last item, the character itself, sorts within each group.
4. Join the sorted characters and print.

```python
s = input()
print(''.join(sorted(s, key=lambda c: (c.isdigit(), c.isupper(),
                                       c.isdigit() and int(c) % 2 == 0, c))))
```

**Watch out.** Key for each kind: lowercase `(F, F, F, c)`, uppercase `(F, T, F, c)`, odd digit `(T, F, F, c)`, even digit `(T, F, T, c)`, which gives exactly the required order.

```stdin
Sorting1234
```

```stdout
ginortS1324
```

## Python Functionals

### Map and Lambda Function

**Problem.** Generate the first `n` Fibonacci numbers (starting 0, 1) and print their cubes as a list using `map` and a lambda.

**Idea.** Build the Fibonacci list, then `map(cube, ...)`.

**Steps.**
1. `cube = lambda x: x ** 3`.
2. Build the Fibonacci list: start with `a, b = 0, 1`; `n` times, append `a`, then `a, b = b, a + b`.
3. `map(cube, fib)` cubes every number; wrap it in `list()` and print.

```python
cube = lambda x: x ** 3

def fibonacci(n):
    fib = []
    a, b = 0, 1
    for _ in range(n):
        fib.append(a)
        a, b = b, a + b
    return fib

if __name__ == '__main__':
    n = int(input())
    print(list(map(cube, fibonacci(n))))
```

**Watch out.** `n` can be 0, so build the list with a loop instead of starting with `[0, 1]`.

```stdin
5
```

```stdout
[0, 1, 1, 8, 27]
```

### Validating Email Addresses With a Filter

**Problem.** Keep the valid emails (`username@websitename.extension`: username = letters, digits, `-`, `_`; website = letters and digits; extension 1–3 letters) and print them sorted.

**Idea.** A regex in `fun(s)`, used by the stub's `filter`.

**Steps.**
1. Pattern: username `[\w-]+`, then `@`, website `[A-Za-z0-9]+`, a dot, extension `[A-Za-z]{1,3}`.
2. `fun(s)` returns True only if `re.fullmatch` matches the whole string.
3. `filter(fun, emails)` keeps the valid ones.
4. The stub sorts them and prints the list.

```python
import re

def fun(s):
    return bool(re.fullmatch(r'[\w-]+@[A-Za-z0-9]+\.[A-Za-z]{1,3}', s))

def filter_mail(emails):
    return list(filter(fun, emails))

if __name__ == '__main__':
    n = int(input())
    emails = []
    for _ in range(n):
        emails.append(input())

    filtered_emails = filter_mail(emails)
    filtered_emails.sort()
    print(filtered_emails)
```

**Watch out.** `\w` = letters, digits and `_`, so `[\w-]` covers the username rules. `fullmatch` makes sure the **whole** string matches.

```stdin
3
lara@hackerrank.com
brian-23@hackerrank.com
britts_54@hackerrank.com
```

```stdout
['brian-23@hackerrank.com', 'britts_54@hackerrank.com', 'lara@hackerrank.com']
```

### Reduce Function

**Problem.** Print the numerator and denominator of the product of `n` fractions, using `reduce`.

**Idea.** `reduce(lambda x, y: x * y, fracs)` multiplies them all; `Fraction` keeps the result reduced.

**Steps.**
1. Read each fraction as `Fraction(numerator, denominator)`.
2. `reduce(lambda x, y: x * y, fracs)` multiplies the first two, then that result by the third, and so on.
3. `Fraction` keeps the result in lowest terms automatically.
4. Return `t.numerator, t.denominator`; the stub prints them.

```python
from fractions import Fraction
from functools import reduce

def product(fracs):
    t = reduce(lambda x, y: x * y, fracs)
    return t.numerator, t.denominator

if __name__ == '__main__':
    fracs = []
    for _ in range(int(input())):
        fracs.append(Fraction(*map(int, input().split())))
    result = product(fracs)
    print(*result)
```

**Watch out.** `operator.mul` can replace the lambda: `reduce(operator.mul, fracs)`.

```stdin
3
1 2
3 4
10 6
```

```stdout
5 8
```

## Regex and Parsing

### Detect Floating Point Number

**Problem.** For each string, print whether it's a float with optional sign, **exactly one dot**, and at least one digit after the dot.

**Idea.** Regex: optional `+`/`-`, any digits, a dot, one or more digits.

**Steps.**
1. Pattern: `[+-]?` optional sign, `\d*` any digits, `\.` exactly one dot, `\d+` at least one digit after it.
2. For each string, `re.fullmatch` checks that the whole string fits the pattern.
3. Print `bool(...)` → `True` or `False`.

```python
import re

for _ in range(int(input())):
    print(bool(re.fullmatch(r'[+-]?\d*\.\d+', input())))
```

**Watch out.** `"12."` is invalid (needs a digit after the dot); `".5"` and `"-.7"` are valid.

```stdin
4
4.0O0
-1.00
+4.54
SomeRandomStuff
```

```stdout
False
True
True
False
```

### Re.split()

**Problem.** Fill in `regex_pattern` so that `re.split` splits a number on `,` and `.`.

**Idea.** A character class with both separators.

**Steps.**
1. Set `regex_pattern = r"[.,]"`: split on a dot **or** a comma.
2. `re.split(regex_pattern, number)` returns the pieces between separators.
3. The stub prints them one per line.

```python
regex_pattern = r"[.,]"   # Do not delete 'r'.

import re
print("\n".join(re.split(regex_pattern, input())))
```

**Watch out.** Inside `[...]`, the dot is a literal dot.

```stdin
100,000,000.000
```

```stdout
100
000
000
000
```

### Group(), Groups() & Groupdict()

**Problem.** Print the first alphanumeric character that repeats **consecutively**, or `-1`.

**Idea.** A capturing group followed by a backreference `\1` matches "the same character again".

**Steps.**
1. `([a-zA-Z0-9])` captures one alphanumeric character as group 1.
2. `\1` requires the very same character immediately after it.
3. `re.search` finds the first place this happens.
4. Print `m.group(1)` if found, otherwise `-1`.

```python
import re

m = re.search(r'([a-zA-Z0-9])\1', input())
print(m.group(1) if m else -1)
```

**Watch out.** `\w` would also match `_`, which isn't alphanumeric here.

```stdin
..12345678910111213141516171820212223
```

```stdout
1
```

### Re.findall() & Re.finditer()

**Problem.** Find all substrings of 2+ vowels that sit **between two consonants**; print each, or `-1`.

**Idea.** Lookbehind and lookahead check the consonants without consuming them, so neighbouring matches can share a consonant.

**Steps.**
1. Middle part: `[aeiou]{2,}` matches two or more vowels.
2. `(?<=[consonants])` and `(?=[consonants])` require a consonant before and after, without including it in the match.
3. `re.findall(..., flags=re.IGNORECASE)` collects all matches, upper or lower case.
4. Print each match on its own line, or `-1` if there are none.

```python
import re

consonants = 'qwrtypsdfghjklzxcvbnm'
pattern = rf'(?<=[{consonants}])[aeiou]{{2,}}(?=[{consonants}])'
matches = re.findall(pattern, input(), flags=re.IGNORECASE)
print('\n'.join(matches) if matches else -1)
```

**Watch out.** In an f-string, `{{2,}}` produces the literal `{2,}`. `re.IGNORECASE` handles uppercase letters.

```stdin
rabcdeefgyYhFjkIoomnpOeorteeeeet
```

```stdout
ee
Ioo
Oeo
eeeee
```

### Re.start() & Re.end()

**Problem.** Print the `(start, end)` indexes of every (possibly overlapping) occurrence of `k` in `S`, or `(-1, -1)`.

**Idea.** A zero-width lookahead `(?=k)` matches at every position where `k` starts, including overlaps.

**Steps.**
1. `(?=k)` is a lookahead: it matches the empty string at every position where `k` starts, so overlaps are found.
2. `re.escape(k)` makes special characters in `k` literal.
3. For each match, print `(start, start + len(k) - 1)`.
4. If nothing matched, print `(-1, -1)`.

```python
import re

s = input()
k = input()
found = False
for m in re.finditer(rf'(?={re.escape(k)})', s):
    print((m.start(), m.start() + len(k) - 1))
    found = True
if not found:
    print((-1, -1))
```

**Watch out.** A normal search would skip overlapping matches (`aa` in `aaa`). `re.escape` protects special characters in `k`.

```stdin
aaadaa
aa
```

```stdout
(0, 1)
(1, 2)
(4, 5)
```

### Regex Substitution

**Problem.** Replace `&&` with `and` and `||` with `or`, but only when surrounded by spaces on both sides.

**Idea.** Lookarounds `(?<= )` and `(?= )` require spaces without consuming them, so consecutive operators (`&& &&`) are both replaced.

**Steps.**
1. `(?<= )&&(?= )` matches `&&` only with a space on each side; replace it with `and`.
2. `(?<= )\|\|(?= )` does the same for `||` → `or` (the `|` must be escaped).
3. The lookarounds don't consume the spaces, so `a && && b` replaces both.
4. Print each modified line.

```python
import re

for _ in range(int(input())):
    line = input()
    line = re.sub(r'(?<= )&&(?= )', 'and', line)
    line = re.sub(r'(?<= )\|\|(?= )', 'or', line)
    print(line)
```

**Watch out.** `|` must be escaped (`\|`), it means "or" in regex. `&&&` and `|||` stay unchanged.

```stdin
11
a = 1;
b = input();

if a + b > 0 && a - b < 0:
    start()
elif a*b > 10 || a/b < 1:
    stop()
print set(list(a)) | set(list(b))
#Note do not change &&& or ||| or & or |
#Only change those '&&' which have space on both sides.
#Only change those '|| which have space on both sides.
```

```stdout
a = 1;
b = input();

if a + b > 0 and a - b < 0:
    start()
elif a*b > 10 or a/b < 1:
    stop()
print set(list(a)) | set(list(b))
#Note do not change &&& or ||| or & or |
#Only change those '&&' which have space on both sides.
#Only change those '|| which have space on both sides.
```

### Validating Roman Numerals

**Problem.** Fill in `regex_pattern` to validate Roman numerals from 1 to 3999.

**Idea.** One part per decimal place: thousands `M{0,3}`, hundreds `CM|CD|D?C{0,3}`, tens `XC|XL|L?X{0,3}`, ones `IX|IV|V?I{0,3}`.

**Steps.**
1. Thousands: `M{0,3}` (0 to 3000).
2. Hundreds: `CM|CD|D?C{0,3}` covers 900, 400 and 0–300 / 500–800.
3. Tens: `XC|XL|L?X{0,3}` the same way; ones: `IX|IV|V?I{0,3}`.
4. `re.match` anchors the start and `$` the end, so the whole string must match.

```python
regex_pattern = r"M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"   # Do not delete 'r'.

import re
print(str(bool(re.match(regex_pattern, input()))))
```

**Watch out.** `re.match` anchors at the start; the `$` anchors the end.

```stdin
CDXXI
```

```stdout
True
```

### Validating phone numbers

**Problem.** A valid number has exactly 10 digits and starts with 7, 8 or 9. Print `YES` or `NO`.

**Idea.** `[789]\d{9}` with `fullmatch`.

**Steps.**
1. Pattern `[789]\d{9}`: first digit 7, 8 or 9, then exactly 9 more digits.
2. For each number, `re.fullmatch` checks the whole string.
3. Print `YES` if it matches, otherwise `NO`.

```python
import re

for _ in range(int(input())):
    print("YES" if re.fullmatch(r'[789]\d{9}', input()) else "NO")
```

**Watch out.** Without full matching, an 11-digit number would pass.

```stdin
2
9587456281
1252478965
```

```stdout
YES
NO
```

### Validating and Parsing Email Addresses

**Problem.** Lines look like `name <user@domain.ext>`. Print the lines whose email is valid: username starts with a letter, then letters/digits/`-`/`.`/`_`; domain letters only; extension 1–3 letters.

**Idea.** `email.utils.parseaddr` splits name and address; validate the address with a regex; print the original line.

**Steps.**
1. `email.utils.parseaddr(line)` splits `name <user@domain.ext>` into `(name, address)`.
2. Check the address against `[A-Za-z][\w.-]*@[A-Za-z]+\.[A-Za-z]{1,3}` with `fullmatch`.
3. If it's valid, print `formataddr((name, addr))`, which rebuilds the original line.

```python
import re
import email.utils

pattern = re.compile(r'[A-Za-z][\w.-]*@[A-Za-z]+\.[A-Za-z]{1,3}')
for _ in range(int(input())):
    line = input()
    name, addr = email.utils.parseaddr(line)
    if pattern.fullmatch(addr):
        print(email.utils.formataddr((name, addr)))
```

**Watch out.** `formataddr` rebuilds the line in the same `name <addr>` format.

```stdin
2
DEXTER <dexter@hotmail.com>
VIRUS <virus!@variable.:p>
```

```stdout
DEXTER <dexter@hotmail.com>
```

### Hex Color Code

**Problem.** In CSS code, print every hex color (`#` + 3 or 6 hex digits) that appears **inside** a `{ }` block (selectors like `#BED` are not colors).

**Idea.** Track whether you're inside braces; inside, find `#` followed by 6 or 3 hex digits that aren't followed by another letter/digit.

**Steps.**
1. Keep a flag `inside`: set it on a line with `{`, clear it on a line with `}`.
2. Only search lines while `inside` is True (selectors like `#BED` are outside the braces).
3. Pattern: `#` then 6 or 3 hex digits, not followed by another letter or digit.
4. Print every color found, in order.

```python
import re

pattern = re.compile(r'#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})(?![0-9a-zA-Z])')
inside = False
for _ in range(int(input())):
    line = input()
    if '{' in line:
        inside = True
    elif '}' in line:
        inside = False
    elif inside:
        for color in pattern.findall(line):
            print(color)
```

**Watch out.** Try 6 digits before 3, otherwise `#FfFdF8` would match as `#FfF`. The negative lookahead rejects things like `#fffabg`.

```stdin
11
#BED
{
    color: #FfFdF8; background-color:#aef;
    font-size: 123px;
    background: -webkit-linear-gradient(top, #f9f9f9, #fff);
}
#Cab
{
    background-color: #ABC;
    border: 2px dashed #fff;
}
```

```stdout
#FfFdF8
#aef
#f9f9f9
#fff
#ABC
#fff
```

### HTML Parser - Part 1

**Problem.** Print start tags, end tags and empty tags (with their attributes) of an HTML snippet in the given format, ignoring comments.

**Idea.** Subclass `HTMLParser` and override `handle_starttag`, `handle_endtag`, `handle_startendtag`. Comments are ignored by default.

**Steps.**
1. Subclass `HTMLParser`.
2. `handle_starttag`: print `Start : tag`, then each attribute as `-> name > value`.
3. `handle_endtag`: print `End   : tag` (three spaces).
4. `handle_startendtag` (self-closing like `<br />`): print `Empty : tag` and its attributes.
5. Feed each input line to the parser; comments are skipped by default.

```python
from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        print("Start :", tag)
        for name, value in attrs:
            print("->", name, ">", value)

    def handle_endtag(self, tag):
        print("End   :", tag)

    def handle_startendtag(self, tag, attrs):
        print("Empty :", tag)
        for name, value in attrs:
            print("->", name, ">", value)

parser = MyHTMLParser()
for _ in range(int(input())):
    parser.feed(input())
```

**Watch out.** Note the three spaces in `End   :`. An attribute without a value prints `None`.

```stdin
2
<html><head><title>HTML Parser - I</title></head>
<body data-modal-target class='1'><h1>HackerRank</h1><br /></body></html>
```

```stdout
Start : html
Start : head
Start : title
End   : title
End   : head
Start : body
-> data-modal-target > None
-> class > 1
Start : h1
End   : h1
Empty : br
End   : body
End   : html
```

### HTML Parser - Part 2

**Problem.** Print single-line comments, multi-line comments and data blocks in the given format (skip data that's only a newline).

**Idea.** Override `handle_comment` (multi-line if it contains `\n`) and `handle_data`.

**Steps.**
1. Subclass `HTMLParser`.
2. `handle_comment`: print `>>> Multi-line Comment` if the text contains `\n`, else `>>> Single-line Comment`; then print the text.
3. `handle_data`: skip data that is just `\n`; otherwise print `>>> Data` and the text.
4. Feed the whole HTML at once so multi-line comments arrive in one piece.

```python
from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    def handle_comment(self, data):
        if '\n' in data:
            print(">>> Multi-line Comment")
        else:
            print(">>> Single-line Comment")
        print(data)

    def handle_data(self, data):
        if data != '\n':
            print(">>> Data")
            print(data)

html = ""
for i in range(int(input())):
    html += input().rstrip()
    html += '\n'

parser = MyHTMLParser()
parser.feed(html)
parser.close()
```

**Watch out.** Feed the whole HTML at once (as the stub does) so multi-line comments arrive as one piece.

```stdin
4
<!--[if IE 9]>IE9-specific content
<![endif]-->
<div> Welcome to HackerRank</div>
<!--[if IE 9]>IE9-specific content<![endif]-->
```

```stdout
>>> Multi-line Comment
[if IE 9]>IE9-specific content
<![endif]
>>> Data
 Welcome to HackerRank
>>> Single-line Comment
[if IE 9]>IE9-specific content<![endif]
```

### Detect HTML Tags, Attributes and Attribute Values

**Problem.** Print each tag name (start or empty tag), followed by its attributes as `-> name > value`. Ignore comments.

**Idea.** `HTMLParser` with `handle_starttag` (it is also called for self-closing tags by the default `handle_startendtag`).

**Steps.**
1. Subclass `HTMLParser` and override `handle_starttag`.
2. Print the tag name, then each attribute as `-> name > value`.
3. Self-closing tags also reach `handle_starttag` through the default `handle_startendtag`.
4. Join all input lines and feed them together, because a tag can span several lines.

```python
from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        print(tag)
        for name, value in attrs:
            print("->", name, ">", value)

parser = MyHTMLParser()
parser.feed(''.join(input() + '\n' for _ in range(int(input()))))
```

**Watch out.** Feed all lines together because a tag can span several lines.

```stdin
9
<head>
<title>HTML</title>
</head>
<object type="application/x-flash"
  data="your-file.swf"
  width="0" height="0">
  <!-- <param name="movie" value="your-file.swf" /> -->
  <param name="quality" value="high"/>
</object>
```

```stdout
head
title
object
-> type > application/x-flash
-> data > your-file.swf
-> width > 0
-> height > 0
param
-> name > quality
-> value > high
```

### Validating UID

**Problem.** A UID is valid if it has exactly 10 alphanumeric characters, at least 2 uppercase letters, at least 3 digits, and no repeated character.

**Idea.** Check each rule separately; plain Python is clearer than one giant regex.

**Steps.**
1. Length is exactly 10 and every character is a letter or digit (`isalnum`).
2. At least 2 uppercase letters: `sum(c.isupper() for c in uid) >= 2`.
3. At least 3 digits: `sum(c.isdigit() for c in uid) >= 3`.
4. No repeats: `len(set(uid)) == 10`.
5. Print `Valid` only if all checks pass.

```python
def valid(uid):
    return (len(uid) == 10 and uid.isalnum()
            and sum(c.isupper() for c in uid) >= 2
            and sum(c.isdigit() for c in uid) >= 3
            and len(set(uid)) == 10)

for _ in range(int(input())):
    print("Valid" if valid(input().strip()) else "Invalid")
```

**Watch out.** `len(set(uid)) == 10` is the "no repeats" check.

```stdin
2
B1CD102354
B1CDEF2354
```

```stdout
Invalid
Valid
```

### Validating Credit Card Numbers

**Problem.** Valid: starts with 4, 5 or 6; 16 digits, optionally in groups of 4 separated by a single `-`; no other characters; no digit repeated 4+ times in a row (ignoring hyphens).

**Idea.** One regex for the format (the backreference `\1` forces the same separator everywhere), then a second check for 4 repeated digits after removing hyphens.

**Steps.**
1. Format regex: `[456]` first digit, then 3 digits, then `(-?)` an optional hyphen captured as group 1.
2. The next groups use `\1`, so they must use the same separator (all hyphens or none).
3. Remove the hyphens and reject the card if `(\d)\1{3}` finds a digit repeated 4 times in a row.
4. Print `Valid` if the format matches and there are no 4 repeats, otherwise `Invalid`.

```python
import re

fmt = re.compile(r'[456]\d{3}(-?)\d{4}\1\d{4}\1\d{4}')
for _ in range(int(input())):
    card = input().strip()
    ok = fmt.fullmatch(card) and not re.search(r'(\d)\1{3}', card.replace('-', ''))
    print("Valid" if ok else "Invalid")
```

**Watch out.** Check the repeated digits **after** removing hyphens: `4444-4444` style repeats cross group boundaries.

```stdin
6
4123456789123456
5123-4567-8912-3456
61234-567-8912-3456
4123356789123456
5133-3367-8912-3456
5123 - 3567 - 8912 - 3456
```

```stdout
Valid
Valid
Invalid
Valid
Invalid
Invalid
```

### Validating Postal Codes

**Problem.** Fill in two regexes: one for a number in 100000–999999, one that finds "alternating repetitive digit pairs" (same digit two places apart). The code is valid with fewer than 2 such pairs.

**Idea.** Range: first digit 1–9, then 5 digits. Alternating pair: a digit, any digit, the same digit again, written with a lookahead so overlapping pairs are all counted.

**Steps.**
1. Range check: `^[1-9][0-9]{5}$`, a 6-digit number that doesn't start with 0.
2. Pair check: `(\d)(?=\d\1)` finds a digit whose twin is two places later; the lookahead lets pairs overlap.
3. Count the pairs with `re.findall`.
4. Valid when the range matches **and** there are fewer than 2 pairs.

```python
regex_integer_in_range = r"^[1-9][0-9]{5}$"   # Do not delete 'r'.
regex_alternating_repetitive_digit_pair = r"(\d)(?=\d\1)"   # Do not delete 'r'.

import re
P = input()

print(bool(re.match(regex_integer_in_range, P))
      and len(re.findall(regex_alternating_repetitive_digit_pair, P)) < 2)
```

**Watch out.** Without the lookahead, `1010` would count only one pair because matches can't overlap.

```stdin
110000
```

```stdout
False
```

### Matrix Script

**Problem.** Read the matrix **column by column** to decode the script, then replace every run of non-alphanumeric characters **between two alphanumerics** with a single space.

**Idea.** Build the decoded string with a column-major comprehension, then `re.sub` with lookarounds so symbols at the start or end stay.

**Steps.**
1. Read `n` rows of width `m`, without stripping (trailing spaces matter).
2. Read column by column: for each column `c`, take `matrix[r][c]` for every row `r`, and join everything.
3. `re.sub` replaces each run of symbols that has a letter/digit on both sides with one space.
4. Symbols at the very start or end don't have both neighbours, so they stay. Print the result.

```python
import re

n, m = map(int, input().split())
matrix = [input() for _ in range(n)]

decoded = ''.join(matrix[r][c] for c in range(m) for r in range(n))
print(re.sub(r'(?<=[A-Za-z0-9])[^A-Za-z0-9]+(?=[A-Za-z0-9])', ' ', decoded))
```

**Watch out.** Lines can end with spaces that matter; don't strip them.

```stdin
7 3
Tsi
h%x
i #
sM 
$a 
#t%
ir!
```

```stdout
This is Matrix#  %!
```
