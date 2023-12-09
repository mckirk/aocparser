from pprint import pprint
from aocparser import parse


def test1():
    example = """\
Card 1: 1 2 3 4 5 6 7 8 9 10 | 11 12 13 14 15 16 17 18 19 20
Card 2: 21 22 23 24 25 26 27 28 29 30 | 31 32 33 34 35 36 37 38 39 40"""

    spec = "[Card {key:i}: {p1:il} `| {p2:il}|\n]"

    parsed = parse(example, spec)

    pprint(parsed)

    assert parsed == {
        1: {
            "key": 1,
            "p1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "p2": [11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
        },
        2: {
            "key": 2,
            "p1": [21, 22, 23, 24, 25, 26, 27, 28, 29, 30],
            "p2": [31, 32, 33, 34, 35, 36, 37, 38, 39, 40],
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

    parsed = parse(example, spec)

    pprint(parsed)

    assert parsed == {
        "maps": {
            "seed": {"key": "seed", "to": "soil", "vals": [[50, 98, 2], [52, 50, 48]]}
        },
        "seeds": [79, 14, 55, 13],
    }


def main():
    test1()
    test2()


if __name__ == "__main__":
    main()
