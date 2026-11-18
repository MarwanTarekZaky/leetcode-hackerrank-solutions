## SOLID Principles

### Single Responsibility Principle

**Problem.** A `Report` class formats the report, saves it to disk and emails it. A new layout, a new storage folder or a new mail server all mean editing the same class, and you can't test the formatting without a disk and an SMTP server.

```py
class Report:
    def __init__(self, title, rows):
        self.title, self.rows = title, rows

    def render(self):              # layout
        ...

    def save(self, path):          # file system
        open(path, "w").write(self.render())

    def email(self, to):           # SMTP
        smtplib.SMTP("mail.local").sendmail("me", to, self.render())
```

**Task.** Split it so each class has **one reason to change**. For title `Q1` and rows `[("a", 1), ("b", 2)]`, the formatter must return `"Q1\n- a: 1\n- b: 2\nTotal: 3"`.

**Idea.** *"A class should have one, and only one, reason to change"* (Robert C. Martin). Group code by **who asks for the change**: the data rules, the layout, the storage and the delivery change for different reasons, so they live in different classes. Each piece becomes small, easy to test and reusable on its own.

**Steps.**
1. Keep `Report` as plain data plus the rules about that data (`total()`).
2. Move the layout into `ReportFormatter.render(report) -> str`.
3. Move file writing into `ReportSaver`, configured with a folder.
4. Move sending into `ReportMailer`, which receives the `send` function from outside, so a test can pass a fake.

```python
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Report:
    title: str
    rows: list[tuple[str, int]] = field(default_factory=list)

    def total(self) -> int:
        return sum(value for _, value in self.rows)


class ReportFormatter:
    # changes only when the layout changes
    def render(self, report: Report) -> str:
        lines = [report.title]
        lines += [f"- {name}: {value}" for name, value in report.rows]
        lines.append(f"Total: {report.total()}")
        return "\n".join(lines)


class ReportSaver:
    # changes only when the storage changes
    def __init__(self, folder: Path):
        self.folder = Path(folder)

    def save(self, name: str, text: str) -> Path:
        path = self.folder / f"{name}.txt"
        path.write_text(text)
        return path


class ReportMailer:
    # changes only when the way we send mail changes
    def __init__(self, send):
        self.send = send  # send(to, subject, body), injected so tests can fake it

    def mail(self, to: str, report: Report, text: str) -> None:
        self.send(to, report.title, text)


if __name__ == "__main__":
    report = Report("Sales", [("apples", 3), ("pears", 5)])
    text = ReportFormatter().render(report)
    print(text)
    outbox = []
    ReportMailer(lambda to, subject, body: outbox.append((to, subject))).mail("boss@example.com", report, text)
    print(outbox)
```

**When to use.**
- A class's description needs the word *"and"* ("formats **and** saves **and** emails").
- One file imports unrelated libraries (`smtplib`, `json`, `sqlite3`) for different jobs.
- Testing one behaviour forces you to set up a database, a network or a disk.

**Watch out.**
- "Single responsibility" doesn't mean "one method per class". It means one **reason to change**, which usually comes from one group of people (accounting, design, ops).
- Don't over-split. A 30-line script doesn't need five classes. Split when two kinds of change start to collide.
- The principle works for functions and modules too: a function that parses **and** validates **and** saves is the same smell.

```test
r = Report("Q1", [("a", 1), ("b", 2)])
assert ReportFormatter().render(r) == "Q1\n- a: 1\n- b: 2\nTotal: 3"
assert ReportFormatter().render(Report("Empty")) == "Empty\nTotal: 0"
import tempfile, pathlib
with tempfile.TemporaryDirectory() as d:
    p = ReportSaver(d).save("q1", "hello")
    assert p == pathlib.Path(d) / "q1.txt" and p.read_text() == "hello"
sent = []
ReportMailer(lambda *a: sent.append(a)).mail("x@y.z", r, "body")
assert sent == [("x@y.z", "Q1", "body")]
```

```stdout
Sales
- apples: 3
- pears: 5
Total: 8
[('boss@example.com', 'Sales')]
```

### Open/Closed Principle

**Problem.** An `area()` function switches on the shape kind. Every new shape means editing this function, and every other function written the same way (`perimeter`, `draw`, `to_json`…).

```py
def area(shape):
    if shape["kind"] == "circle":
        return math.pi * shape["r"] ** 2
    elif shape["kind"] == "rect":
        return shape["w"] * shape["h"]
    # a triangle? edit this function, and every function like it
```

**Task.** Redesign it so `total_area(shapes)` never has to change when a new shape type is added. `total_area([Circle(1), Rectangle(2, 3)])` must return `π + 6`.

**Idea.** *"Software entities should be open for extension, but closed for modification"* (Bertrand Meyer). Put the part that varies behind an **abstraction**: every shape knows its own `area()`. The code that uses shapes depends only on that abstraction, so adding a shape is **new code** (a new class), not **changed code**.

**Steps.**
1. Define an abstract base class `Shape` with an abstract `area()` method.
2. Each concrete shape (`Circle`, `Rectangle`, …) subclasses `Shape` and implements `area()`.
3. `total_area` just calls `shape.area()`. It never checks the type.
4. To add a shape, write a new subclass. Nothing that already exists is edited.

```python
import math
from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...


class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius ** 2


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width, self.height = width, height

    def area(self) -> float:
        return self.width * self.height


def total_area(shapes: list[Shape]) -> float:
    # closed for modification: never edited when a new shape arrives
    return sum(shape.area() for shape in shapes)


# open for extension: a new shape is a new class, nothing else changes
class Triangle(Shape):
    def __init__(self, base: float, height: float):
        self.base, self.height = base, height

    def area(self) -> float:
        return self.base * self.height / 2


if __name__ == "__main__":
    print(round(total_area([Circle(1), Rectangle(2, 3), Triangle(4, 5)]), 2))
```

**When to use.**
- The same `if/elif` on a "kind" or "type" shows up in several places.
- You keep editing a stable, tested module just to support one more variant.

**Watch out.**
- `ABC` + `@abstractmethod` makes Python refuse to instantiate `Shape()` or a subclass that forgot `area()` (`TypeError`), so mistakes show up early.
- Don't build extension points for changes that may never come. Apply OCP when the second or third variant appears.
- No design is closed against **every** change. Choose which axis of change (new shapes? new operations?) you protect. For new **operations** on fixed types, see the Visitor pattern.
- Pythonic alternative: `functools.singledispatch` lets you add new types to a function from outside:

```py
from functools import singledispatch

@singledispatch
def area(shape) -> float:
    raise TypeError(f"no area for {type(shape).__name__}")

@area.register
def _(shape: Circle) -> float:
    return math.pi * shape.radius ** 2
```

```test
assert abs(total_area([Circle(1), Rectangle(2, 3)]) - (math.pi + 6)) < 1e-9
assert total_area([]) == 0
class Hexagon(Shape):
    def __init__(self, side): self.side = side
    def area(self): return 3 * math.sqrt(3) / 2 * self.side ** 2
assert abs(total_area([Hexagon(2), Triangle(2, 2)]) - (6 * math.sqrt(3) + 2)) < 1e-9
try:
    Shape()
    assert False
except TypeError:
    pass
class Broken(Shape):
    pass
try:
    Broken()
    assert False
except TypeError:
    pass
```

```stdout
19.14
```

### Liskov Substitution Principle

**Problem.** `Square` inherits from a mutable `Rectangle` and overrides the setters to keep its sides equal. Code written for rectangles breaks when it gets a square.

```py
class Rectangle:
    def __init__(self, w, h): self.width, self.height = w, h
    def set_width(self, w): self.width = w
    def set_height(self, h): self.height = h
    def area(self): return self.width * self.height

class Square(Rectangle):
    def set_width(self, w): self.width = self.height = w
    def set_height(self, h): self.width = self.height = h

def stretch(rect):
    rect.set_width(5)
    rect.set_height(4)
    assert rect.area() == 20      # fails for Square: 16
```

**Task.** Redesign the hierarchy so any subtype can be used wherever its parent is expected, without surprises.

**Idea.** *"Objects of a subtype must be usable through the parent type without breaking the program"* (Barbara Liskov). A subclass must keep **every promise** of its parent. A mutable `Rectangle` promises that width and height change independently. A `Square` can't keep that promise, so it is not a *behavioural* subtype, even though "a square is a rectangle" in geometry. Fix: make both **siblings** under `Shape`, whose only promise is `area()`, and make them **immutable**, so the broken promise disappears.

**Steps.**
1. Create an abstract `Shape` with `area()`. That is the only contract clients rely on.
2. Make `Rectangle` and `Square` separate frozen dataclasses that both implement `Shape`.
3. To "resize", create a new object (`dataclasses.replace`). There are no setters that a subclass could break.
4. Client code (`total_area`) works for every `Shape` without `isinstance` checks.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, replace


class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...


@dataclass(frozen=True)
class Rectangle(Shape):
    width: float
    height: float

    def area(self) -> float:
        return self.width * self.height


@dataclass(frozen=True)
class Square(Shape):
    side: float

    def area(self) -> float:
        return self.side ** 2


def total_area(shapes: list[Shape]) -> float:
    return sum(s.area() for s in shapes)  # every Shape works, no isinstance checks


if __name__ == "__main__":
    rect = replace(Rectangle(2, 3), width=5, height=4)
    print(rect.area())
    print(Square(4).area())
    print(total_area([rect, Square(4)]))
```

**When to use.** Every time you write a subclass. Ask: *"Can the subclass do everything the parent promises, with the same inputs, giving results the caller will accept?"*

**Watch out.**
- Red flags: a subclass method that raises `NotImplementedError`, does nothing, accepts **fewer** inputs than the parent, or client code that has to check `isinstance` before calling a method.
- The rules: a subclass may not **strengthen** preconditions (demand more), **weaken** postconditions (promise less), break the parent's invariants, or raise new kinds of exceptions.
- Classic second example: `Bird.fly()` with a `Penguin` subclass. Fix it the same way: split the abstraction (`Bird`, `FlyingBird`) instead of overriding `fly()` to throw.
- "Is-a" in the real world isn't enough. Inheritance is about **behaviour**. When in doubt, prefer composition.

```test
from dataclasses import FrozenInstanceError
assert Rectangle(5, 4).area() == 20 and Square(4).area() == 16
assert not isinstance(Square(2), Rectangle) and isinstance(Square(2), Shape)
try:
    Square(2).side = 3
    assert False
except FrozenInstanceError:
    pass
assert all(s.area() >= 0 for s in [Rectangle(0, 3), Square(0), Rectangle(2, 2)])
assert total_area([Rectangle(1, 2), Square(3)]) == 11
assert replace(Square(2), side=5) == Square(5)
```

```stdout
20
16
36
```

### Interface Segregation Principle

**Problem.** One big `Machine` interface forces every device to implement printing, scanning and faxing. A basic printer has to "implement" fax by throwing, and code that only prints still depends on the fax methods.

```py
class Machine(ABC):
    @abstractmethod
    def print_document(self, doc): ...
    @abstractmethod
    def scan_document(self, doc): ...
    @abstractmethod
    def send_fax(self, doc, number): ...

class BasicPrinter(Machine):
    def print_document(self, doc): return f"printed {doc}"
    def scan_document(self, doc): raise NotImplementedError     # forced to lie
    def send_fax(self, doc, number): raise NotImplementedError
```

**Task.** Split the interface so classes implement only what they support, and each client depends only on the methods it actually uses.

**Idea.** *"Clients should not be forced to depend on methods they do not use."* Replace one fat interface with small **role interfaces** (`Printer`, `Scanner`, `FaxMachine`). A class implements the roles it really has. A function asks only for the role it needs. In Python, `typing.Protocol` describes a role by its methods. Classes don't even have to inherit from it (structural typing).

**Steps.**
1. Define one `Protocol` per role, each with only the methods of that role.
2. `BasicPrinter` implements just `print_document`. `OfficeMachine` implements all three roles.
3. Type each client function with the smallest role it needs: `print_all(printer: Printer, …)`, `archive(scanner: Scanner, …)`.
4. Use `@runtime_checkable` if you want `isinstance(obj, Scanner)` checks.

```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class Printer(Protocol):
    def print_document(self, doc: str) -> str: ...


@runtime_checkable
class Scanner(Protocol):
    def scan_document(self, doc: str) -> str: ...


@runtime_checkable
class FaxMachine(Protocol):
    def send_fax(self, doc: str, number: str) -> str: ...


class BasicPrinter:
    def print_document(self, doc: str) -> str:
        return f"printed {doc}"


class OfficeMachine:
    def print_document(self, doc: str) -> str:
        return f"printed {doc}"

    def scan_document(self, doc: str) -> str:
        return f"scanned {doc}"

    def send_fax(self, doc: str, number: str) -> str:
        return f"faxed {doc} to {number}"


# each client asks only for the role it needs
def print_all(printer: Printer, docs: list[str]) -> list[str]:
    return [printer.print_document(d) for d in docs]


def archive(scanner: Scanner, docs: list[str]) -> list[str]:
    return [scanner.scan_document(d) for d in docs]


if __name__ == "__main__":
    print(print_all(BasicPrinter(), ["a.pdf"]))
    print(archive(OfficeMachine(), ["b.pdf"]))
    print(isinstance(BasicPrinter(), Scanner))
```

**When to use.**
- Implementations are full of `raise NotImplementedError` or empty `pass` methods.
- Changing a method that one client uses forces unrelated clients to be retested or redeployed.

**Watch out.**
- Split by **what clients need**, not mechanically into one-method interfaces.
- `runtime_checkable` only checks that the method **names** exist, not their signatures. A type checker (mypy, Pyright) checks the signatures.
- `Protocol` = structural ("has these methods"). `ABC` = nominal ("inherits from this class"). Use an `ABC` when you also want to share code or force subclasses to implement methods.
- ISP and LSP go together: a class forced to implement a method it can't support usually breaks LSP too.

```test
assert isinstance(BasicPrinter(), Printer) and not isinstance(BasicPrinter(), Scanner)
m = OfficeMachine()
assert isinstance(m, Printer) and isinstance(m, Scanner) and isinstance(m, FaxMachine)
assert print_all(m, ["x", "y"]) == ["printed x", "printed y"]
assert archive(m, []) == []
assert m.send_fax("x", "123") == "faxed x to 123"
```

```stdout
['printed a.pdf']
['scanned b.pdf']
False
```

### Dependency Inversion Principle

**Problem.** `OrderService` creates its own MySQL connection. You can't test the business rules without a running database, and switching to another database means editing the service.

```py
class OrderService:
    def __init__(self):
        self.db = MySQLDatabase("prod-host", "user", "pw")   # concrete, hard-wired

    def place(self, order_id, customer, total):
        self.db.execute("INSERT INTO orders ...")
```

**Task.** Make `OrderService` work with **any** storage: an in-memory one for tests, SQLite, or a fake, without changing its code.

**Idea.** *"High-level modules should not depend on low-level modules. Both should depend on abstractions."* The business logic (`OrderService`) defines the interface it needs (`OrderRepository`: `add`, `get`). The storage classes implement that interface. The concrete repository is **passed in** from outside (dependency injection), so the dependency arrow now points from the details to the abstraction.

**Steps.**
1. Define `OrderRepository` as a `Protocol` with `add(order)` and `get(order_id)`.
2. Give `OrderService` a repository through its constructor, and keep only business rules in it (positive total, no duplicate id).
3. Write `InMemoryOrderRepository` (a dict) and `SqliteOrderRepository` (with parameterized SQL).
4. The caller (the "composition root": `main`, a test, a web app factory) chooses which one to use.

```python
import sqlite3
from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass(frozen=True)
class Order:
    id: int
    customer: str
    total: float


class OrderRepository(Protocol):
    def add(self, order: Order) -> None: ...
    def get(self, order_id: int) -> Optional[Order]: ...


class OrderService:
    # high-level policy: knows the abstraction, not the database
    def __init__(self, repo: OrderRepository):
        self.repo = repo

    def place(self, order_id: int, customer: str, total: float) -> Order:
        if total <= 0:
            raise ValueError("total must be positive")
        if self.repo.get(order_id) is not None:
            raise ValueError(f"order {order_id} already exists")
        order = Order(order_id, customer, total)
        self.repo.add(order)
        return order


class InMemoryOrderRepository:
    def __init__(self):
        self._orders: dict[int, Order] = {}

    def add(self, order: Order) -> None:
        self._orders[order.id] = order

    def get(self, order_id: int) -> Optional[Order]:
        return self._orders.get(order_id)


class SqliteOrderRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        conn.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, customer TEXT, total REAL)")

    def add(self, order: Order) -> None:
        self.conn.execute("INSERT INTO orders VALUES (?, ?, ?)", (order.id, order.customer, order.total))

    def get(self, order_id: int) -> Optional[Order]:
        row = self.conn.execute("SELECT id, customer, total FROM orders WHERE id = ?", (order_id,)).fetchone()
        return Order(*row) if row else None


if __name__ == "__main__":
    service = OrderService(InMemoryOrderRepository())
    service.place(1, "Ada", 25.0)
    print(service.repo.get(1))
    service = OrderService(SqliteOrderRepository(sqlite3.connect(":memory:")))
    service.place(2, "Linus", 40.5)
    print(service.repo.get(2))
```

**When to use.**
- Business logic creates its own database clients, HTTP clients, clocks or file handles.
- Tests need real infrastructure, or are slow and flaky because of it.

**Watch out.**
- Dependency **inversion** is the principle. Dependency **injection** (passing objects in) is the usual technique to achieve it. You don't need a DI framework: a constructor argument is enough.
- The abstraction belongs to the **high-level** side. Design `OrderRepository` around what the service needs, not around what MySQL offers.
- Always use parameterized queries (`?` placeholders), never f-strings, when building SQL: it prevents SQL injection.
- Injecting small things like a clock (`now=datetime.now`) or a random generator makes time- and random-dependent code testable too.

```test
for repo in (InMemoryOrderRepository(), SqliteOrderRepository(sqlite3.connect(":memory:"))):
    s = OrderService(repo)
    o = s.place(7, "Grace", 10.0)
    assert repo.get(7) == o == Order(7, "Grace", 10.0)
    assert repo.get(8) is None
    for bad in [(7, "X", 1.0), (9, "X", 0)]:
        try:
            s.place(*bad)
            assert False
        except ValueError:
            pass
class FakeRepo:
    def __init__(self): self.added = []
    def add(self, order): self.added.append(order)
    def get(self, order_id): return None
f = FakeRepo()
OrderService(f).place(1, "A", 2.0)
assert f.added == [Order(1, "A", 2.0)]
```

```stdout
Order(id=1, customer='Ada', total=25.0)
Order(id=2, customer='Linus', total=40.5)
```
