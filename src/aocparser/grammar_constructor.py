from collections import Counter


class GrammarConstructor:
    def __init__(self, return_types_by_name: dict | None):
        self.rules = dict()
        self.index_by_tag = Counter()
        self.return_types_by_name = return_types_by_name

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

    def add_return_type(self, name, type):
        if self.return_types_by_name is not None:
            self.return_types_by_name[name] = type

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
