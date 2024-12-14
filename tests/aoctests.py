import unittest
from aocparser import parse


class TestAocParser(unittest.TestCase):
    def test_simple(self):
        example = """\
Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53
Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19"""

        spec = "[Card {key:i}: {p1:il} `| {p2:il}]"

        parsed = parse(spec, example)

        expected = {
            1: {
                "key": 1,
                "p1": [41, 48, 83, 86, 17],
                "p2": [83, 86, 6, 31, 17, 9, 48, 53],
            },
            2: {
                "key": 2,
                "p1": [13, 32, 20, 16, 61],
                "p2": [61, 30, 68, 82, 17, 32, 24, 19],
            },
        }

        self.assertEqual(parsed, expected)

    def test_nested(self):
        example = """\
seeds: 79 14 55 13

seed-to-soil map:
50 98 2
52 50 48"""

        spec = """\
seeds: {seeds:il}

{maps:[{key:w}-to-{to:w} map:
{vals:[{il}|\n]}]}"""

        parsed = parse(spec, example)

        expected = {
            "maps": {
                "seed": {
                    "key": "seed",
                    "to": "soil",
                    "vals": [[50, 98, 2], [52, 50, 48]],
                }
            },
            "seeds": [79, 14, 55, 13],
        }

        self.assertEqual(parsed, expected)

    def test_simple2(self):
        example = """\
RL

AAA = (BBB, CCC)
BBB = (DDD, EEE)"""

        spec = """\
{w}

[{key:w} = ({L:w}, {R:w})]"""

        parsed = parse(spec, example)

        expected = [
            "RL",
            {
                "AAA": {"L": "BBB", "R": "CCC", "key": "AAA"},
                "BBB": {"L": "DDD", "R": "EEE", "key": "BBB"},
            },
        ]

        self.assertEqual(parsed, expected)

    def test_choice(self):
        spec = "[<mask:mask = {w}|mem:mem`[{addr:i}`] = {val:i}>]"

        inp = """\
mask = 00
mem[1] = 1
mask = 01
mem[2] = 2"""

        parsed = parse(spec, inp)

        expected = [
            {"mask": "00", "mem": None},
            {"mask": None, "mem": {"addr": 1, "val": 1}},
            {"mask": "01", "mem": None},
            {"mask": None, "mem": {"addr": 2, "val": 2}},
        ]

        self.assertEqual(parsed, expected)
        self.assertEqual(parsed[0]["mask"], "00")
        self.assertEqual(parsed[1]["mem"]["addr"], 1)

    def test_choice_lifting(self):
        spec = "[<set:{n:w}={v:i}|minus:{n:w}-|plus:{n:w}+>|,]"

        inp = "a=1,b=2,c-,d+"

        parsed = parse(spec, inp)

        expected = [
            {"minus": None, "n": "a", "plus": None, "set": {"n": "a", "v": 1}},
            {"minus": None, "n": "b", "plus": None, "set": {"n": "b", "v": 2}},
            {"minus": {"n": "c"}, "n": "c", "plus": None, "set": None},
            {"minus": None, "n": "d", "plus": {"n": "d"}, "set": None},
        ]

        self.assertEqual(parsed, expected)
        self.assertEqual(parsed[0]["n"], "a")
        self.assertEqual(parsed[2]["n"], "c")

    def test_direct_dict(self):
        spec = "[{key:w}={i}|,]"
        inp = "a=1,b=2,c=3"
        parsed = parse(spec, inp)
        expected = {"a": 1, "b": 2, "c": 3}
        self.assertEqual(parsed, expected)

    def test_signed_int(self):
        spec = "p={si},{si} v={si},{si}"
        inp = "p=0,4 v=3,-3"
        parsed = parse(spec, inp)
        expected = [0, 4, 3, -3]
        self.assertEqual(parsed, expected)


if __name__ == "__main__":
    unittest.main()
