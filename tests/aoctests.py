from pprint import pprint
from aocparser import parse


def test1():
    example = """\
Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53
Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19"""

    spec = "[Card {key:i}: {p1:il} `| {p2:il}|\n]"

    parsed = parse(spec, example)

    pprint(parsed)

    assert parsed == {
        1: {"key": 1, "p1": [41, 48, 83, 86, 17], "p2": [83, 86, 6, 31, 17, 9, 48, 53]},
        2: {
            "key": 2,
            "p1": [13, 32, 20, 16, 61],
            "p2": [61, 30, 68, 82, 17, 32, 24, 19],
        },
    }


def test2():
    example = """\
seeds: 79 14 55 13

seed-to-soil map:
50 98 2
52 50 48"""

    spec = """\
seeds: {seeds:il}

{maps:[{key:w}-to-{to:w} map:
{vals:[{il}|\n]}|\n\n]}"""

    parsed = parse(spec, example)

    pprint(parsed)

    assert parsed == {
        "maps": {
            "seed": {"key": "seed", "to": "soil", "vals": [[50, 98, 2], [52, 50, 48]]}
        },
        "seeds": [79, 14, 55, 13],
    }


def test3():
    example = """\
RL

AAA = (BBB, CCC)
BBB = (DDD, EEE)"""

    spec = """\
{w}

[{key:w} = ({L:w}, {R:w})|\n]"""

    parsed = parse(spec, example)

    pprint(parsed)

    assert parsed == [
        "RL",
        {
            "AAA": {"L": "BBB", "R": "CCC", "key": "AAA"},
            "BBB": {"L": "DDD", "R": "EEE", "key": "BBB"},
        },
    ]


def test4():
    spec = """\
[<mask:mask = {w}|mem:mem`[{i}`] = {i}>|\n]"""

    inp = """\
mask = 00
mem[1] = 1
mask = 01
mem[2] = 2"""

    parsed = parse(spec, inp)

    pprint(parsed)

    assert parsed == [("mask", "00"), ("mem", [1, 1]), ("mask", "01"), ("mem", [2, 2])]


def main():
    test1()
    test2()
    test3()
    test4()


if __name__ == "__main__":
    main()
