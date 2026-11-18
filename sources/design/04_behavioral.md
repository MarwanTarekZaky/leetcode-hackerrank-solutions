## Behavioral Patterns

### Chain of Responsibility

**Problem.** Purchase approvals are one `if/elif` ladder. A new role, a different order, or an extra check on the way (fraud, budget) means editing this function every time.

```py
def approve(amount):
    if amount <= 1_000:
        return "TeamLead approved"
    elif amount <= 10_000:
        return "Manager approved"
    elif amount <= 100_000:
        return "Director approved"
    return "rejected"
```

**Task.** Pass the request along a **chain of handlers**. Each one approves it if it can, or forwards it to the next. Chains must be built and reordered at runtime, and a new check must be one new class.

**Idea.** Chain of Responsibility links handler objects. Each handler holds a reference to its **successor**. A request enters at the first handler. Each handler decides to **handle it** (and stop) or **pass it on**. The sender doesn't know which handler will answer, and handlers don't know the whole chain.

**Steps.**
1. Base class `Approver` with a `successor` and a `limit`.
2. `approve(amount)`: if `can_approve(amount)`, answer. Else, if there's a successor, return `successor.approve(amount)`. Else reject.
3. Concrete approvers just set their `limit`. Special handlers override `approve` or `can_approve`.
4. Build the chain by nesting: `TeamLead(Manager(Director()))`.

```python
from typing import Optional


class Approver:
    limit = 0

    def __init__(self, successor: Optional["Approver"] = None):
        self.successor = successor

    def can_approve(self, amount: float) -> bool:
        return amount <= self.limit

    def approve(self, amount: float) -> str:
        if self.can_approve(amount):
            return f"{type(self).__name__} approved {amount}"
        if self.successor is not None:
            return self.successor.approve(amount)
        return f"rejected {amount}: over every limit"


class TeamLead(Approver):
    limit = 1_000


class Manager(Approver):
    limit = 10_000


class Director(Approver):
    limit = 100_000


if __name__ == "__main__":
    chain = TeamLead(Manager(Director()))
    for amount in (500, 7_500, 50_000, 250_000):
        print(chain.approve(amount))
```

**When to use.**
- Several objects may handle a request, and which one should is decided at runtime.
- You need a pipeline of checks that can stop early: web middleware, logging levels, event bubbling in UIs, validation steps, support-ticket escalation.

**Watch out.**
- A request can reach the end **unhandled**. Always define what happens then (here: a rejection message).
- Long chains are hard to debug. Log which handler answered.
- Variant: in **middleware** chains, every handler does its part and then calls the next one (like Django/ASGI middleware), instead of "first one that can, wins".
- A list of handlers plus a loop (`for h in handlers: if h.can(x): return h.do(x)`) is a simpler Python alternative when handlers don't need to control forwarding.

```test
chain = TeamLead(Manager(Director()))
assert chain.approve(1000) == "TeamLead approved 1000"
assert chain.approve(1001) == "Manager approved 1001"
assert chain.approve(10**6) == "rejected 1000000: over every limit"
class Cfo(Approver):
    limit = 1_000_000
assert TeamLead(Manager(Director(Cfo()))).approve(10**6) == "Cfo approved 1000000"
class FlagRoundNumbers(Approver):
    def approve(self, amount):
        if amount >= 1000 and amount % 1000 == 0:
            return f"flagged {amount}"
        return super().approve(amount)
guarded = FlagRoundNumbers(TeamLead(Manager()))
assert guarded.approve(5000) == "flagged 5000" and guarded.approve(5001) == "Manager approved 5001"
assert Manager(TeamLead()).approve(500) == "Manager approved 500"
```

```stdout
TeamLead approved 500
Manager approved 7500
Director approved 50000
rejected 250000: over every limit
```

### Command

**Problem.** An editor changes its text directly in methods. There is no way to undo, redo, log or replay what happened, because the actions aren't objects you can keep.

```py
class Editor:
    def append(self, text):
        self.text += text
    def delete_last(self, n):
        self.text = self.text[:-n]      # bug: n = 0 deletes everything ("abc"[:-0] == "")
    # undo? redo? a macro that replays steps? each needs special code
```

**Task.** Turn every action into an object with `execute()` and `undo()`, and build an editor with **undo** and **redo**.

**Idea.** Command turns a request into an **object** that holds everything needed to perform it (the receiver and the arguments). The **invoker** (`Editor`) runs commands and keeps them in a history without knowing what they do. Undo pops the last command and calls its `undo()`. Redo runs it again.

**Steps.**
1. `Command` interface: `execute()` and `undo()`.
2. `Append(doc, text)`: execute adds the text. Undo cuts exactly `len(text)` characters from the end.
3. `DeleteLast(doc, count)`: execute **remembers what it removed**, so undo can put it back.
4. `Editor.run` executes, pushes onto the done-stack, and clears the redo-stack. `undo` / `redo` move commands between the two stacks.

```python
from abc import ABC, abstractmethod


class Document:
    def __init__(self):
        self.text = ""


class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...

    @abstractmethod
    def undo(self) -> None: ...


class Append(Command):
    def __init__(self, doc: Document, text: str):
        self.doc, self.text = doc, text

    def execute(self) -> None:
        self.doc.text += self.text

    def undo(self) -> None:
        self.doc.text = self.doc.text[:len(self.doc.text) - len(self.text)]


class DeleteLast(Command):
    def __init__(self, doc: Document, count: int):
        self.doc, self.count = doc, count
        self.removed = ""

    def execute(self) -> None:
        keep = max(len(self.doc.text) - self.count, 0)
        self.removed = self.doc.text[keep:]
        self.doc.text = self.doc.text[:keep]

    def undo(self) -> None:
        self.doc.text += self.removed


class Editor:
    # the invoker: runs and remembers commands, knows nothing about what they do
    def __init__(self):
        self._done: list[Command] = []
        self._undone: list[Command] = []

    def run(self, command: Command) -> None:
        command.execute()
        self._done.append(command)
        self._undone.clear()  # a new action makes the old redo history invalid

    def undo(self) -> bool:
        if not self._done:
            return False
        command = self._done.pop()
        command.undo()
        self._undone.append(command)
        return True

    def redo(self) -> bool:
        if not self._undone:
            return False
        command = self._undone.pop()
        command.execute()
        self._done.append(command)
        return True


if __name__ == "__main__":
    doc, editor = Document(), Editor()
    editor.run(Append(doc, "Hello"))
    editor.run(Append(doc, " world"))
    editor.run(DeleteLast(doc, 6))
    print(repr(doc.text))
    editor.undo()
    print(repr(doc.text))
    editor.undo()
    print(repr(doc.text))
    editor.redo()
    print(repr(doc.text))
```

**When to use.**
- Undo/redo, macros, transaction logs.
- Queuing or scheduling work (job queues, task runners): a command can be stored and run later, maybe on another thread or machine.
- Decoupling UI elements (buttons, menu items, shortcuts) from the actions they trigger.

**Watch out.**
- `undo()` must restore the **exact** previous state. Store what you need during `execute()` (like `removed`), because you can't recompute it afterwards.
- Watch out for slicing traps: `s[:-0]` is `""`, not `s`. That's why the code uses `s[:len(s) - n]`.
- Running a new command must **clear the redo stack**. Otherwise redo would replay actions on a state they were never meant for.
- In Python, a command without undo can just be a function or `functools.partial(fn, *args)`. Use classes when you need `undo`, a description, or serialization.

```test
doc, ed = Document(), Editor()
assert not ed.undo() and not ed.redo()
ed.run(Append(doc, "abc"))
ed.run(Append(doc, ""))
ed.undo()
assert doc.text == "abc"
ed.run(DeleteLast(doc, 10))
assert doc.text == ""
ed.undo()
assert doc.text == "abc"
ed.run(DeleteLast(doc, 0))
assert doc.text == "abc"
ed.undo()
ed.undo()
assert doc.text == ""
assert ed.redo() and doc.text == "abc"
ed.run(Append(doc, "!"))
assert not ed.redo() and doc.text == "abc!"
```

```stdout
'Hello'
'Hello world'
'Hello'
'Hello world'
```

### Interpreter

**Problem.** Business users want pricing rules like `price * qty + shipping` stored in the database and evaluated per order. The quick solution, `eval()`, runs **any** Python code a user types.

```py
total = eval(rule, {}, order)    # never do this with user input: rule could delete files
```

**Task.** Define a tiny, safe language for arithmetic rules. Parse rules written in Reverse Polish Notation (`"price qty * shipping +"`) into a tree, then evaluate the tree with a dict of variables.

**Idea.** Interpreter represents each **grammar rule as a class**: `Number` and `Variable` are terminals, and `Add`, `Subtract`, `Multiply` are non-terminals that hold sub-expressions. A sentence becomes an **abstract syntax tree** (a Composite), and `interpret(context)` evaluates it recursively. Only operations you defined can run, so it's safe.

**Steps.**
1. `Expression` with `interpret(context)`.
2. `Number` returns its value. `Variable` looks up its name in the context (clear error if missing).
3. `BinaryOp` interprets both sides and combines them with `apply`. Subclasses only set the symbol and `apply`.
4. `parse_rpn` reads tokens left to right with a stack: numbers and names are pushed; an operator pops two operands and pushes the new node. At the end exactly one expression must remain.

```python
from abc import ABC, abstractmethod


class Expression(ABC):
    @abstractmethod
    def interpret(self, context: dict[str, int]) -> int: ...


class Number(Expression):
    def __init__(self, value: int):
        self.value = value

    def interpret(self, context: dict[str, int]) -> int:
        return self.value

    def __str__(self) -> str:
        return str(self.value)


class Variable(Expression):
    def __init__(self, name: str):
        self.name = name

    def interpret(self, context: dict[str, int]) -> int:
        if self.name not in context:
            raise NameError(f"variable {self.name!r} is not defined")
        return context[self.name]

    def __str__(self) -> str:
        return self.name


class BinaryOp(Expression):
    symbol = "?"

    def __init__(self, left: Expression, right: Expression):
        self.left, self.right = left, right

    def interpret(self, context: dict[str, int]) -> int:
        return self.apply(self.left.interpret(context), self.right.interpret(context))

    @abstractmethod
    def apply(self, a: int, b: int) -> int: ...

    def __str__(self) -> str:
        return f"({self.left} {self.symbol} {self.right})"


class Add(BinaryOp):
    symbol = "+"

    def apply(self, a: int, b: int) -> int:
        return a + b


class Subtract(BinaryOp):
    symbol = "-"

    def apply(self, a: int, b: int) -> int:
        return a - b


class Multiply(BinaryOp):
    symbol = "*"

    def apply(self, a: int, b: int) -> int:
        return a * b


OPERATORS = {cls.symbol: cls for cls in (Add, Subtract, Multiply)}


def parse_rpn(source: str) -> Expression:
    stack: list[Expression] = []
    for token in source.split():
        if token in OPERATORS:
            if len(stack) < 2:
                raise ValueError(f"not enough operands for {token!r}")
            right, left = stack.pop(), stack.pop()
            stack.append(OPERATORS[token](left, right))
        elif token.lstrip("-").isdigit():
            stack.append(Number(int(token)))
        elif token.isidentifier():
            stack.append(Variable(token))
        else:
            raise ValueError(f"bad token {token!r}")
    if len(stack) != 1:
        raise ValueError("expression must reduce to exactly one value")
    return stack[0]


if __name__ == "__main__":
    expr = parse_rpn("price qty * shipping +")
    print(expr)
    print(expr.interpret({"price": 12, "qty": 3, "shipping": 5}))
    print(parse_rpn("10 4 - 2 *").interpret({}))
```

**When to use.**
- You have a **small, stable grammar** that users or configs write in: rules, filters, search queries, simple formulas, feature flags.
- You want a safe alternative to `eval()`.

**Watch out.**
- **Never `eval()` user input.** Even with `{"__builtins__": {}}` there are known escapes. A small interpreter (or `ast.literal_eval` for plain literals) is the safe route.
- Order on the stack: the **first** pop is the **right** operand. Getting it backwards breaks `-` (and `/`).
- One class per rule is fine for small grammars. For big languages use a parser generator (Lark, ANTLR) or Python's `ast` module.
- The tree is a Composite, and new operations over it (pretty-printing, simplifying) fit the Visitor pattern.

```test
ctx = {"a": 2, "b": 5}
assert parse_rpn("a b +").interpret(ctx) == 7
assert parse_rpn("a b -").interpret(ctx) == -3
assert parse_rpn("3 -4 *").interpret({}) == -12
assert str(parse_rpn("a b c * +")) == "(a + (b * c))"
for bad in ["+", "1 2", "1 $ +", ""]:
    try:
        parse_rpn(bad)
        assert False, bad
    except ValueError:
        pass
try:
    parse_rpn("x 1 +").interpret({})
    assert False
except NameError:
    pass
class Power(BinaryOp):
    symbol = "^"
    def apply(self, a, b): return a ** b
OPERATORS["^"] = Power
assert parse_rpn("2 10 ^ 1 -").interpret({}) == 1023
```

```stdout
((price * qty) + shipping)
41
12
```

### Iterator

**Problem.** To loop over a binary search tree in sorted order, every caller reaches into the tree's nodes and writes its own recursive walk, which also builds the whole list in memory first.

```py
def walk(node, out):
    if node:
        walk(node.left, out)
        out.append(node.value)
        walk(node.right, out)

values = []
walk(tree.root, values)     # callers depend on the tree's internals
```

**Task.** Make the tree work with a normal `for` loop (`for v in tree`, `list(tree)`, `x in tree`) in sorted order, **lazily**, without exposing its nodes. Several loops over the same tree must not interfere.

**Idea.** Iterator moves the traversal into a separate object that remembers **where it is**. Python builds this pattern into the language: a collection's `__iter__` returns an iterator, and the iterator's `__next__` returns the next item or raises `StopIteration`. An in-order iterator keeps a stack of the nodes still to visit, so it uses O(height) memory instead of O(n).

**Steps.**
1. `InorderIterator` starts by pushing the root and all its left descendants on a stack.
2. `__next__`: pop a node (the smallest not yet returned), push the left spine of its right child, return the node's value.
3. `BST.__iter__` returns a **new** iterator each time, so loops are independent.
4. A **generator** (`preorder`, using `yield`) is the shortcut: Python writes `__iter__` and `__next__` for you.

```python
from typing import Optional


class _Node:
    def __init__(self, value):
        self.value = value
        self.left: Optional["_Node"] = None
        self.right: Optional["_Node"] = None


class InorderIterator:
    def __init__(self, root: Optional[_Node]):
        self._stack: list[_Node] = []
        self._push_left(root)

    def _push_left(self, node: Optional[_Node]) -> None:
        while node is not None:
            self._stack.append(node)
            node = node.left

    def __iter__(self):
        return self

    def __next__(self):
        if not self._stack:
            raise StopIteration
        node = self._stack.pop()
        self._push_left(node.right)
        return node.value


class BST:
    def __init__(self, values=()):
        self.root: Optional[_Node] = None
        for v in values:
            self.insert(v)

    def insert(self, value) -> None:
        if self.root is None:
            self.root = _Node(value)
            return
        node = self.root
        while True:
            side = "left" if value < node.value else "right"
            child = getattr(node, side)
            if child is None:
                setattr(node, side, _Node(value))
                return
            node = child

    def __iter__(self):
        return InorderIterator(self.root)  # a fresh iterator for every loop

    def preorder(self):
        # the same pattern as a generator: Python writes __next__ for you
        stack = [self.root] if self.root else []
        while stack:
            node = stack.pop()
            yield node.value
            if node.right:
                stack.append(node.right)
            if node.left:
                stack.append(node.left)


if __name__ == "__main__":
    tree = BST([5, 3, 8, 1, 4, 9])
    print(list(tree))
    print(list(tree.preorder()))
    it = iter(tree)
    print(next(it), next(it), 4 in tree)
```

**When to use.**
- A collection has a complex internal structure (tree, graph, paginated API, file in chunks) and clients should just loop over it.
- You need several traversal orders, or lazy (on-demand) traversal of huge or infinite data.

**Watch out.**
- **Iterable vs iterator**: an iterable (`BST`) returns a **new** iterator from `__iter__`. An iterator returns **itself** and is used up after one pass. If `BST.__iter__` returned `self`, a second loop would see nothing.
- Changing a collection while iterating over it gives wrong results (Python raises `RuntimeError` for dicts and sets, but not for your own classes).
- Prefer generators (`yield`) for most custom iteration. Write a class only when the iterator needs extra methods or state that clients use.
- `itertools` (`islice`, `chain`, `takewhile`…) works with any iterator you write.

```test
import random
assert list(BST()) == [] and list(BST().preorder()) == []
vals = random.Random(1).sample(range(1000), 200)
t = BST(vals)
assert list(t) == sorted(vals)
a, b = iter(t), iter(t)
assert next(a) == next(b) == min(vals)
it = iter(BST([2, 1]))
assert list(it) == [1, 2] and list(it) == []
assert 999 not in BST([1, 2, 3]) and 2 in BST([1, 2, 3])
```

```stdout
[1, 3, 4, 5, 8, 9]
[5, 3, 1, 4, 8, 9]
1 3 True
```

### Mediator

**Problem.** In a chat app, every user object holds references to every other user and delivers messages itself. With n users there are n × (n − 1) links, and features like direct messages or "user joined" notices mean changing `User`.

```py
class User:
    def __init__(self, name):
        self.name, self.friends = name, []   # every user knows every other user
    def send(self, text):
        for f in self.friends:
            f.inbox.append(f"{self.name}: {text}")
```

**Task.** Let users talk **only through a chat room**. Users never reference each other. The room handles broadcasts, direct messages, join notices and errors.

**Idea.** A Mediator **centralizes communication** between objects. Colleagues (`User`) only know the mediator (`ChatRoom`). They tell it what happened, and it decides who should receive what. Many-to-many links become one-to-many, and the interaction rules live in one place.

**Steps.**
1. `ChatRoom.join(user)` registers the user, gives it a link to the room, and announces it to the others.
2. `User.send(text, to=None)` just forwards to `room.send(...)`. Without a room it raises `RuntimeError`.
3. `ChatRoom.send` broadcasts to everyone except the sender, or delivers to one user for a direct message (unknown name → `ValueError`).
4. `User.receive` appends to the user's inbox.

```python
from typing import Optional


class ChatRoom:
    def __init__(self):
        self._members: dict[str, "User"] = {}

    def join(self, user: "User") -> None:
        self._members[user.name] = user
        user.room = self
        self._broadcast("room", f"{user.name} joined", skip=user.name)

    def send(self, sender: str, text: str, to: Optional[str] = None) -> None:
        if to is None:
            self._broadcast(sender, text, skip=sender)
        elif to in self._members:
            self._members[to].receive(sender, text)
        else:
            raise ValueError(f"no user {to!r} in the room")

    def _broadcast(self, sender: str, text: str, skip: str) -> None:
        for name, member in self._members.items():
            if name != skip:
                member.receive(sender, text)


class User:
    def __init__(self, name: str):
        self.name = name
        self.room: Optional[ChatRoom] = None
        self.inbox: list[str] = []

    def send(self, text: str, to: Optional[str] = None) -> None:
        if self.room is None:
            raise RuntimeError(f"{self.name} is not in a room")
        self.room.send(self.name, text, to)

    def receive(self, sender: str, text: str) -> None:
        self.inbox.append(f"{sender}: {text}")


if __name__ == "__main__":
    room = ChatRoom()
    ada, bob, cy = User("ada"), User("bob"), User("cy")
    for user in (ada, bob, cy):
        room.join(user)
    ada.send("hi all")
    bob.send("psst", to="cy")
    print(ada.inbox)
    print(bob.inbox)
    print(cy.inbox)
```

**When to use.**
- Many objects interact in complex ways and the web of references is hard to follow (form fields that enable/disable each other, chat rooms, air-traffic control, game lobbies).
- You want to reuse components that are otherwise tied to each other.

**Watch out.**
- The mediator can grow into a **god object** that knows everything. Keep it about coordination, and split it if it collects unrelated rules.
- Mediator vs Observer: an observer subject just broadcasts to whoever subscribed. A mediator **decides** who gets what, often using observer-style notifications inside.
- Mediator vs Facade: a facade simplifies access **into** a subsystem, and the subsystem doesn't know it. Colleagues **know** their mediator and talk through it.

```test
room = ChatRoom()
a, b = User("a"), User("b")
room.join(a)
room.join(b)
a.send("x")
b.send("y", to="a")
assert a.inbox == ["room: b joined", "b: y"] and b.inbox == ["a: x"]
try:
    a.send("z", to="nobody")
    assert False
except ValueError:
    pass
try:
    User("lonely").send("hello?")
    assert False
except RuntimeError:
    pass
assert not hasattr(a, "friends")
```

```stdout
['room: bob joined', 'room: cy joined']
['room: cy joined', 'ada: hi all']
['ada: hi all', 'bob: psst']
```

### Memento

**Problem.** To support undo, outside code copies the editor's private fields and later writes them back. Every new field in the editor silently breaks all those places, and encapsulation is gone.

```py
backup = (editor._text, editor._cursor, editor._selection)
...
editor._text, editor._cursor, editor._selection = backup
```

**Task.** Let the editor **save and restore its own state** as opaque snapshots, and let a separate history object keep those snapshots (with a size limit) without looking inside them.

**Idea.** Memento has three roles. The **originator** (`Editor`) creates a snapshot of its state and can restore from one. The **memento** (`Snapshot`) is an immutable copy of that state. The **caretaker** (`History`) stores mementos and hands them back for undo, but never reads or changes them. Only the editor knows what's inside, so the editor can change freely.

**Steps.**
1. `Snapshot` is a frozen dataclass with the editor's state (`text`, `cursor`).
2. `Editor.save()` returns a `Snapshot`. `Editor.restore(snapshot)` copies the values back.
3. `History.checkpoint()` asks the editor for a snapshot and pushes it, dropping the oldest when over the limit.
4. `History.undo()` pops the last snapshot and asks the editor to restore it.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Snapshot:
    # the memento: an immutable copy of the editor's state
    text: str
    cursor: int


class Editor:
    # the originator: the only class that creates or reads snapshots
    def __init__(self):
        self.text = ""
        self.cursor = 0

    def write(self, chars: str) -> None:
        self.text = self.text[:self.cursor] + chars + self.text[self.cursor:]
        self.cursor += len(chars)

    def move(self, position: int) -> None:
        self.cursor = max(0, min(position, len(self.text)))

    def save(self) -> Snapshot:
        return Snapshot(self.text, self.cursor)

    def restore(self, snapshot: Snapshot) -> None:
        self.text, self.cursor = snapshot.text, snapshot.cursor


class History:
    # the caretaker: keeps snapshots but never looks inside them
    def __init__(self, editor: Editor, limit: int = 100):
        self.editor = editor
        self.limit = limit
        self._stack: list[Snapshot] = []

    def checkpoint(self) -> None:
        self._stack.append(self.editor.save())
        if len(self._stack) > self.limit:
            self._stack.pop(0)

    def undo(self) -> bool:
        if not self._stack:
            return False
        self.editor.restore(self._stack.pop())
        return True


if __name__ == "__main__":
    editor = Editor()
    history = History(editor)
    history.checkpoint()
    editor.write("Hello")
    history.checkpoint()
    editor.move(0)
    editor.write(">> ")
    print(editor.text, editor.cursor)
    history.undo()
    print(editor.text, editor.cursor)
    history.undo()
    print(repr(editor.text), editor.cursor)
```

**When to use.**
- Undo, checkpoints, "cancel" in dialogs, rolling back a failed multi-step operation, saving game state.
- You need to snapshot an object's state without exposing its internals.

**Watch out.**
- Memento vs Command for undo: Memento stores **whole states** (simple, uses more memory). Command stores **actions** and how to reverse them (less memory, but each undo must be written correctly). Large editors often combine both.
- Snapshots must not share mutable objects with the live state. If the state holds lists or dicts, `copy.deepcopy` them in `save()`.
- Limit the history (as `limit` does), or snapshots of large objects will eat memory. A `collections.deque(maxlen=...)` drops the oldest automatically.
- Python can't truly hide fields, so "opaque" is a convention: the caretaker just never touches the snapshot's attributes.

```test
from dataclasses import FrozenInstanceError
e = Editor()
h = History(e, limit=2)
for word in ("a", "b", "c"):
    h.checkpoint()
    e.write(word)
assert e.text == "abc"
assert h.undo() and e.text == "ab"
assert h.undo() and e.text == "a"
assert not h.undo() and e.text == "a"
e.move(99)
assert e.cursor == 1
e.move(-5)
assert e.cursor == 0
s = e.save()
try:
    s.text = "hack"
    assert False
except FrozenInstanceError:
    pass
```

```stdout
>> Hello 3
Hello 5
'' 0
```

### Observer

**Problem.** When a stock price changes, the `Stock` class itself calls the dashboard, the alerts and the audit log. It knows every consumer and must be edited for each new one.

```py
class Stock:
    def set_price(self, price):
        self.price = price
        dashboard.refresh(self)    # Stock knows every consumer...
        alerts.check(self)
        audit_log.write(self)      # ...and changes for each new one
```

**Task.** Let any number of listeners **subscribe** to price changes and **unsubscribe** later. `Stock` must notify them without knowing who they are, and only when the price really changes.

**Idea.** Observer defines a one-to-many dependency. The **subject** (`Stock`) keeps a list of **observers** and notifies all of them when its state changes. Observers register themselves. The subject only knows they are callables with a fixed signature. In Python an observer can be any callable: a function, a lambda, a bound method, or an object with `__call__`.

**Steps.**
1. `Stock` keeps `_listeners`. `subscribe(fn)` appends it and returns an **unsubscribe function**.
2. `price` is a property. Its setter does nothing if the value didn't change, otherwise stores it and calls every listener with `(symbol, old, new)`.
3. It loops over a **copy** of the list, so a listener may unsubscribe during the notification.
4. `PriceAlert` is a stateful observer: it records when the price crosses its threshold upward.

```python
from typing import Callable

Listener = Callable[[str, float, float], None]


class Stock:
    def __init__(self, symbol: str, price: float):
        self.symbol = symbol
        self._price = price
        self._listeners: list[Listener] = []

    def subscribe(self, listener: Listener) -> Callable[[], None]:
        self._listeners.append(listener)
        return lambda: self._listeners.remove(listener)  # call it to unsubscribe

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: float) -> None:
        if value == self._price:
            return
        old, self._price = self._price, value
        for listener in list(self._listeners):  # copy: a listener may unsubscribe while we loop
            listener(self.symbol, old, value)


class PriceAlert:
    def __init__(self, threshold: float):
        self.threshold = threshold
        self.alerts: list[str] = []

    def __call__(self, symbol: str, old: float, new: float) -> None:
        if old < self.threshold <= new:
            self.alerts.append(f"{symbol} crossed {self.threshold}: {new}")


if __name__ == "__main__":
    stock = Stock("ACME", 95.0)
    log = []
    stop_log = stock.subscribe(lambda s, old, new: log.append(f"{s} {old} -> {new}"))
    alert = PriceAlert(100)
    stock.subscribe(alert)
    for p in (98.0, 101.5, 101.5, 99.0):
        stock.price = p
    stop_log()
    stock.price = 105.0
    print(log)
    print(alert.alerts)
```

**When to use.**
- A change in one object must update others, and you don't know in advance how many or which ones (UI updates, event systems, model–view, webhooks, pub/sub).
- You want to add reactions without editing the object that changes.

**Watch out.**
- **Memory leaks**: the subject keeps observers alive. Always unsubscribe, or store observers in a `weakref.WeakSet` / use `weakref.WeakMethod` for bound methods.
- An observer that raises stops the loop and the remaining observers miss the event. Decide on a policy (catch and log, or let it fail loudly).
- Don't rely on notification order between observers.
- An observer that changes the subject inside its callback can cause infinite loops. The "only notify on real change" check helps.

```test
s = Stock("X", 1.0)
seen = []
def once(sym, old, new):
    seen.append(new)
    unsub()
unsub = s.subscribe(once)
other = []
s.subscribe(lambda *a: other.append(a))
s.price = 2.0
s.price = 3.0
s.price = 3.0
assert seen == [2.0] and other == [("X", 1.0, 2.0), ("X", 2.0, 3.0)]
a = PriceAlert(10)
s.subscribe(a)
for p in (9, 10, 11, 5, 12):
    s.price = p
assert a.alerts == ["X crossed 10: 10", "X crossed 10: 12"]
```

```stdout
['ACME 95.0 -> 98.0', 'ACME 98.0 -> 101.5', 'ACME 101.5 -> 99.0']
['ACME crossed 100: 101.5', 'ACME crossed 100: 105.0']
```

### State

**Problem.** An order's behaviour depends on its status, so every method has the same `if/elif` ladder on `self.status`. A new status means editing every method, and invalid transitions slip through.

```py
class Order:
    def cancel(self):
        if self.status == "pending":
            self.status = "cancelled"
        elif self.status == "paid":
            self.refund()
            self.status = "cancelled"
        elif self.status in ("shipped", "delivered"):
            raise ValueError("too late")
    def ship(self):
        if self.status == "paid": ...
        # the same ladder in every method
```

**Task.** Model the order lifecycle `pending → paid → shipped → delivered` (plus `cancelled` from pending or paid, with a refund when paid) so that each status is a class, and any invalid action raises `InvalidTransition`.

**Idea.** State puts each state's behaviour in **its own class**. The context (`Order`) holds a current state object and **delegates** every action to it. A state handles the actions that make sense for it, usually by switching `order.state` to the next state. All other actions fall back to the base class, which refuses them. The `if/elif` ladders disappear.

**Steps.**
1. `OrderState` base class: every action (`pay`, `ship`, `deliver`, `cancel`) raises `InvalidTransition` by default.
2. Each concrete state overrides only its valid actions: `Pending` (pay, cancel), `Paid` (ship, cancel with refund), `Shipped` (deliver). `Delivered` and `Cancelled` allow nothing.
3. `Order` starts in `Pending()` and forwards each method to `self.state`.
4. `status` returns the current state's name.

```python
class InvalidTransition(Exception):
    pass


class OrderState:
    name = "?"

    def pay(self, order: "Order") -> None:
        self._deny("pay")

    def ship(self, order: "Order") -> None:
        self._deny("ship")

    def deliver(self, order: "Order") -> None:
        self._deny("deliver")

    def cancel(self, order: "Order") -> None:
        self._deny("cancel")

    def _deny(self, action: str) -> None:
        raise InvalidTransition(f"cannot {action} an order that is {self.name}")


class Pending(OrderState):
    name = "pending"

    def pay(self, order):
        order.state = Paid()

    def cancel(self, order):
        order.state = Cancelled()


class Paid(OrderState):
    name = "paid"

    def ship(self, order):
        order.state = Shipped()

    def cancel(self, order):
        order.refunded = True
        order.state = Cancelled()


class Shipped(OrderState):
    name = "shipped"

    def deliver(self, order):
        order.state = Delivered()


class Delivered(OrderState):
    name = "delivered"


class Cancelled(OrderState):
    name = "cancelled"


class Order:
    def __init__(self):
        self.state: OrderState = Pending()
        self.refunded = False

    @property
    def status(self) -> str:
        return self.state.name

    def pay(self) -> None:
        self.state.pay(self)

    def ship(self) -> None:
        self.state.ship(self)

    def deliver(self) -> None:
        self.state.deliver(self)

    def cancel(self) -> None:
        self.state.cancel(self)


if __name__ == "__main__":
    order = Order()
    order.pay()
    order.ship()
    print(order.status)
    try:
        order.cancel()
    except InvalidTransition as e:
        print(e)
    order.deliver()
    print(order.status)
```

**When to use.**
- An object behaves very differently depending on its state, and the same state checks are repeated in many methods.
- You have a clear state machine: orders, documents (draft/review/published), connections, game characters, traffic lights, parsers.

**Watch out.**
- For a few states with simple rules, a **transition table** (`{("pending", "pay"): "paid", ...}`) can be clearer than one class per state. Use classes when states have real behaviour.
- State vs Strategy: they look the same (an object delegates to a swappable object). In State, the states **switch themselves** as the object changes. In Strategy, the **client** picks the strategy and it usually stays.
- States without data can be shared single instances instead of being created on every transition.
- Make side effects (the refund) part of the transition, so they can't be forgotten.

```test
o = Order()
assert o.status == "pending"
o.cancel()
assert o.status == "cancelled" and not o.refunded
for action in ("pay", "ship", "deliver", "cancel"):
    try:
        getattr(o, action)()
        assert False
    except InvalidTransition as e:
        assert str(e) == f"cannot {action} an order that is cancelled"
o = Order()
o.pay()
o.cancel()
assert o.status == "cancelled" and o.refunded
o = Order()
try:
    o.ship()
    assert False
except InvalidTransition:
    pass
o.pay()
o.ship()
o.deliver()
assert o.status == "delivered"
```

```stdout
shipped
cannot cancel an order that is shipped
delivered
```

### Strategy

**Problem.** The cart's `total()` contains every discount rule in one growing `if/elif`. Marketing invents a new promotion every week, and each one means editing and retesting the cart.

```py
def total(cart, discount_kind):
    subtotal = sum(price * qty for _, price, qty in cart.items)
    if discount_kind == "percent10":
        return subtotal * 0.9
    elif discount_kind == "black_friday":
        return subtotal - 15 if subtotal >= 40 else subtotal
    elif ...                    # one more branch per promotion
```

**Task.** Make the discount a **pluggable strategy**: the cart computes the subtotal and asks the current strategy how much to take off. Strategies must be swappable at runtime, and new ones must not touch `Cart`.

**Idea.** Strategy defines a **family of interchangeable algorithms** behind one interface and lets the client pick one. The context (`Cart`) holds a strategy and calls it. In Python the interface can simply be "a callable that takes the subtotal and returns the discount", so a plain function, a lambda or a configurable object with `__call__` all work.

**Steps.**
1. Define the strategy type: `Discount = Callable[[float], float]`.
2. Write strategies: `no_discount` (a function), `PercentOff(percent)` and `AmountOff(amount, minimum)` (configurable callable objects that validate their settings).
3. `Cart` stores `self.discount` and uses it in `total()`. It never checks which strategy it has.
4. Swap strategies by assigning `cart.discount = ...`.

```python
from typing import Callable

Discount = Callable[[float], float]  # takes the subtotal, returns the amount to take off


def no_discount(subtotal: float) -> float:
    return 0.0


class PercentOff:
    def __init__(self, percent: float):
        if not 0 <= percent <= 100:
            raise ValueError("percent must be between 0 and 100")
        self.percent = percent

    def __call__(self, subtotal: float) -> float:
        return subtotal * self.percent / 100


class AmountOff:
    def __init__(self, amount: float, minimum: float = 0):
        self.amount, self.minimum = amount, minimum

    def __call__(self, subtotal: float) -> float:
        return min(self.amount, subtotal) if subtotal >= self.minimum else 0.0


class Cart:
    def __init__(self, discount: Discount = no_discount):
        self.discount = discount  # the strategy: swappable at runtime
        self.items: list[tuple[str, float, int]] = []

    def add(self, name: str, price: float, qty: int = 1) -> None:
        self.items.append((name, price, qty))

    def subtotal(self) -> float:
        return sum(price * qty for _, price, qty in self.items)

    def total(self) -> float:
        subtotal = self.subtotal()
        return round(subtotal - self.discount(subtotal), 2)


if __name__ == "__main__":
    cart = Cart()
    cart.add("book", 20.0, 2)
    cart.add("pen", 2.5, 4)
    print(cart.total())
    cart.discount = PercentOff(10)
    print(cart.total())
    cart.discount = AmountOff(15, minimum=40)
    print(cart.total())
    cart.discount = lambda subtotal: 5.0 if len(cart.items) >= 2 else 0.0
    print(cart.total())
```

**When to use.**
- Several algorithms do the same job in different ways (pricing, sorting keys, compression, routing, validation, retry policies) and you want to choose at runtime.
- A class has a big conditional that picks between variants of one behaviour.

**Watch out.**
- In Python, **functions are strategies**. `sorted(items, key=...)` and `max(..., key=...)` are the Strategy pattern. Write a class only when the strategy needs configuration or state.
- The strategy should get everything it needs through its arguments, not by reaching back into the context.
- For real money, use `decimal.Decimal` or integer cents instead of floats.
- Strategy vs Template Method: Strategy swaps a **whole algorithm by composition** (at runtime). Template Method varies **steps by inheritance** (fixed when you write the class).

```test
c = Cart()
assert c.total() == 0
c.add("a", 10.0, 3)
assert c.total() == 30.0
c.discount = PercentOff(25)
assert c.total() == 22.5
c.discount = AmountOff(50)
assert c.total() == 0.0
c.discount = AmountOff(5, minimum=31)
assert c.total() == 30.0
assert Cart(PercentOff(100)).total() == 0
for bad in (-1, 101):
    try:
        PercentOff(bad)
        assert False
    except ValueError:
        pass
```

```stdout
50.0
45.0
35.0
45.0
```

### Template Method

**Problem.** CSV and Markdown exporters each copy the same algorithm (handle empty input, read the columns, write a header, write the rows, add a footer). The copies slowly drift apart, and the naive CSV breaks on values that contain commas.

```py
class CsvExporter:
    def export(self, rows):
        if not rows: return ""
        cols = list(rows[0])
        out = [",".join(cols)] + [",".join(str(r[c]) for c in cols) for r in rows]
        return "\n".join(out)

class MarkdownExporter:
    def export(self, rows):
        if not rows: return "_no data_"
        cols = list(rows[0])     # the same steps, copied again
        ...
```

**Task.** Write the export algorithm **once** in a base class, and let each format provide only the steps that differ (header, row, and optionally footer and empty output).

**Idea.** Template Method puts the **skeleton of an algorithm** in a base-class method (`export`). It calls **abstract steps** that subclasses must implement (`header`, `row`), and **hooks** with default behaviour that subclasses may override (`footer`, `empty`). The order of the steps is fixed in one place. Subclasses fill in the details.

**Steps.**
1. `Exporter.export(rows)`: if there are no rows, return `self.empty()`. Otherwise take the columns from the first row, build `header`, then a `row` per item, then `footer` if it isn't empty.
2. Declare `header` and `row` as abstract. Give `footer` and `empty` defaults that return `""` (hooks).
3. `CsvExporter` uses the `csv` module, so commas and quotes are escaped correctly.
4. `MarkdownExporter` builds a table and overrides both hooks.

```python
import csv
import io
from abc import ABC, abstractmethod


class Exporter(ABC):
    def export(self, rows: list[dict]) -> str:
        # the template method: a fixed skeleton, subclasses fill in the steps
        if not rows:
            return self.empty()
        columns = list(rows[0])
        lines = [self.header(columns)]
        lines += [self.row([r.get(c, "") for c in columns]) for r in rows]
        footer = self.footer(len(rows))
        if footer:
            lines.append(footer)
        return "\n".join(lines)

    @abstractmethod
    def header(self, columns: list[str]) -> str: ...

    @abstractmethod
    def row(self, values: list) -> str: ...

    def footer(self, count: int) -> str:  # hook: optional step
        return ""

    def empty(self) -> str:  # hook
        return ""


class CsvExporter(Exporter):
    def header(self, columns: list[str]) -> str:
        return self._line(columns)

    def row(self, values: list) -> str:
        return self._line(values)

    @staticmethod
    def _line(values) -> str:
        buf = io.StringIO()
        csv.writer(buf, lineterminator="").writerow(values)  # quotes commas and quotes correctly
        return buf.getvalue()


class MarkdownExporter(Exporter):
    def header(self, columns: list[str]) -> str:
        return "| " + " | ".join(columns) + " |\n|" + "---|" * len(columns)

    def row(self, values: list) -> str:
        return "| " + " | ".join(str(v) for v in values) + " |"

    def footer(self, count: int) -> str:
        return f"\n{count} rows"

    def empty(self) -> str:
        return "_no data_"


if __name__ == "__main__":
    rows = [{"name": "Ada", "city": "London"}, {"name": "Linus", "city": "Helsinki, FI"}]
    print(CsvExporter().export(rows))
    print(MarkdownExporter().export(rows))
    print(MarkdownExporter().export([]))
```

**When to use.**
- Several classes run the **same algorithm with small differences** in some steps (exporters, parsers, test fixtures with setUp/tearDown, game turns, data pipelines).
- You want a framework to control the flow and let users customize only specific steps.

**Watch out.**
- Subclasses should **not override the template method** itself. Python has no `final` enforcement at runtime (`typing.final` is only checked by type checkers), so document it.
- Too many hooks make the flow hard to follow. If subclasses override almost every step, Strategy (composition) is probably a better fit.
- Never build CSV by joining with commas. Use the `csv` module: values containing commas, quotes or newlines must be quoted.
- Real-world examples: `unittest.TestCase` (`setUp` → test → `tearDown`), `socketserver.BaseRequestHandler`, `html.parser.HTMLParser` (`handle_starttag` hooks).

```test
rows = [{"a": 1, "b": 'say "hi"'}, {"a": 2}]
assert CsvExporter().export(rows) == 'a,b\n1,"say ""hi"""\n2,'
assert CsvExporter().export([]) == ""
md = MarkdownExporter().export([{"x": 1}])
assert md == "| x |\n|---|\n| 1 |\n\n1 rows"
class TsvExporter(Exporter):
    def header(self, columns): return "\t".join(columns)
    def row(self, values): return "\t".join(map(str, values))
assert TsvExporter().export([{"k": "v"}]) == "k\nv"
try:
    Exporter()
    assert False
except TypeError:
    pass
```

```stdout
name,city
Ada,London
Linus,"Helsinki, FI"
| name | city |
|---|---|
| Ada | London |
| Linus | Helsinki, FI |

2 rows
_no data_
```

### Visitor

**Problem.** Every new feature on shapes (area, JSON export, SVG, perimeter…) adds a method to every shape class. The shape classes fill up with unrelated code, and one feature is spread over many files.

```py
@dataclass
class Circle:
    radius: float
    def area(self): ...
    def to_json(self): ...
    def to_svg(self): ...
    def perimeter(self): ...
    # every new feature = edit every shape class
```

**Task.** Add new **operations** over a structure of shapes (including nested groups) **without changing the shape classes**. Each operation must live in one class.

**Idea.** Visitor moves each operation into a **visitor class** with one method per element type (`visit_circle`, `visit_rectangle`, `visit_group`). Each element has a single `accept(visitor)` method that calls the right one (`visitor.visit_circle(self)`). This **double dispatch** picks the code by both the operation and the element type. Adding an operation = adding a visitor. The elements stay untouched.

**Steps.**
1. `Shape` declares `accept(visitor)`. `Circle`, `Rectangle` and `Group` implement it with one line each.
2. `ShapeVisitor` declares one abstract `visit_*` method per shape type.
3. `AreaVisitor` computes areas. For a group, it sums `child.accept(self)` over its shapes.
4. `JsonVisitor` builds JSON-ready dicts the same way. A new operation (perimeter, SVG) is one more visitor.

```python
import json
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


class Shape(ABC):
    @abstractmethod
    def accept(self, visitor: "ShapeVisitor"): ...


@dataclass
class Circle(Shape):
    radius: float

    def accept(self, visitor):
        return visitor.visit_circle(self)


@dataclass
class Rectangle(Shape):
    width: float
    height: float

    def accept(self, visitor):
        return visitor.visit_rectangle(self)


@dataclass
class Group(Shape):
    shapes: list[Shape] = field(default_factory=list)

    def accept(self, visitor):
        return visitor.visit_group(self)


class ShapeVisitor(ABC):
    @abstractmethod
    def visit_circle(self, c: Circle): ...

    @abstractmethod
    def visit_rectangle(self, r: Rectangle): ...

    @abstractmethod
    def visit_group(self, g: Group): ...


class AreaVisitor(ShapeVisitor):
    def visit_circle(self, c: Circle) -> float:
        return math.pi * c.radius ** 2

    def visit_rectangle(self, r: Rectangle) -> float:
        return r.width * r.height

    def visit_group(self, g: Group) -> float:
        return sum(s.accept(self) for s in g.shapes)


class JsonVisitor(ShapeVisitor):
    def visit_circle(self, c: Circle) -> dict:
        return {"type": "circle", "radius": c.radius}

    def visit_rectangle(self, r: Rectangle) -> dict:
        return {"type": "rectangle", "width": r.width, "height": r.height}

    def visit_group(self, g: Group) -> dict:
        return {"type": "group", "shapes": [s.accept(self) for s in g.shapes]}


if __name__ == "__main__":
    drawing = Group([Rectangle(2, 3), Group([Circle(1), Rectangle(1, 1)])])
    print(round(drawing.accept(AreaVisitor()), 2))
    print(json.dumps(drawing.accept(JsonVisitor())))
```

**When to use.**
- The element classes are **stable**, but you keep adding **operations** over them: compilers and linters walking an AST, exporters, reports over a document tree.
- You want all the code of one operation in one place.

**Watch out.**
- The trade-off is the reverse of OCP with polymorphism: new **operations** are easy, new **element types** are hard (every visitor needs a new method). Pick Visitor only if the element types rarely change.
- Visitors often need access to the elements' data, which can weaken encapsulation.
- Pythonic alternative: `functools.singledispatch` gives type-based dispatch without `accept` methods:

```py
from functools import singledispatch

@singledispatch
def area(shape) -> float:
    raise TypeError(type(shape).__name__)

@area.register
def _(shape: Circle) -> float:
    return math.pi * shape.radius ** 2

@area.register
def _(shape: Group) -> float:
    return sum(area(s) for s in shape.shapes)
```

- Real-world example: Python's own `ast.NodeVisitor` (`visit_FunctionDef`, `visit_Call`, …).

```test
assert Rectangle(2, 5).accept(AreaVisitor()) == 10
assert Group().accept(AreaVisitor()) == 0
assert abs(Group([Circle(1), Group([Circle(1)])]).accept(AreaVisitor()) - 2 * math.pi) < 1e-9
assert Group([Circle(2)]).accept(JsonVisitor()) == {"type": "group", "shapes": [{"type": "circle", "radius": 2}]}
class PerimeterVisitor(ShapeVisitor):
    def visit_circle(self, c): return 2 * math.pi * c.radius
    def visit_rectangle(self, r): return 2 * (r.width + r.height)
    def visit_group(self, g): return sum(s.accept(self) for s in g.shapes)
assert Group([Rectangle(1, 2), Rectangle(3, 3)]).accept(PerimeterVisitor()) == 18
class Incomplete(ShapeVisitor):
    def visit_circle(self, c): return 0
try:
    Incomplete()
    assert False
except TypeError:
    pass
```

```stdout
10.14
{"type": "group", "shapes": [{"type": "rectangle", "width": 2, "height": 3}, {"type": "group", "shapes": [{"type": "circle", "radius": 1}, {"type": "rectangle", "width": 1, "height": 1}]}]}
```
