# aocparser

This package is a simple parser for puzzle inputs such as the Advent of Code input files.

## Grammar

The grammar consists of four basic constructs:

### Literals

Literals are matched exactly. Characters with special meaning, i.e. `[`, `]`, `{`, `}`, `<`, `>`, and `|` must be escaped with a backtick (`` ` ``).

> ``foo`|bar`` matches `foo|bar`.

### Value elements

Value elements (i.e., elements that should be parsed into a value) are denoted by curly brackets (`{` and `}`), with the type given after a colon (`:`):

> `{foo:i}` matches `42` and parses into `{'foo': 42}`.

The name of the value element is optional. If no name is given, the value is stored with its index as its key.
If none of the value elements in the container element are named, the container element is parsed into a list.
Otherwise, it is parsed into a dict.

> `{i}{i}` matches `42 43` and parses into `[42, 43]`

> `{i}{bar:i}` matches `42 43` and parses into `{0: 42, 'bar': 43}`.

#### Defined types

Currently, the following types are defined:
- `i`: integer
- `w`: word (i.e., an alphanumeric string without whitespace)
- `n`: name (i.e., a word not starting with a number)
- `il`: list of integers
- `wl`: list of words
- `nl`: list of names

### Container elements

Container elements (i.e., elements that should be parsed into a list or a dict) are denoted by square brackets (`[` and `]`), with the 'join string' given after a pipe (`|`):

> `[{i}|,]` matches `42,43` and parses into `[42, 43]`.

The join string is optional. If no join string is given, it will default to (an arbitrary amount of) spaces.

> `[{i}]` matches `42 43` and parses into `[42, 43]`.

#### Dicts

If a value element inside the container has the name `key`, the container is parsed into a dict, with the value of the `key` element as the key.

> `[{key:w} = {val:i}|\n]` matches
> ```ini
> foo = 42
> bar = 43
> ```
> and parses into
> ```python
> {'foo': {'key': 'foo', 'val': 42},
>  'bar': {'key': 'bar', 'val': 43}}
> ```

### Choice elements

Choice elements (i.e., elements that should be parsed into one of two values) are denoted by angle brackets (`<` and `>`), with the choices separated by a pipe (`|`).
To distinguish the choices, they need to be named, with the name given before a colon (`:`).

> `<num:{i}|word:{w}>` matches `42` and parses into `namespace(num=42, word=None)`, and matches `foo` and parses into `namespace(num=None, word='foo')`.
>
> `namespace` is a simple class that stores the given attributes, i.e. `namespace(num=42, word=None).num == 42`.


## Examples

### 2023/day04

```python
from aocparser import parse

example = """\
Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53
Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19"""

spec = "[Card {key:i}: {p1:il} `| {p2:il}|\n]"

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
{vals:[{il}|\n]}|\n\n]}"""

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

[{key:w} = ({L:w}, {R:w})|\n]"""

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
from types import SimpleNamespace as namespace
from aocparser import parse

example = """\
mask = 00
mem[1] = 1
mask = 01
mem[2] = 2"""

spec = "[<mask:mask = {w}|mem:mem`[{i}`] = {i}>|\n]"

assert parsed == [
    namespace(mask="00", mem=None),
    namespace(mem=[1, 1], mask=None),
    namespace(mask="01", mem=None),
    namespace(mem=[2, 2], mask=None),
]
```