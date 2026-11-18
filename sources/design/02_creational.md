## Creational Patterns

### Singleton

**Problem.** Configuration is loaded in many places with `Config()`. Every call creates a fresh object, so a setting changed in one module is invisible in another.

```py
class Config:
    def __init__(self):
        self.settings = load_settings_from_disk()   # slow, and every caller gets its own copy

Config().settings["debug"] = True
Config().settings["debug"]                       # KeyError: a brand-new object
```

**Task.** Make `Config() is Config()` always `True`, even when many threads create it at the same time.

**Idea.** A Singleton guarantees **one instance** of a class and a global access point to it. In Python, object creation goes through `__new__` before `__init__`. Override `__new__` to create the instance once, store it on the class, and return the stored one on every later call. A lock with a second check (double-checked locking) stops two threads from both creating it.

**Steps.**
1. Keep `_instance = None` and a `threading.Lock()` as class attributes.
2. In `__new__`: if there's no instance yet, take the lock and check **again** (another thread may have won the race), then create it with `super().__new__(cls)`.
3. Initialize the state inside that branch, not in `__init__`, because `__init__` runs on **every** `Config()` call and would reset it.
4. Return the stored instance.

```python
import threading


class Config:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # double-checked: another thread may have created it
                    instance = super().__new__(cls)
                    instance._settings = {}
                    cls._instance = instance
        return cls._instance

    def get(self, key, default=None):
        return self._settings.get(key, default)

    def set(self, key, value):
        self._settings[key] = value


if __name__ == "__main__":
    a, b = Config(), Config()
    a.set("debug", True)
    print(a is b, b.get("debug"))
```

**When to use.**
- Exactly one object must coordinate something shared: a configuration, a connection pool, a logger, a hardware device.
- Creating it is expensive and it is safe to share.

**Watch out.**
- **Most Pythonic singleton: a module.** A module is imported once, so `settings = Config()` in `config.py` and `from config import settings` everywhere is a singleton without any tricks.
- Singletons are **global state**. They hide dependencies and leak state between tests. Often it's better to create one object at startup and pass it in (see Dependency Inversion).
- `__init__` runs on every call, so putting state in `__init__` resets it each time.
- Subclasses: `cls._instance` is first read from the parent. For class hierarchies, use a metaclass with a dict keyed by class:

```py
class SingletonMeta(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    ...
```

```test
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(8) as pool:
    ids = set(pool.map(lambda _: id(Config()), range(200)))
assert len(ids) == 1
c = Config()
c.set("level", 3)
assert Config().get("level") == 3 and Config().get("missing", "x") == "x"
assert Config() is c
```

```stdout
True True
```

### Factory Method

**Problem.** `Notifier.notify` decides with `if/elif` which channel object to create. The sending logic is tied to every concrete channel, and a new channel means editing this method.

```py
class Notifier:
    def notify(self, kind, to, text):
        if kind == "email":
            channel = EmailChannel()
        elif kind == "sms":
            channel = SmsChannel()
        # a push channel? edit this method again
        return channel.send(to, text.strip())
```

**Task.** Let **subclasses** decide which `Channel` to create, so `notify()` never changes when a new channel is added.

**Idea.** Factory Method moves object creation into a separate, overridable method: `create_channel()`. The base class (`Notifier`, the *creator*) holds the shared logic and calls `self.create_channel()` without knowing the concrete class. Each subclass overrides that one method to return its own product (`EmailChannel`, `SmsChannel`).

**Steps.**
1. Define the product interface `Channel` with `send(to, text)`.
2. Write the concrete products: `EmailChannel`, `SmsChannel` (SMS cuts the text to 160 characters).
3. In `Notifier`, declare the abstract **factory method** `create_channel()`, and write `notify()` using it.
4. `EmailNotifier` and `SmsNotifier` only override `create_channel()`.

```python
from abc import ABC, abstractmethod


class Channel(ABC):
    @abstractmethod
    def send(self, to: str, text: str) -> str: ...


class EmailChannel(Channel):
    def send(self, to: str, text: str) -> str:
        return f"email to {to}: {text}"


class SmsChannel(Channel):
    def send(self, to: str, text: str) -> str:
        return f"sms to {to}: {text[:160]}"


class Notifier(ABC):
    @abstractmethod
    def create_channel(self) -> Channel: ...  # the factory method

    def notify(self, to: str, text: str) -> str:
        # shared logic: never changes when a new channel is added
        channel = self.create_channel()
        return channel.send(to, text.strip())


class EmailNotifier(Notifier):
    def create_channel(self) -> Channel:
        return EmailChannel()


class SmsNotifier(Notifier):
    def create_channel(self) -> Channel:
        return SmsChannel()


if __name__ == "__main__":
    for notifier in (EmailNotifier(), SmsNotifier()):
        print(notifier.notify("ada", "  Build passed  "))
```

**When to use.**
- A class has a workflow that is the same for all variants, but needs to create a different object for each variant.
- A framework lets users plug in their own classes: users subclass and override the factory method.

**Watch out.**
- Don't confuse it with a **simple factory** (one function with a dict lookup). That is often all you need in Python, because classes are first-class objects:

```py
CHANNELS = {"email": EmailChannel, "sms": SmsChannel}

def make_channel(kind: str) -> Channel:
    try:
        return CHANNELS[kind]()
    except KeyError:
        raise ValueError(f"unknown channel {kind!r}") from None
```

- Factory Method uses **inheritance** (a subclass per product). Abstract Factory uses **composition** (an object that creates a family of products).
- Factory Method is a special case of Template Method: one step of the algorithm is "create the object".

```test
assert EmailNotifier().notify("x", "hi") == "email to x: hi"
assert SmsNotifier().notify("x", "a" * 200) == "sms to x: " + "a" * 160
class PushChannel(Channel):
    def send(self, to, text): return f"push to {to}: {text}"
class PushNotifier(Notifier):
    def create_channel(self): return PushChannel()
assert PushNotifier().notify("x", " yo ") == "push to x: yo"
try:
    Notifier()
    assert False
except TypeError:
    pass
```

```stdout
email to ada: Build passed
sms to ada: Build passed
```

### Abstract Factory

**Problem.** A form supports a light and a dark theme. Every widget repeats the theme check, and it's easy to mix a light button with a dark checkbox by mistake.

```py
def build_form(theme):
    button = LightButton("OK") if theme == "light" else DarkButton("OK")
    checkbox = LightCheckbox("Remember me") if theme == "light" else DarkCheckbox("Remember me")
    # one forgotten check = a dark checkbox on a light form
```

**Task.** Create whole **families** of widgets that always match, and let the form code work with any family without knowing the concrete classes.

**Idea.** An Abstract Factory is an object with one creation method **per product** (`create_button`, `create_checkbox`). Each concrete factory (`LightThemeFactory`, `DarkThemeFactory`) creates products of **one family**. The client gets a factory once, at startup, and from then on can't mix families.

**Steps.**
1. Define the abstract products: `Button`, `Checkbox`.
2. Write one concrete product per family: `LightButton`, `DarkButton`, `LightCheckbox`, `DarkCheckbox`.
3. Define `UIFactory` with `create_button(label)` and `create_checkbox(label)`, and one concrete factory per family.
4. The client (`build_form`) receives a factory and only calls its methods. The theme is chosen in a single place.

```python
from abc import ABC, abstractmethod


class Button(ABC):
    def __init__(self, label: str):
        self.label = label

    @abstractmethod
    def render(self) -> str: ...


class Checkbox(ABC):
    def __init__(self, label: str):
        self.label = label

    @abstractmethod
    def render(self) -> str: ...


class LightButton(Button):
    def render(self) -> str:
        return f"light button: {self.label}"


class DarkButton(Button):
    def render(self) -> str:
        return f"dark button: {self.label}"


class LightCheckbox(Checkbox):
    def render(self) -> str:
        return f"light checkbox: {self.label}"


class DarkCheckbox(Checkbox):
    def render(self) -> str:
        return f"dark checkbox: {self.label}"


class UIFactory(ABC):
    @abstractmethod
    def create_button(self, label: str) -> Button: ...

    @abstractmethod
    def create_checkbox(self, label: str) -> Checkbox: ...


class LightThemeFactory(UIFactory):
    def create_button(self, label: str) -> Button:
        return LightButton(label)

    def create_checkbox(self, label: str) -> Checkbox:
        return LightCheckbox(label)


class DarkThemeFactory(UIFactory):
    def create_button(self, label: str) -> Button:
        return DarkButton(label)

    def create_checkbox(self, label: str) -> Checkbox:
        return DarkCheckbox(label)


def build_form(factory: UIFactory) -> list[str]:
    # works with any family and can't mix them
    return [factory.create_button("OK").render(), factory.create_checkbox("Remember me").render()]


FACTORIES = {"light": LightThemeFactory, "dark": DarkThemeFactory}

if __name__ == "__main__":
    for theme in ("light", "dark"):
        print(build_form(FACTORIES[theme]()))
```

**When to use.**
- Code must create several related objects that have to be used together (UI themes, database drivers with connection + cursor + dialect, cloud providers with storage + queue).
- You want to switch the whole family in one place (config, tests).

**Watch out.**
- Adding a new **family** is easy (one factory + its products). Adding a new **product kind** (say, a `Slider`) means changing `UIFactory` and every concrete factory. Choose this pattern when the product kinds are stable.
- Pick the factory once, at the edge of the program (`FACTORIES[theme]()`), and pass it in. Don't scatter the theme check again.
- In Python a factory can also be a simple object or module with the right functions. The ABC just makes the contract explicit.

```test
assert build_form(LightThemeFactory()) == ["light button: OK", "light checkbox: Remember me"]
assert build_form(DarkThemeFactory()) == ["dark button: OK", "dark checkbox: Remember me"]
f = DarkThemeFactory()
assert isinstance(f.create_button("x"), Button) and isinstance(f.create_checkbox("x"), DarkCheckbox)
class ContrastButton(Button):
    def render(self): return f"CONTRAST BUTTON: {self.label.upper()}"
class ContrastCheckbox(Checkbox):
    def render(self): return f"CONTRAST CHECKBOX: {self.label.upper()}"
class ContrastFactory(UIFactory):
    def create_button(self, label): return ContrastButton(label)
    def create_checkbox(self, label): return ContrastCheckbox(label)
assert build_form(ContrastFactory()) == ["CONTRAST BUTTON: OK", "CONTRAST CHECKBOX: REMEMBER ME"]
```

```stdout
['light button: OK', 'light checkbox: Remember me']
['dark button: OK', 'dark checkbox: Remember me']
```

### Builder

**Problem.** An HTTP request object has many optional parts. The constructor call is unreadable, the defaults are unclear, and nothing checks invalid combinations.

```py
req = Request("POST", "https://api.example.com/users", {"Content-Type": "application/json"},
              {"notify": "yes"}, '{"name": "Ada"}', 5, 3, True, None)
# which argument is which? what are the defaults? who stops a GET with a body?
```

**Task.** Build a request **step by step** with readable, chainable calls, sensible defaults, and validation when the request is finished. The result must be immutable.

**Idea.** A Builder separates **constructing** a complex object from the object itself. It collects the parts through small methods (`method()`, `header()`, `param()`, `json_body()`, `timeout()`), each returning `self` so calls chain. `build()` checks the whole configuration once and returns the final, immutable object.

**Steps.**
1. Make `Request` a frozen dataclass (the product).
2. `RequestBuilder.__init__` takes the required part (the URL) and sets defaults for the rest.
3. Each setter stores one part, validates what it can locally, and returns `self`.
4. `build()` checks rules that involve several parts (no body on `GET`/`HEAD`), encodes the query string, copies the mutable parts, and returns the `Request`.

```python
import json
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlencode


@dataclass(frozen=True)
class Request:
    method: str
    url: str
    headers: dict
    body: Optional[str]
    timeout: float


class RequestBuilder:
    def __init__(self, url: str):
        self._url = url
        self._method = "GET"
        self._headers: dict[str, str] = {}
        self._params: dict[str, str] = {}
        self._body: Optional[str] = None
        self._timeout = 10.0

    def method(self, method: str) -> "RequestBuilder":
        self._method = method.upper()
        return self

    def header(self, name: str, value: str) -> "RequestBuilder":
        self._headers[name] = value
        return self

    def param(self, name: str, value) -> "RequestBuilder":
        self._params[name] = str(value)
        return self

    def json_body(self, data) -> "RequestBuilder":
        self._body = json.dumps(data)
        self._headers["Content-Type"] = "application/json"
        return self

    def timeout(self, seconds: float) -> "RequestBuilder":
        if seconds <= 0:
            raise ValueError("timeout must be positive")
        self._timeout = seconds
        return self

    def build(self) -> Request:
        if self._body is not None and self._method in ("GET", "HEAD"):
            raise ValueError(f"{self._method} request cannot have a body")
        url = self._url + ("?" + urlencode(self._params) if self._params else "")
        # copy the dict so later builder calls can't change an already built request
        return Request(self._method, url, dict(self._headers), self._body, self._timeout)


if __name__ == "__main__":
    req = (RequestBuilder("https://api.example.com/users")
           .method("post")
           .param("notify", "yes")
           .json_body({"name": "Ada"})
           .timeout(5)
           .build())
    print(req.method, req.url)
    print(req.headers, req.body, req.timeout)
```

**When to use.**
- An object has many optional parts, or must be assembled in steps (queries, requests, documents, test data).
- Validation depends on several parts together, so it can only happen at the end.
- The same building steps should produce different representations (for example a builder that outputs SQL and another that outputs a description).

**Watch out.**
- In Python, keyword arguments with defaults (`Request(url, method="POST", timeout=5)`) or a dataclass often replace a builder. Use a builder when there are **steps**, **validation across fields**, or **repeated additions** (many headers, many params).
- Each step must `return self`, otherwise chaining fails with `AttributeError: 'NoneType' object has no attribute …`.
- Copy mutable state in `build()`. Otherwise reusing the builder silently changes objects you already built.
- Real-world examples: SQLAlchemy's `select(...).where(...).order_by(...)`, and `pathlib` / `str` method chains in a lighter form.

```test
r = RequestBuilder("http://x").build()
assert (r.method, r.url, r.headers, r.body, r.timeout) == ("GET", "http://x", {}, None, 10.0)
r = RequestBuilder("http://x").param("q", "a b").param("page", 2).header("A", "1").build()
assert r.url == "http://x?q=a+b&page=2" and r.headers == {"A": "1"}
try:
    RequestBuilder("http://x").json_body({}).build()
    assert False
except ValueError:
    pass
try:
    RequestBuilder("http://x").timeout(0)
    assert False
except ValueError:
    pass
b = RequestBuilder("http://x").method("put").header("A", "1")
first = b.build()
b.header("B", "2")
second = b.build()
assert first.headers == {"A": "1"} and second.headers == {"A": "1", "B": "2"}
```

```stdout
POST https://api.example.com/users?notify=yes
{'Content-Type': 'application/json'} {"name": "Ada"} 5
```

### Prototype

**Problem.** Building a configured monster is slow (attacks and stats come from disk). To make a stronger variant, the code repeats the whole slow setup and then changes two fields.

```py
def make_orc_chief():
    orc = Monster("Orc", 30)
    orc.attacks = load_attacks_from_disk("orc")   # slow
    orc.stats = compute_stats("orc")              # slow
    orc.name, orc.hp = "Orc Chief", 90
    return orc
```

**Task.** Create new objects by **copying** a ready-made prototype and changing only what differs. Copies must be fully independent: changing a copy's list must never change the prototype.

**Idea.** Prototype creates objects by **cloning** an existing instance instead of building from scratch. The object knows how to copy itself (`clone()`). A registry keeps named prototypes, so callers ask for `"orc"` without knowing how it was set up. In Python, `copy.deepcopy` does the deep clone, and `dataclasses.replace` applies changes while checking field names.

**Steps.**
1. Make `Monster` a dataclass with mutable fields (`attacks`, `stats`).
2. `clone(**changes)`: deep-copy `self` first (so lists and dicts are not shared), then `replace(...)` the changed fields.
3. `MonsterRegistry` stores prototypes by key. `create(key, **changes)` clones the stored one.
4. Unknown keys raise a clear `KeyError`. Unknown fields raise `TypeError` from `replace`.

```python
import copy
from dataclasses import dataclass, field, replace


@dataclass
class Monster:
    name: str
    hp: int
    attacks: list[str] = field(default_factory=list)
    stats: dict[str, int] = field(default_factory=dict)

    def clone(self, **changes) -> "Monster":
        # deep copy first so the clone never shares lists or dicts with the prototype
        return replace(copy.deepcopy(self), **changes)


class MonsterRegistry:
    def __init__(self):
        self._prototypes: dict[str, Monster] = {}

    def register(self, key: str, prototype: Monster) -> None:
        self._prototypes[key] = prototype

    def create(self, key: str, **changes) -> Monster:
        if key not in self._prototypes:
            raise KeyError(f"no prototype {key!r}")
        return self._prototypes[key].clone(**changes)


if __name__ == "__main__":
    registry = MonsterRegistry()
    registry.register("orc", Monster("Orc", 30, ["club"], {"str": 8}))
    boss = registry.create("orc", name="Orc Chief", hp=90)
    boss.attacks.append("war cry")
    print(boss)
    print(registry.create("orc"))
```

**When to use.**
- Creating an object is expensive (I/O, heavy computation), but copying it is cheap.
- You have a few preset configurations and want many slightly different objects from them.
- Code must copy objects without depending on their concrete classes.

**Watch out.**
- **Shallow vs deep copy**: `copy.copy` copies the outer object but **shares** the inner lists and dicts. Appending to the clone's list changes the prototype too. Use `copy.deepcopy` for nested mutable state.
- `deepcopy` handles cycles (it keeps a memo of copied objects), but it can be slow or copy too much (open files, locks, sockets can't be copied). Customize it with `__deepcopy__` / `__copy__` when needed.
- Don't put objects in the prototype that must stay shared (a database connection). Inject those after cloning.

```test
proto = Monster("Goblin", 10, ["stab"], {"agi": 5})
c = proto.clone(hp=12)
assert c is not proto and c.hp == 12 and proto.hp == 10
c.attacks.append("run")
c.stats["agi"] = 9
assert proto.attacks == ["stab"] and proto.stats == {"agi": 5}
shallow = copy.copy(proto)
shallow.attacks.append("oops")
assert proto.attacks == ["stab", "oops"]
try:
    proto.clone(speed=3)
    assert False
except TypeError:
    pass
reg = MonsterRegistry()
reg.register("g", Monster("G", 1))
assert reg.create("g") == Monster("G", 1) and reg.create("g") is not reg.create("g")
try:
    reg.create("dragon")
    assert False
except KeyError:
    pass
```

```stdout
Monster(name='Orc Chief', hp=90, attacks=['club', 'war cry'], stats={'str': 8})
Monster(name='Orc', hp=30, attacks=['club'], stats={'str': 8})
```
