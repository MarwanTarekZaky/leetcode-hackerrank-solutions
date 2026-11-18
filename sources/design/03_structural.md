## Structural Patterns

### Adapter

**Problem.** The shop calls `processor.pay(amount_cents) -> bool` everywhere. The bank you must now support ships an SDK with a different interface, and you can't edit the SDK.

```py
# our code, everywhere:
processor.pay(1999)                              # cents in, True/False out

# the bank's SDK (third-party, can't change it):
LegacyBankApi().send_money("19.99", "USD")       # -> {"status": "OK", ...}
```

**Task.** Make `LegacyBankApi` usable everywhere a `PaymentProcessor` is expected, without changing either side. `pay(1999)` must call `send_money("19.99", currency)`.

**Idea.** An Adapter is a **wrapper that translates one interface into another**. It implements the interface your code expects (`pay`), holds the incompatible object, and converts each call: the arguments on the way in (cents → `"19.99"`), and the result on the way out (`{"status": "OK"}` → `True`).

**Steps.**
1. Describe the target interface (`PaymentProcessor` with `pay(amount_cents) -> bool`).
2. Write `LegacyBankAdapter`, which receives the SDK object (and the currency) in its constructor.
3. In `pay`: reject negative amounts, format cents as a decimal string with integer math, call `send_money`, and turn the status into a `bool`.
4. Client code (`checkout`) works with the adapter exactly as with a native processor.

```python
from typing import Protocol


class PaymentProcessor(Protocol):
    def pay(self, amount_cents: int) -> bool: ...


class ModernGateway:
    def pay(self, amount_cents: int) -> bool:
        return amount_cents > 0


class LegacyBankApi:
    # third-party code: we can't change it
    def send_money(self, amount: str, currency: str) -> dict:
        ok = float(amount) > 0
        return {"status": "OK" if ok else "ERROR", "amount": amount, "currency": currency}


class LegacyBankAdapter:
    def __init__(self, api: LegacyBankApi, currency: str = "USD"):
        self.api = api
        self.currency = currency

    def pay(self, amount_cents: int) -> bool:
        if amount_cents < 0:
            raise ValueError("amount must not be negative")
        amount = f"{amount_cents // 100}.{amount_cents % 100:02d}"  # 1999 -> "19.99" without float rounding
        return self.api.send_money(amount, self.currency)["status"] == "OK"


def checkout(processor: PaymentProcessor, amount_cents: int) -> str:
    return "paid" if processor.pay(amount_cents) else "declined"


if __name__ == "__main__":
    print(checkout(ModernGateway(), 1999))
    print(checkout(LegacyBankAdapter(LegacyBankApi()), 1999))
    print(checkout(LegacyBankAdapter(LegacyBankApi()), 0))
```

**When to use.**
- You want to use an existing class (third-party SDK, legacy module) whose interface doesn't match what your code expects.
- You want to keep a vendor's API out of your business code, so switching vendors means writing one new adapter.

**Watch out.**
- An adapter **translates** only. It shouldn't add business logic. That belongs in the service that uses it.
- Money: never convert cents with `amount_cents / 100` and float formatting for real payments. Use integer math or `decimal.Decimal`.
- Adapter vs Facade: an adapter makes **one** object fit an **existing** interface. A facade defines a **new**, simpler interface over **many** objects.
- Adapter vs Decorator: an adapter **changes** the interface. A decorator **keeps** it and adds behaviour.

```test
class SpyApi(LegacyBankApi):
    def __init__(self): self.calls = []
    def send_money(self, amount, currency):
        self.calls.append((amount, currency))
        return super().send_money(amount, currency)
spy = SpyApi()
a = LegacyBankAdapter(spy, "EUR")
assert a.pay(1999) and a.pay(5) and not a.pay(0)
assert spy.calls == [("19.99", "EUR"), ("0.05", "EUR"), ("0.00", "EUR")]
try:
    a.pay(-1)
    assert False
except ValueError:
    pass
assert checkout(a, 100) == "paid" and checkout(ModernGateway(), 0) == "declined"
```

```stdout
paid
paid
declined
```

### Bridge

**Problem.** Shapes can be drawn as SVG or as ASCII. With inheritance, every shape × renderer pair is its own class, and the number of classes multiplies.

```py
class SvgCircle: ...
class AsciiCircle: ...
class SvgSquare: ...
class AsciiSquare: ...
# add Triangle -> 2 more classes; add a PNG renderer -> 3 more. N shapes x M renderers.
```

**Task.** Let shapes and renderers vary **independently**, so adding a shape or a renderer is one new class, and a shape can even switch renderer at runtime.

**Idea.** Bridge splits one hierarchy into two: the **abstraction** (`Shape`: what to draw) and the **implementation** (`Renderer`: how to draw). The abstraction **holds a reference** to an implementation (the "bridge") and delegates the low-level work to it. N shapes + M renderers = N + M classes instead of N × M.

**Steps.**
1. Define `Renderer` with the primitive operations (`circle(radius)`, `square(side)`), and write `SvgRenderer` and `AsciiRenderer`.
2. Define `Shape`, which receives a renderer in its constructor.
3. `Circle` and `Square` keep their own data and logic (`scale`), and draw by calling `self.renderer`.
4. Combine freely: `Circle(SvgRenderer(), 2)`, `Square(AsciiRenderer(), 3)`.

```python
from abc import ABC, abstractmethod


class Renderer(ABC):
    # the implementation side: how to draw
    @abstractmethod
    def circle(self, radius: float) -> str: ...

    @abstractmethod
    def square(self, side: float) -> str: ...


class SvgRenderer(Renderer):
    def circle(self, radius: float) -> str:
        return f'<circle r="{radius}"/>'

    def square(self, side: float) -> str:
        return f'<rect width="{side}" height="{side}"/>'


class AsciiRenderer(Renderer):
    def circle(self, radius: float) -> str:
        return f"O radius {radius}"

    def square(self, side: float) -> str:
        return f"[] side {side}"


class Shape(ABC):
    # the abstraction side: what to draw; holds the bridge to a Renderer
    def __init__(self, renderer: Renderer):
        self.renderer = renderer

    @abstractmethod
    def draw(self) -> str: ...

    @abstractmethod
    def scale(self, factor: float) -> None: ...


class Circle(Shape):
    def __init__(self, renderer: Renderer, radius: float):
        super().__init__(renderer)
        self.radius = radius

    def draw(self) -> str:
        return self.renderer.circle(self.radius)

    def scale(self, factor: float) -> None:
        self.radius *= factor


class Square(Shape):
    def __init__(self, renderer: Renderer, side: float):
        super().__init__(renderer)
        self.side = side

    def draw(self) -> str:
        return self.renderer.square(self.side)

    def scale(self, factor: float) -> None:
        self.side *= factor


if __name__ == "__main__":
    for renderer in (SvgRenderer(), AsciiRenderer()):
        shapes = [Circle(renderer, 2), Square(renderer, 3)]
        shapes[0].scale(2)
        print([s.draw() for s in shapes])
```

**When to use.**
- A class varies along **two independent dimensions** (shape × renderer, notification type × delivery channel, remote control × device).
- You want to switch the implementation at runtime, or share one implementation between many abstractions.

**Watch out.**
- Bridge is designed **up front** to keep two hierarchies apart. Adapter is applied **afterwards** to make existing classes fit.
- Keep the implementation interface low-level (primitives). If `Renderer` grows a method for every shape, consider giving it smaller building blocks (lines, arcs).
- Bridge is "composition over inheritance" applied to a whole hierarchy.

```test
c = Circle(SvgRenderer(), 1.5)
assert c.draw() == '<circle r="1.5"/>'
c.renderer = AsciiRenderer()
assert c.draw() == "O radius 1.5"
s = Square(AsciiRenderer(), 2)
s.scale(3)
assert s.draw() == "[] side 6"
class MarkdownRenderer(Renderer):
    def circle(self, radius): return f"(circle {radius})"
    def square(self, side): return f"(square {side})"
assert [x.draw() for x in (Circle(MarkdownRenderer(), 1), Square(MarkdownRenderer(), 2))] == ["(circle 1)", "(square 2)"]
```

```stdout
['<circle r="4"/>', '<rect width="3" height="3"/>']
['O radius 4', '[] side 3']
```

### Composite

**Problem.** To compute the size of a folder, every caller writes its own recursive walk and has to check whether each item is a file or a folder.

```py
def total_size(item):
    if isinstance(item, File):
        return item.size
    total = 0
    for child in item.children:     # every caller re-implements the walk
        total += total_size(child)  # and must know every node type
    return total
```

**Task.** Let clients treat a single file and a whole folder tree **the same way**: `node.size()` and `node.lines()` must work on both.

**Idea.** Composite builds **part–whole trees** where leaves (`File`) and containers (`Folder`) share one interface (`Node`). A container implements each operation by **delegating to its children** and combining the results. Clients call `size()` on the root and never check types; the recursion lives inside the tree.

**Steps.**
1. Define `Node` with `size()` and `lines(depth)`.
2. `File` (leaf) returns its own size and one line.
3. `Folder` (composite) keeps a list of child nodes. `size()` sums the children's sizes. `lines()` prints its own header, then its children one level deeper.
4. `add(*children)` returns `self` so trees can be built fluently.

```python
from abc import ABC, abstractmethod


class Node(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def size(self) -> int: ...

    @abstractmethod
    def lines(self, depth: int = 0) -> list[str]: ...


class File(Node):
    def __init__(self, name: str, size: int):
        super().__init__(name)
        self._size = size

    def size(self) -> int:
        return self._size

    def lines(self, depth: int = 0) -> list[str]:
        return ["  " * depth + f"{self.name} ({self._size})"]


class Folder(Node):
    def __init__(self, name: str, *children: Node):
        super().__init__(name)
        self.children: list[Node] = list(children)

    def add(self, *children: Node) -> "Folder":
        self.children.extend(children)
        return self

    def size(self) -> int:
        return sum(child.size() for child in self.children)  # same call for files and folders

    def lines(self, depth: int = 0) -> list[str]:
        out = ["  " * depth + f"{self.name}/ ({self.size()})"]
        for child in self.children:
            out += child.lines(depth + 1)
        return out


if __name__ == "__main__":
    root = Folder("project",
                  File("README.md", 120),
                  Folder("src", File("main.py", 300), File("util.py", 80)),
                  Folder("empty"))
    print("\n".join(root.lines()))
```

**When to use.**
- Your data is a **tree**: file systems, UI widgets inside containers, menus and submenus, org charts, expressions, scene graphs.
- Clients should handle one item and a group of items the same way.

**Watch out.**
- Decide where child-management methods (`add`, `remove`) live. Putting them only on `Folder` is safer (you can't add children to a file). Putting them on `Node` is more uniform but leaves needs to reject them.
- Deep trees and recursion: Python's default recursion limit is about 1000. For very deep trees, use an explicit stack.
- Recomputing `size()` at every level is O(n) per call. Cache it if the tree is large and rarely changes.
- Avoid cycles (a folder inside itself). They make every operation loop forever.

```test
src = Folder("src").add(File("a.py", 10), File("b.py", 5))
root = Folder("root", src, File("x", 1))
assert src.size() == 15 and root.size() == 16 and Folder("e").size() == 0
assert File("f", 7).size() == 7
assert root.lines() == ["root/ (16)", "  src/ (15)", "    a.py (10)", "    b.py (5)", "  x (1)"]
assert all(isinstance(n, Node) for n in (root, src, File("f", 1)))
```

```stdout
project/ (500)
  README.md (120)
  src/ (380)
    main.py (300)
    util.py (80)
  empty/ (0)
```

### Decorator

**Problem.** Data can be stored in memory or in files, optionally compressed, optionally Base64-encoded. Subclassing every combination makes the number of classes explode.

```py
class CompressedMemorySource(MemorySource): ...
class EncodedMemorySource(MemorySource): ...
class CompressedEncodedMemorySource(MemorySource): ...
class CompressedFileSource(FileSource): ...
# every combination of features x storages is a new subclass
```

**Task.** Add compression and encoding **on top of any source**, in any combination and order, chosen at runtime, without changing the source classes.

**Idea.** A Decorator **wraps an object and has the same interface** as the object it wraps. It forwards each call to the wrapped object and adds behaviour before or after. Because a decorator *is* a `DataSource`, decorators can wrap other decorators: `Compression(Base64(MemorySource()))` is a stack of features built at runtime.

**Steps.**
1. Define the component interface `DataSource` with `write(data)` and `read()`.
2. Write the plain component `MemorySource`.
3. Write `SourceDecorator`, which holds a `wrapped` source and forwards both calls.
4. Each concrete decorator overrides the calls: `Compression` compresses on write and decompresses on read; `Base64` encodes on write and decodes on read.

```python
import base64
import zlib
from abc import ABC, abstractmethod


class DataSource(ABC):
    @abstractmethod
    def write(self, data: bytes) -> None: ...

    @abstractmethod
    def read(self) -> bytes: ...


class MemorySource(DataSource):
    def __init__(self):
        self.stored = b""

    def write(self, data: bytes) -> None:
        self.stored = data

    def read(self) -> bytes:
        return self.stored


class SourceDecorator(DataSource):
    # same interface as what it wraps, so decorators can stack
    def __init__(self, wrapped: DataSource):
        self.wrapped = wrapped

    def write(self, data: bytes) -> None:
        self.wrapped.write(data)

    def read(self) -> bytes:
        return self.wrapped.read()


class Compression(SourceDecorator):
    def write(self, data: bytes) -> None:
        super().write(zlib.compress(data))

    def read(self) -> bytes:
        return zlib.decompress(super().read())


class Base64(SourceDecorator):
    def write(self, data: bytes) -> None:
        super().write(base64.b64encode(data))

    def read(self) -> bytes:
        return base64.b64decode(super().read())


if __name__ == "__main__":
    storage = MemorySource()
    source = Compression(Base64(storage))   # compress first, then encode as text
    source.write(b"hello " * 20)
    print(source.read() == b"hello " * 20)
    print(storage.stored.isascii(), len(storage.stored) < 120)
```

**When to use.**
- You need to add responsibilities to objects **at runtime**, in combinations, without subclassing every combination (I/O streams, middleware, caching, logging, retries).
- You can't or don't want to change the original class.

**Watch out.**
- **Order matters**: `Compression(Base64(s))` compresses then encodes. `Base64(Compression(s))` encodes then compresses (and stores binary). Reading must undo the steps in reverse order, which the stack does for you.
- The GoF Decorator pattern is not the same as Python's `@decorator` syntax, but they share the idea: wrap and add behaviour, keep the interface. Python's version wraps **functions**:

```py
import functools

def retry(times: int):
    def decorate(fn):
        @functools.wraps(fn)          # keep the name and docstring of fn
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return fn(*args, **kwargs)
                except ConnectionError:
                    if attempt == times - 1:
                        raise
        return wrapper
    return decorate
```

- Decorators that forget to forward a method break the interface. `SourceDecorator` forwards everything by default, so concrete decorators override only what they change.
- Real-world examples: `io.BufferedReader(io.FileIO(...))`, `gzip.GzipFile(fileobj=...)`, WSGI/ASGI middleware.

```test
for make in (lambda s: s, Compression, Base64, lambda s: Compression(Base64(s)), lambda s: Base64(Compression(s))):
    store = MemorySource()
    src = make(store)
    src.write(b"data \x00\xff" * 5)
    assert src.read() == b"data \x00\xff" * 5
store = MemorySource()
Base64(store).write(b"hi")
assert store.stored == b"aGk="
store = MemorySource()
Compression(Base64(store)).write(b"x" * 1000)
assert store.stored.isascii() and len(store.stored) < 50
assert isinstance(Compression(MemorySource()), DataSource)
```

```stdout
True
True True
```

### Facade

**Problem.** Placing an order means calling inventory, payments and shipping in the right order, and putting the stock back if the payment fails. Every caller repeats this sequence, and some forget the rollback.

```py
# every caller repeats this, in this exact order, with this exact rollback:
inventory.reserve("book", 2)
try:
    tx = payments.charge(prices["book"] * 2)
except ValueError:
    inventory.release("book", 2)
    raise
label = shipping.ship("book", 2, "Cairo")
```

**Task.** Give clients **one simple call**, `place_order(item, qty, address)`, that runs the whole workflow correctly, while the subsystems stay available for anyone who needs them directly.

**Idea.** A Facade is a class with a **simple, high-level interface** in front of a complex subsystem. It knows which objects to call, in what order, and how to undo things on failure. Clients depend on the facade instead of on every subsystem class. The subsystems don't know the facade exists.

**Steps.**
1. Keep the subsystems as they are: `Inventory` (reserve/release), `Payments` (charge, with a limit), `Shipping` (ship).
2. `Checkout` (the facade) receives the subsystems and a price list in its constructor.
3. `place_order`: reserve stock, then charge. If the charge fails, release the stock and re-raise. Then ship and return a summary.
4. Clients only call `place_order`.

```python
class Inventory:
    def __init__(self, stock: dict[str, int]):
        self.stock = dict(stock)

    def reserve(self, item: str, qty: int) -> None:
        if self.stock.get(item, 0) < qty:
            raise ValueError(f"out of stock: {item}")
        self.stock[item] -= qty

    def release(self, item: str, qty: int) -> None:
        self.stock[item] += qty


class Payments:
    def __init__(self, limit: int):
        self.limit = limit
        self.charges: list[int] = []

    def charge(self, amount: int) -> str:
        if amount > self.limit:
            raise ValueError(f"payment declined: {amount} > limit {self.limit}")
        self.charges.append(amount)
        return f"tx{len(self.charges)}"


class Shipping:
    def ship(self, item: str, qty: int, address: str) -> str:
        return f"ship {qty} x {item} to {address}"


class Checkout:
    # the facade: one simple call that runs the whole workflow correctly
    def __init__(self, inventory: Inventory, payments: Payments, shipping: Shipping, prices: dict[str, int]):
        self.inventory = inventory
        self.payments = payments
        self.shipping = shipping
        self.prices = prices

    def place_order(self, item: str, qty: int, address: str) -> dict:
        self.inventory.reserve(item, qty)
        try:
            tx = self.payments.charge(self.prices[item] * qty)
        except Exception:
            self.inventory.release(item, qty)  # roll back so stock stays correct
            raise
        return {"tx": tx, "shipment": self.shipping.ship(item, qty, address)}


if __name__ == "__main__":
    shop = Checkout(Inventory({"book": 5}), Payments(limit=60), Shipping(), prices={"book": 25})
    print(shop.place_order("book", 2, "Cairo"))
    try:
        shop.place_order("book", 3, "Paris")
    except ValueError as e:
        print("failed:", e)
    print(shop.inventory.stock)
```

**When to use.**
- A subsystem has many classes and a common workflow that clients keep re-implementing.
- You want to layer a system: each layer talks to the one below only through a facade.
- You want to hide a messy legacy API behind something simple.

**Watch out.**
- A facade should **simplify, not hide**. Clients that need fine control can still use the subsystems directly.
- Don't let the facade become a "god object" that holds all business logic. It **coordinates**. The rules stay in the subsystems.
- The rollback (`except Exception: release; raise`) is the part callers usually get wrong. Centralizing it is a big part of the value.
- Real-world examples: `requests.get(url)` in front of sessions, adapters and connection pools; `subprocess.run` in front of `Popen`.

```test
inv, pay = Inventory({"pen": 2}), Payments(limit=10)
shop = Checkout(inv, pay, Shipping(), {"pen": 4})
assert shop.place_order("pen", 2, "Oslo") == {"tx": "tx1", "shipment": "ship 2 x pen to Oslo"}
assert inv.stock == {"pen": 0} and pay.charges == [8]
try:
    shop.place_order("pen", 1, "Oslo")
    assert False
except ValueError as e:
    assert "out of stock" in str(e)
assert pay.charges == [8]
inv.stock["pen"] = 5
try:
    shop.place_order("pen", 3, "Oslo")
    assert False
except ValueError:
    pass
assert inv.stock == {"pen": 5} and pay.charges == [8]
```

```stdout
{'tx': 'tx1', 'shipment': 'ship 2 x book to Cairo'}
failed: payment declined: 75 > limit 60
{'book': 3}
```

### Flyweight

**Problem.** A text editor stores the font, size and colour inside every character object. A book of a million characters holds a million copies of the same few styles.

```py
class Char:
    def __init__(self, ch, font, size, color):
        self.ch = ch
        self.font, self.size, self.color = font, size, color   # repeated for every character

doc = [Char(c, "Arial", 12, "black") for c in book_text]       # 1,000,000 identical style copies
```

**Task.** Store each distinct style **once** and share it between all characters that use it. 10,011 characters in 2 styles must create only 2 style objects.

**Idea.** Flyweight splits an object's state in two. The **intrinsic** state is the same for many objects (font, size, colour), so it becomes an immutable, shared object. The **extrinsic** state is unique (the character itself, its position) and is stored outside or passed in. A **factory** with a pool returns the existing shared object instead of creating a new one.

**Steps.**
1. Make `Style` a frozen (immutable, hashable) dataclass. Sharing is only safe if nobody can change it.
2. `StyleFactory.get(font, size, color)` looks up the tuple key in a dict and creates the style only the first time.
3. `Document` stores `(char, style)` pairs, where the style comes from the factory.
4. `len(factory)` shows how many distinct styles exist.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Style:
    # intrinsic state: shared, so it must be immutable
    font: str
    size: int
    color: str


class StyleFactory:
    def __init__(self):
        self._pool: dict[tuple, Style] = {}

    def get(self, font: str, size: int, color: str) -> Style:
        key = (font, size, color)
        if key not in self._pool:
            self._pool[key] = Style(font, size, color)
        return self._pool[key]

    def __len__(self) -> int:
        return len(self._pool)


class Document:
    def __init__(self, factory: StyleFactory):
        self.factory = factory
        self.chars: list[tuple[str, Style]] = []  # extrinsic state: the character itself

    def add(self, text: str, font: str = "Arial", size: int = 12, color: str = "black") -> None:
        style = self.factory.get(font, size, color)
        self.chars.extend((ch, style) for ch in text)


if __name__ == "__main__":
    factory = StyleFactory()
    doc = Document(factory)
    doc.add("Hello ", "Arial", 12, "black")
    doc.add("World", "Arial", 12, "red")
    doc.add("!" * 10_000, "Arial", 12, "black")
    print(len(doc.chars), len(factory))
    print(doc.chars[0][1] is doc.chars[-1][1])
```

**When to use.**
- You have a **huge number** of similar objects and memory is a real problem (characters, map tiles, particles, game units, tree sprites).
- Most of each object's state can be shared, and the shared part can be immutable.

**Watch out.**
- Shared objects **must be immutable**. If one character could change its shared style, every character using it would change.
- Measure first (`sys.getsizeof`, `tracemalloc`). Flyweight adds complexity, so use it only when memory matters.
- Python has flyweights built in: small integers and interned strings (`sys.intern`) are shared. `functools.cache` on a factory function is a one-line flyweight pool:

```py
from functools import cache

@cache
def get_style(font: str, size: int, color: str) -> Style:
    return Style(font, size, color)
```

- `__slots__` on the per-item class (no per-instance `__dict__`) is another big memory saving that combines well with Flyweight.

```test
f = StyleFactory()
a = f.get("Mono", 10, "red")
assert a is f.get("Mono", 10, "red") and a is not f.get("Mono", 11, "red") and len(f) == 2
doc = Document(f)
doc.add("ab", "Mono", 10, "red")
doc.add("c")
assert [c for c, _ in doc.chars] == ["a", "b", "c"] and doc.chars[0][1] is a and len(f) == 3
from dataclasses import FrozenInstanceError
try:
    a.color = "blue"
    assert False
except FrozenInstanceError:
    pass
```

```stdout
10011 2
True
```

### Proxy

**Problem.** Thousands of users ask a slow, rate-limited weather API for the same few cities. Every page view makes a network call for an answer we already had.

```py
service = RemoteWeatherService()
for user in users:                         # 10,000 users in 3 cities
    show(service.forecast(user.city))      # 10,000 slow network calls, same 3 answers
```

**Task.** Cut the remote calls without changing `RemoteWeatherService` or its callers: they keep calling `.forecast(city)`. Answers older than a time-to-live (TTL) must be fetched again.

**Idea.** A Proxy is a **stand-in with the same interface** as the real object. It **controls access** to it: here it serves cached answers and only calls the real service on a miss or when the entry is too old. Other common proxies: **virtual** (create the expensive object lazily), **protection** (check permissions), **remote** (hide the network), **logging**.

**Steps.**
1. Describe the interface (`WeatherService.forecast(city)`).
2. `CachingWeatherProxy` receives the real service, a TTL and a **clock** function (injected so tests can control time).
3. In `forecast`: if the city is cached and younger than the TTL, return the cached value.
4. Otherwise call the real service, store `(value, time)`, and return the value.

```python
import time
from typing import Callable, Protocol


class WeatherService(Protocol):
    def forecast(self, city: str) -> str: ...


class RemoteWeatherService:
    def __init__(self):
        self.calls = 0

    def forecast(self, city: str) -> str:
        self.calls += 1  # imagine a slow, rate-limited HTTP call here
        return f"{city}: sunny"


class CachingWeatherProxy:
    def __init__(self, service: WeatherService, ttl: float = 600,
                 clock: Callable[[], float] = time.monotonic):
        self._service = service
        self._ttl = ttl
        self._clock = clock
        self._cache: dict[str, tuple[str, float]] = {}

    def forecast(self, city: str) -> str:
        now = self._clock()
        hit = self._cache.get(city)
        if hit is not None and now - hit[1] < self._ttl:
            return hit[0]
        value = self._service.forecast(city)
        self._cache[city] = (value, now)
        return value


if __name__ == "__main__":
    remote = RemoteWeatherService()
    weather = CachingWeatherProxy(remote)
    for city in ["Cairo", "Cairo", "Oslo", "Cairo"]:
        print(weather.forecast(city))
    print("remote calls:", remote.calls)
```

**When to use.**
- **Caching** expensive or rate-limited calls.
- **Lazy loading**: create a heavy object only when it's first used.
- **Access control**, **logging**, **metrics** or **rate limiting** around an object, without touching it or its callers.

**Watch out.**
- Proxy vs Decorator: same structure (wrap + same interface). A proxy **controls access** and usually manages the real object's lifecycle. A decorator **adds features** and is stacked by the client.
- Caches need a limit and an expiry policy. Otherwise they grow forever or serve stale data.
- Use `time.monotonic()` for measuring durations. `time.time()` can jump when the system clock changes.
- For pure functions, `functools.lru_cache(maxsize=...)` is a ready-made caching proxy.

```test
now = [0.0]
remote = RemoteWeatherService()
p = CachingWeatherProxy(remote, ttl=10, clock=lambda: now[0])
assert p.forecast("A") == "A: sunny" and p.forecast("A") == "A: sunny" and remote.calls == 1
now[0] = 9.9
p.forecast("A")
assert remote.calls == 1
now[0] = 10
p.forecast("A")
assert remote.calls == 2
p.forecast("B")
assert remote.calls == 3
```

```stdout
Cairo: sunny
Cairo: sunny
Oslo: sunny
Cairo: sunny
remote calls: 2
```
