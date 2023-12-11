from collections import Counter


class GrammarConstructor:
    def __init__(self):
        self.rules = dict()
        self.index_by_tag = Counter()

    def add_rule(self, tag, rule):
        rule_index = self.index_by_tag[tag]
        self.index_by_tag[tag] += 1

        if tag == "start":
            assert rule_index == 0, "Only one start rule is allowed"
            rule_name = "start"
        else:
            rule_name = f"{tag}{rule_index}"

        self.rules[rule_name] = rule

        return rule_name

    def construct(self):
        grammar = "\n".join(
            f"{rule_name}: {rule}" for rule_name, rule in self.rules.items()
        )

        grammar += """
ALPHANUM: LETTER | DIGIT
ALPHANUMWORD: ALPHANUM+

%import common.INT
%import common.WORD
%import common.CNAME
%import common.LETTER
%import common.DIGIT
%ignore " "\
"""

        return grammar
