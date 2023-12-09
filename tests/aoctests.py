from pprint import pprint
from aocparser import parse


def test1():
    example = """\
Card 1: 1 2 3 4 5 6 7 8 9 10 | 11 12 13 14 15 16 17 18 19 20
Card 2: 21 22 23 24 25 26 27 28 29 30 | 31 32 33 34 35 36 37 38 39 40"""

    dsl_input = "<elem join='\\n'>Card <int n='key'/>: <intlist n='part1'/> | <intlist n='part2'/></elem>"

    parsed = parse(example, dsl_input)

    pprint(parsed)

    assert parsed == {
        1: {
            "key": 1,
            "part1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "part2": [11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
        },
        2: {
            "key": 2,
            "part1": [21, 22, 23, 24, 25, 26, 27, 28, 29, 30],
            "part2": [31, 32, 33, 34, 35, 36, 37, 38, 39, 40],
        },
    }


def test2():
    example = """\
seeds: 79 14 55 13

seed-to-soil map:
50 98 2
52 50 48"""

    dsl_input = """\
seeds: <intlist n='seeds'/>

<elem join='\\n\\n' n='maps'><name n='key'/>-to-<word n='to'/> map:
<elem join='\\n' n='vals'><intlist/></elem></elem>"""

    parsed = parse(example, dsl_input)

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
