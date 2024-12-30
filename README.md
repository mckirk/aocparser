# aocparser

This package is a simple parser for puzzle inputs such as the Advent of Code input files.

## Grammar

The grammar consists of four basic constructs:

### Literals

Literals are matched exactly. Characters with special meaning, i.e. `[`, `]`, `{`, `}`, `<`, `>`, and `|` must be escaped with a backslash (`` \ ``).

> ``foo\|bar`` matches `foo|bar`.

### Value elements

Value elements (i.e., elements that should be parsed into a value) are denoted by curly brackets (`{` and `}`), with the type given after a colon (`:`):

> `{foo:i}` matches `42` and parses into `{'foo': 42}`.

The name of the value element is optional. If no name is given, the value is stored with its index as its key.
If none of the value elements in the container element are named, the container element is parsed into a list.
Otherwise, it is parsed into a dict.

> `{i} {i}` matches `42 43` and parses into `[42, 43]`

> `{i} {bar:i}` matches `42 43` and parses into `{0: 42, 'bar': 43}`.

#### Defined types

Currently, the following types are defined:
- `i`: integer
- `si`: signed integer (optionally starting with a +/-)
- `w`: word (i.e., an alphanumeric string without whitespace)
- `n`: name (i.e., a word not starting with a number)
- `il`: list of integers, separated by 'inline whitespace' (i.e., non-linebreak whitespace)
- `sil`: list of signed integers
- `wl`: list of words
- `nl`: list of names

### Container elements

Container elements (i.e., elements that should be parsed into a list or a dict) are denoted by square brackets (`[` and `]`), with the 'join string' given after a pipe (`|`):

> `[{i}|,]` matches `42,43` and parses into `[42, 43]`.

The join string is optional. If no join string is given, it will default to (an arbitrary amount of) whitespace (i.e., spaces, tabs, newlines).

> `[{i}]` matches `42 43` and parses into `[42, 43]`.

> `[{il}]` matches
> ```
> 42 43
> 44 45
> ```
> and parses into `[[42, 43], [44, 45]]`.

#### Dicts

If a value element inside a container has the name `key`, the container is parsed into a dict, with the value of the `key` element as the key.

> `[{key:w} = {val:i}]` matches
> ```ini
> foo = 42
> bar = 43
> ```
> and parses into
> ```python
> {'foo': {'key': 'foo', 'val': 42},
>  'bar': {'key': 'bar', 'val': 43}}
> ```

If a container has two child elements, one 'key' element and one unnamed element, the unnamed element gets returned directly as the value:

> `[{key:w} = {i}]` matches
> ```ini
> foo = 42
> bar = 43
> ```
> and parses into
> ```python
> {'foo': 42,
>  'bar': 43}
> ```

### Choice elements

Choice elements (i.e., elements that should be parsed into one of multiple options) are denoted by angle brackets (`<` and `>`), with the choices separated by a pipe (`|`).
To distinguish the choices, they need to be named, with the name given before a colon (`:`).

> `<num:{i}|word:{w}>`
> - matches `42` and parses into `dict(num=42, word=None)`
> - matches `foo` and parses into `dict(word='foo', num=None)`

If all choices contain an element with the same name, that element is lifted to the result of the choice element as well.

> `<inc:{n:w}++|dec:{n:w}-->`
> - matches `a++` and parses into `dict(n='a', inc={'n': 'a'}, dec=None)`
> - matches `a--` and parses into `dict(n='a', dec={'n': 'a'}, inc=None)`.

## Returned 'dict' type

The returned dictionaries are actually `NamespaceDict`s, which subclass dictionaries to also allow access to the values as attributes.
This means that `parsed['foo']` is equivalent to `parsed.foo`.


## Examples

### 2023/day04

```python
from aocparser import parse

example = """\
Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53
Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19"""

spec = r"[Card {key:i}: {p1:il} \| {p2:il}]"

assert parse(spec, example) == {
    1: {"key": 1,
        "p1": [41, 48, 83, 86, 17],
        "p2": [83, 86, 6, 31, 17, 9, 48, 53]},
    2: {
        "key": 2,
        "p1": [13, 32, 20, 16, 61],
        "p2": [61, 30, 68, 82, 17, 32, 24, 19],
    },
}
```

### 2023/day05

```python
from aocparser import parse

example = """\
seeds: 79 14 55 13

seed-to-soil map:
50 98 2
52 50 48"""

spec = """\
seeds: {seeds:il}

{maps:[{key:w}-to-{to:w} map:
{vals:[{il}]}]}"""

assert parse(spec, example) == {
    "maps": {
        "seed": {"key": "seed", "to": "soil", "vals": [[50, 98, 2], [52, 50, 48]]}
    },
    "seeds": [79, 14, 55, 13],
}
```

### 2023/day08

```python
from aocparser import parse

example = """\
RL

AAA = (BBB, CCC)
BBB = (DDD, EEE)"""

spec = """\
{w}

[{key:w} = ({L:w}, {R:w})]"""

assert parse(spec, example) == [
    "RL",
    {
        "AAA": {"L": "BBB", "R": "CCC", "key": "AAA"},
        "BBB": {"L": "DDD", "R": "EEE", "key": "BBB"},
    },
]
```

### 2020/day14

```python
from aocparser import parse

example = """\
mask = 00
mem[1] = 1
mask = 01
mem[2] = 2"""

spec = r"[<mask:mask = {w}|mem:mem\[{i}\] = {i}>]"

assert parsed == [
    {"mask": "00", "mem": None},
    {"mask": None, "mem": {"addr": 1, "val": 1}},
    {"mask": "01", "mem": None},
    {"mask": None, "mem": {"addr": 2, "val": 2}},
]

assert parsed[0].mask == "00"
assert parsed[1].mem.addr == 1
```

### 2023/day15

```python
from aocparser import parse

example = "a=1,b=2,c-"

spec = "[<set:{n:w}={v:i}|minus:{n:w}->|,]"

parsed = parse(spec, example)

assert parsed == [
    {"minus": None, "n": "a", "set": {"n": "a", "v": 1}},
    {"minus": None, "n": "b", "set": {"n": "b", "v": 2}},
    {"minus": {"n": "c"}, "n": "c", "set": None},
]

assert parsed[0].n == "a"
assert parsed[2].n == "c"
```

### 2024/day24

```python
from aocparser import parse

example = """\
x00: 1
x01: 1
x02: 1
y00: 0
y01: 1
y02: 0

x00 AND y00 -> z00
x01 XOR y01 -> z01
x02 OR y02 -> z02"""

spec = r"""
[{key:w}: {i}]

[{w} <and_:AND|xor_:XOR|or_:OR> {w} -\> {key:w}]""".strip()

parsed = parse(spec, example)

assert parsed == [
    {"x00": 1, "x01": 1, "x02": 1, "y00": 0, "y01": 1, "y02": 0},
    {
        "z00": {
            0: "x00",
            1: {"and_": True, "or_": None, "xor_": None},
            2: "y00",
            "key": "z00",
        },
        "z01": {
            0: "x01",
            1: {"and_": None, "or_": None, "xor_": True},
            2: "y01",
            "key": "z01",
        },
        "z02": {
            0: "x02",
            1: {"and_": None, "or_": True, "xor_": None},
            2: "y02",
            "key": "z02",
        },
    },
]
```