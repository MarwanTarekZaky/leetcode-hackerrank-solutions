## XML

### XML 1 - Find the Score

**Problem.** Return the total number of attributes across all elements of an XML document.

**Idea.** `node.iter()` walks the element and all its descendants; `len(element.attrib)` counts each element's attributes.

**Steps.**
1. `node.iter()` visits the root and every element inside it, at any depth.
2. For each element, `len(elem.attrib)` is how many attributes it has.
3. Add them all up with `sum(...)` and return the total.

```python
import sys
import xml.etree.ElementTree as etree

def get_attr_number(node):
    return sum(len(elem.attrib) for elem in node.iter())

if __name__ == '__main__':
    sys.stdin.readline()
    xml = sys.stdin.read()
    tree = etree.ElementTree(etree.fromstring(xml))
    root = tree.getroot()
    print(get_attr_number(root))
```

**Watch out.** `iter()` includes the root itself. Recursive version: `len(node.attrib) + sum(get_attr_number(child) for child in node)`.

```stdin
6
<feed xml:lang='en'>
    <title>HackerRank</title>
    <subtitle lang='en'>Programming challenges</subtitle>
    <link rel='alternate' type='text/html' href='http://hackerrank.com/'/>
    <updated>2013-12-25T12:00:00</updated>
</feed>
```

```stdout
5
```

### XML2 - Find the Maximum Depth

**Problem.** Find the maximum nesting depth of an XML document (the root is level 0).

**Idea.** Recursive DFS: increase the level when entering an element, update the global maximum, recurse into children.

**Steps.**
1. Start with `depth(root, -1)`; the first thing the function does is `level += 1`, so the root is level 0.
2. Update the global `maxdepth` with the current level.
3. Call `depth(child, level)` for every child, so each child is one level deeper.
4. After the walk finishes, print `maxdepth`.

```python
import xml.etree.ElementTree as etree

maxdepth = 0
def depth(elem, level):
    global maxdepth
    level += 1
    maxdepth = max(maxdepth, level)
    for child in elem:
        depth(child, level)

if __name__ == '__main__':
    n = int(input())
    xml = ""
    for i in range(n):
        xml = xml + input() + "\n"
    tree = etree.ElementTree(etree.fromstring(xml))
    depth(tree.getroot(), -1)
    print(maxdepth)
```

**Watch out.** The stub starts with level `-1`, so the root becomes level 0. `global maxdepth` is required to assign to the module-level variable.

```stdin
6
<feed xml:lang='en'>
    <title>HackerRank</title>
    <subtitle lang='en'>Programming challenges</subtitle>
    <link rel='alternate' type='text/html' href='http://hackerrank.com/'/>
    <updated>2013-12-25T12:00:00</updated>
</feed>
```

```stdout
1
```

## Closures and Decorators

### Standardize Mobile Number Using Decorators

**Problem.** Numbers come in different forms (`07895462130`, `919875641230`, `9195969878`, possibly with `+91`). Use a decorator to convert each to `+91 xxxxx xxxxx` before sorting and printing.

**Idea.** Keep only the **last 10 digits** of each number, format them, then call the decorated function with the cleaned list.

**Steps.**
1. `wrapper(f)` returns a new function `fun(l)` that cleans the list before calling `f`.
2. For each number, `n[-10:]` is the real 10-digit number whatever prefix it had (`0`, `91`, `+91`).
3. Format it as `+91 ` + first 5 digits + space + last 5 digits.
4. `@wrapper` makes `sort_phone` receive the cleaned list; it sorts and prints them.

```python
def wrapper(f):
    def fun(l):
        f(['+91 {} {}'.format(n[-10:-5], n[-5:]) for n in l])
    return fun

@wrapper
def sort_phone(l):
    print(*sorted(l), sep='\n')

if __name__ == '__main__':
    l = [input() for _ in range(int(input()))]
    sort_phone(l)
```

**Watch out.** A decorator is a function that takes a function and returns a new one; `@wrapper` above `sort_phone` means `sort_phone = wrapper(sort_phone)`.

```stdin
3
07895462130
919875641230
9195969878
```

```stdout
+91 78954 62130
+91 91959 69878
+91 98756 41230
```

### Decorators 2 - Name Directory

**Problem.** Print people's names as `Mr./Ms. First Last`, sorted by age (stable for equal ages), using a decorator.

**Idea.** The decorator sorts the people by age (as integers) and maps the original formatting function over them.

**Steps.**
1. Each person is `[first, last, age, sex]` (all strings).
2. The decorator's `inner(people)` sorts them by `int(p[2])`; the sort is stable, so equal ages keep input order.
3. It then applies the original `name_format` to each person with `map`.
4. `name_format` adds `Mr. ` for `M` or `Ms. ` for `F`, then the first and last name. The stub prints each line.

```python
import operator

def person_lister(f):
    def inner(people):
        return map(f, sorted(people, key=lambda p: int(p[2])))
    return inner

@person_lister
def name_format(person):
    return ("Mr. " if person[3] == "M" else "Ms. ") + person[0] + " " + person[1]

if __name__ == '__main__':
    people = [input().split() for i in range(int(input()))]
    print(*name_format(people), sep='\n')
```

**Watch out.** Ages are strings in the input; sort by `int(p[2])` so `9` comes before `10`.

```stdin
3
Mike Thomson 20 M
Robert Bustle 32 M
Andria Bustle 30 F
```

```stdout
Mr. Mike Thomson
Ms. Andria Bustle
Mr. Robert Bustle
```

## Numpy

### Arrays

**Problem.** Convert a list of numbers to a NumPy float array, reversed.

**Idea.** `numpy.array(arr[::-1], float)`.

**Steps.**
1. `arr[::-1]` reverses the list of strings.
2. `numpy.array(..., float)` converts it to a NumPy array of floats.
3. Return it; the stub prints it.

```python
import numpy
numpy.set_printoptions(legacy='1.13')

def arrays(arr):
    return numpy.array(arr[::-1], float)

arr = input().strip().split(' ')
result = arrays(arr)
print(result)
```

**Watch out.**
- The second argument of `numpy.array` is the dtype; it converts the strings to floats.
- HackerRank runs an older NumPy that prints float arrays in the "1.13 style" (`[ 1.  0.]`, with extra spaces). Newer NumPy prints `[1. 0.]`. `numpy.set_printoptions(legacy='1.13')` makes the output match on both, which is why it appears in the NumPy solutions that print floats.

```stdin
1 2 3 4 -8 -10
```

```stdout
[-10.  -8.   4.   3.   2.   1.]
```

### Shape and Reshape

**Problem.** Reshape 9 space-separated integers into a 3×3 array.

**Idea.** `numpy.array(...).reshape(3, 3)`.

**Steps.**
1. Read the 9 numbers into an integer NumPy array (shape `(9,)`).
2. `.reshape(3, 3)` arranges them into 3 rows of 3.
3. Print the result.

```python
import numpy

arr = numpy.array(input().split(), int)
print(arr.reshape(3, 3))
```

**Watch out.** `reshape` returns a new view; `arr.shape = (3, 3)` changes it in place.

```stdin
1 2 3 4 5 6 7 8 9
```

```stdout
[[1 2 3]
 [4 5 6]
 [7 8 9]]
```

### Transpose and Flatten

**Problem.** Read an `N × M` integer array; print its transpose, then its flattened form.

**Idea.** `numpy.transpose(a)` (or `a.T`) and `a.flatten()`.

**Steps.**
1. Read `n` rows of `m` numbers into a 2D integer array.
2. Print `numpy.transpose(a)`: rows become columns.
3. Print `a.flatten()`: all values in one row, read row by row.

```python
import numpy

n, m = map(int, input().split())
a = numpy.array([input().split() for _ in range(n)], int)
print(numpy.transpose(a))
print(a.flatten())
```

**Watch out.** Building the array from a list of lists of strings with `dtype=int` converts everything at once.

```stdin
2 2
1 2
3 4
```

```stdout
[[1 3]
 [2 4]]
[1 2 3 4]
```

### Concatenate

**Problem.** Read an `N × P` array and an `M × P` array; print them concatenated along axis 0.

**Idea.** `numpy.concatenate((a, b), axis=0)`.

**Steps.**
1. Read `n`, `m`, `p`.
2. Read the first `n` rows into array `a` and the next `m` rows into array `b`.
3. `numpy.concatenate((a, b), axis=0)` stacks `b` under `a`; print it.

```python
import numpy

n, m, p = map(int, input().split())
a = numpy.array([input().split() for _ in range(n)], int)
b = numpy.array([input().split() for _ in range(m)], int)
print(numpy.concatenate((a, b), axis=0))
```

**Watch out.** The arrays are passed as **one tuple** argument.

```stdin
4 3 2
1 2
1 2
1 2
1 2
3 4
3 4
3 4
```

```stdout
[[1 2]
 [1 2]
 [1 2]
 [1 2]
 [3 4]
 [3 4]
 [3 4]]
```

### Zeros and Ones

**Problem.** Given a shape, print an integer array of zeros and one of ones.

**Idea.** `numpy.zeros(shape, dtype=int)` and `numpy.ones(shape, dtype=int)`.

**Steps.**
1. Read the dimensions into a tuple, e.g. `(3, 3, 3)`.
2. Print `numpy.zeros(shape, dtype=int)`.
3. Print `numpy.ones(shape, dtype=int)`.

```python
import numpy

shape = tuple(map(int, input().split()))
print(numpy.zeros(shape, dtype=int))
print(numpy.ones(shape, dtype=int))
```

**Watch out.** Without `dtype=int` they'd print as floats (`0.`).

```stdin
3 3 3
```

```stdout
[[[0 0 0]
  [0 0 0]
  [0 0 0]]

 [[0 0 0]
  [0 0 0]
  [0 0 0]]

 [[0 0 0]
  [0 0 0]
  [0 0 0]]]
[[[1 1 1]
  [1 1 1]
  [1 1 1]]

 [[1 1 1]
  [1 1 1]
  [1 1 1]]

 [[1 1 1]
  [1 1 1]
  [1 1 1]]]
```

### Eye and Identity

**Problem.** Print an `N × M` array with 1s on the main diagonal and 0s elsewhere.

**Idea.** `numpy.eye(N, M)` (identity only works for square arrays).

**Steps.**
1. Read `n` (rows) and `m` (columns).
2. `numpy.eye(n, m)` builds an `n × m` float array with 1s on the main diagonal.
3. Print it (with the 1.13 print style HackerRank expects).

```python
import numpy
numpy.set_printoptions(legacy='1.13')

n, m = map(int, input().split())
print(numpy.eye(n, m))
```

**Watch out.** `numpy.eye(n, m, k=1)` would shift the diagonal up by one.

```stdin
3 3
```

```stdout
[[ 1.  0.  0.]
 [ 0.  1.  0.]
 [ 0.  0.  1.]]
```

### Array Mathematics

**Problem.** For arrays A and B (`N × M`), print `A + B`, `A - B`, `A * B`, `A // B`, `A % B`, `A ** B`.

**Idea.** NumPy operators work element by element.

**Steps.**
1. Read arrays A and B, each `n × m` integers.
2. Each operator works element by element: `a + b`, `a - b`, `a * b`.
3. Then `a // b` (integer division), `a % b` (remainder), `a ** b` (power).
4. Print the six results in that order.

```python
import numpy

n, m = map(int, input().split())
a = numpy.array([input().split() for _ in range(n)], int)
b = numpy.array([input().split() for _ in range(n)], int)
print(a + b)
print(a - b)
print(a * b)
print(a // b)
print(a % b)
print(a ** b)
```

**Watch out.** Use `//` (integer division); `/` would print floats.

```stdin
1 4
1 2 3 4
5 6 7 8
```

```stdout
[[ 6  8 10 12]]
[[-4 -4 -4 -4]]
[[ 5 12 21 32]]
[[0 0 0 0]]
[[1 2 3 4]]
[[    1    64  2187 65536]]
```

### Floor, Ceil and Rint

**Problem.** Print the floor, ceil and rint (round to nearest integer) of a float array.

**Idea.** `numpy.floor`, `numpy.ceil`, `numpy.rint`.

**Steps.**
1. Read the numbers into a float array.
2. `numpy.floor`: round each value down.
3. `numpy.ceil`: round each value up.
4. `numpy.rint`: round to the nearest integer (halves go to the even one). Print all three.

```python
import numpy
numpy.set_printoptions(legacy='1.13')

a = numpy.array(input().split(), float)
print(numpy.floor(a))
print(numpy.ceil(a))
print(numpy.rint(a))
```

**Watch out.** `rint` rounds halves to the nearest **even** number (`5.5 → 6`, `4.5 → 4`).

```stdin
1.1 2.2 3.3 4.4 5.5 6.6 7.7 8.8 9.9
```

```stdout
[ 1.  2.  3.  4.  5.  6.  7.  8.  9.]
[  2.   3.   4.   5.   6.   7.   8.   9.  10.]
[  1.   2.   3.   4.   6.   7.   8.   9.  10.]
```

### Sum and Prod

**Problem.** Sum an `N × M` array over axis 0, then print the product of that result.

**Idea.** `numpy.prod(numpy.sum(a, axis=0))`.

**Steps.**
1. Read the `n × m` integer array.
2. `numpy.sum(a, axis=0)` adds down each column, giving one number per column.
3. `numpy.prod(...)` multiplies those column sums; print it.

```python
import numpy

n, m = map(int, input().split())
a = numpy.array([input().split() for _ in range(n)], int)
print(numpy.prod(numpy.sum(a, axis=0)))
```

**Watch out.** Axis 0 sums **down the columns**.

```stdin
2 2
1 2
3 4
```

```stdout
24
```

### Min and Max

**Problem.** Take the minimum over axis 1, then print the maximum of that.

**Idea.** `numpy.max(numpy.min(a, axis=1))`.

**Steps.**
1. Read the `n × m` integer array.
2. `numpy.min(a, axis=1)` takes the smallest value in each row.
3. `numpy.max(...)` of those row minimums is the answer; print it.

```python
import numpy

n, m = map(int, input().split())
a = numpy.array([input().split() for _ in range(n)], int)
print(numpy.max(numpy.min(a, axis=1)))
```

**Watch out.** Axis 1 works **across each row**.

```stdin
4 2
2 5
3 7
1 3
4 0
```

```stdout
3
```

### Mean, Var, and Std

**Problem.** Print the mean over axis 1, the variance over axis 0, and the standard deviation over all values.

**Idea.** `numpy.mean`, `numpy.var`, `numpy.std` with the right `axis`.

**Steps.**
1. Read the `n × m` integer array.
2. Print `numpy.mean(a, axis=1)`: the average of each row.
3. Print `numpy.var(a, axis=0)`: the variance of each column.
4. Print `numpy.std(a)` over all values, rounded to 11 decimals.

```python
import numpy
numpy.set_printoptions(legacy='1.13')

n, m = map(int, input().split())
a = numpy.array([input().split() for _ in range(n)], int)
print(numpy.mean(a, axis=1))
print(numpy.var(a, axis=0))
print(round(numpy.std(a), 11))
```

**Watch out.** The expected std has 11 decimals (`1.11803398875`), which is how old NumPy printed it; `round(..., 11)` reproduces that on any version.

```stdin
2 2
1 2
3 4
```

```stdout
[ 1.5  3.5]
[ 1.  1.]
1.11803398875
```

### Dot and Cross

**Problem.** Print the matrix product of two `N × N` arrays.

**Idea.** `numpy.dot(a, b)` (for 2D arrays it's matrix multiplication).

**Steps.**
1. Read the two `n × n` integer matrices.
2. `numpy.dot(a, b)`: each cell `[i][j]` is row `i` of A times column `j` of B, summed.
3. Print the result.

```python
import numpy

n = int(input())
a = numpy.array([input().split() for _ in range(n)], int)
b = numpy.array([input().split() for _ in range(n)], int)
print(numpy.dot(a, b))
```

**Watch out.** `a * b` would multiply element by element, which is different. `a @ b` is the same as `dot` for 2D.

```stdin
2
1 2
3 4
1 2
3 4
```

```stdout
[[ 7 10]
 [15 22]]
```

### Inner and Outer

**Problem.** Print the inner product and the outer product of two 1D arrays.

**Idea.** `numpy.inner(a, b)` (sum of products) and `numpy.outer(a, b)` (every pair multiplied).

**Steps.**
1. Read the two 1D integer arrays.
2. `numpy.inner(a, b)`: multiply matching elements and add them up (one number).
3. `numpy.outer(a, b)`: the table where cell `[i][j] = a[i] * b[j]`.
4. Print the inner product, then the outer product.

```python
import numpy

a = numpy.array(input().split(), int)
b = numpy.array(input().split(), int)
print(numpy.inner(a, b))
print(numpy.outer(a, b))
```

**Watch out.** The outer product of sizes `n` and `m` is an `n × m` matrix.

```stdin
0 1
2 3
```

```stdout
3
[[0 0]
 [2 3]]
```

### Polynomials

**Problem.** Given polynomial coefficients (highest power first) and a value `x`, print the polynomial evaluated at `x`.

**Idea.** `numpy.polyval(coefficients, x)`.

**Steps.**
1. Read the coefficients as floats, highest power first (`1.1 2 3` means `1.1x² + 2x + 3`).
2. Read `x`.
3. `numpy.polyval(coefficients, x)` evaluates the polynomial at `x`; print it.

```python
import numpy

coefficients = list(map(float, input().split()))
x = float(input())
print(numpy.polyval(coefficients, x))
```

**Watch out.** Coefficients go from the highest power down to the constant.

```stdin
1.1 2 3
0
```

```stdout
3.0
```

### Linear Algebra

**Problem.** Print the determinant of an `N × N` matrix, rounded to 2 decimals.

**Idea.** `numpy.linalg.det(a)`, then `round(..., 2)`.

**Steps.**
1. Read the `n × n` matrix as floats.
2. `numpy.linalg.det(a)` computes the determinant.
3. Round to 2 decimals to hide floating-point noise, and print.

```python
import numpy

n = int(input())
a = numpy.array([input().split() for _ in range(n)], float)
print(round(numpy.linalg.det(a), 2))
```

**Watch out.** The determinant is computed with floating point, so it can come out as `-0.0` or `1e-16` without rounding.

```stdin
2
1.1 1.1
1.1 1.1
```

```stdout
0.0
```

## Debugging

### Words Score

**Problem.** Fix the given code: a word scores 2 if it has an even number of vowels (a, e, i, o, u, y), else 1. Print the total.

**Idea.** The bug is `++score`: Python has no `++` operator, so `++score` just means `+(+score)` and does nothing. Replace it with `score += 1`.

**Steps.**
1. Find the bug: `++score` does nothing in Python (it's just `+(+score)`).
2. Replace it with `score += 1`.
3. Everything else stays: count the vowels in each word; even count → `+2`, odd → `+1`.

```python
def is_vowel(letter):
    return letter in ['a', 'e', 'i', 'o', 'u', 'y']

def score_words(words):
    score = 0
    for word in words:
        num_vowels = 0
        for letter in word:
            if is_vowel(letter):
                num_vowels += 1
        if num_vowels % 2 == 0:
            score += 2
        else:
            score += 1
    return score

n = int(input())
words = input().split()
print(score_words(words))
```

**Watch out.** Only one line changes; the rest of the given code is correct.

```stdin
2
hacker book
```

```stdout
4
```

### Default Arguments

**Problem.** Fix the code: `print_from_stream(n, stream=EvenStream())` gives wrong results when called more than once.

**Idea.** A default argument is created **once**, when the function is defined, so every call shares the same `EvenStream` and it keeps counting from where the last call stopped. Use `None` as the default and create a fresh stream inside the function.

**Steps.**
1. Find the bug: `stream=EvenStream()` is created only once, when the function is defined, and shared by every call.
2. Change the default to `stream=None`.
3. Inside the function, `if stream is None: stream = EvenStream()` makes a fresh stream on each call.
4. Print `n` values from the stream as before.

```python
class EvenStream(object):
    def __init__(self):
        self.current = 0

    def get_next(self):
        to_return = self.current
        self.current += 2
        return to_return

class OddStream(object):
    def __init__(self):
        self.current = 1

    def get_next(self):
        to_return = self.current
        self.current += 2
        return to_return

def print_from_stream(n, stream=None):
    if stream is None:
        stream = EvenStream()
    for _ in range(n):
        print(stream.get_next())

queries = int(input())
for _ in range(queries):
    stream_name, n = input().split()
    n = int(n)
    if stream_name == "even":
        print_from_stream(n)
    else:
        print_from_stream(n, OddStream())
```

**Watch out.** The same trap happens with `def f(items=[])`: the list is shared between calls. Always use `None` for mutable defaults.

```stdin
3
odd 2
even 3
odd 5
```

```stdout
1
3
0
2
4
1
3
5
7
9
```
