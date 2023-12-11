# aocparser

This package is a simple parser for puzzle inputs such as the Advent of Code input files.

# Examples

## 2023/day04

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

## 2023/day05

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

## 2023/day08

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

## 2020/day14

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