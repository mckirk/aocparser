from abc import ABC, abstractmethod
import json

from aocparser.grammar_constructor import GrammarConstructor


class DSLElement(ABC):
    def __init__(
        self,
        tag: str,
        attributes: dict,
        content: list,
        grammar_constructor: GrammarConstructor,
    ):
        self.tag = tag
        self.attributes = attributes
        self.content = content

        self.rule_name: str | None = None
        self.rule: str | None = None

        self.create_rule(grammar_constructor)

        assert self.rule_name is not None

    def get_name(self, *args):
        return self.attributes.get("n")

    def get_inner_elements(self):
        return [c for c in self.content if isinstance(c, DSLElement)]

    def register_transforms(self, transformer, override_rule_name: str | None = None):
        transformer.__setattr__(
            override_rule_name or self.rule_name,
            lambda *args: (self.get_name(*args), self.transform(*args)),
        )

        for c in self.get_inner_elements():
            c.register_transforms(transformer)

    @abstractmethod
    def create_rule(self, grammar_constructor: GrammarConstructor):
        ...

    @abstractmethod
    def transform(self, *args):
        ...


class SequenceElement(DSLElement):
    def create_rule(self, grammar_constructor):
        rule_parts = []
        for c in self.content:
            if isinstance(c, DSLElement):
                rule_parts.append(c.rule_name)
            else:
                rule_parts.append(f"{json.dumps(c)}")

        self.rule = f"{' '.join(rule_parts)}"
        self.rule_name = grammar_constructor.add_rule(self.tag, self.rule)

    def get_name(self, *args):
        elems = args[0]
        keys = [e[0] for e in elems]
        if "key" in keys:
            return elems[keys.index("key")][1]
        else:
            return super().get_name(*args)

    def transform(self, *args):
        elems = args[0]
        keys = [e[0] for e in elems]
        vals = [e[1] for e in elems]

        if any(k is not None for k in keys):
            return {(k if k is not None else i): v for i, (k, v) in enumerate(elems)}

        if len(vals) == 1:
            return vals[0]
        else:
            return vals


class ListElement(DSLElement):
    def __init__(self, tag, attributes, content, grammar_constructor):
        self.inner = SequenceElement(
            tag + "_inner", dict(), content, grammar_constructor
        )
        super().__init__(tag, attributes, content, grammar_constructor)

    def get_inner_elements(self):
        return [self.inner]

    def create_rule(self, grammar_constructor):
        inner_rule_name = self.inner.rule_name

        join = self.attributes.get("join")
        if join is None:
            self.rule = f"{inner_rule_name}*"
        else:
            self.rule = f"{inner_rule_name} ({json.dumps(join)} {inner_rule_name})*"
        self.rule_name = grammar_constructor.add_rule(self.tag, self.rule)

    def transform(self, *args):
        elems = args[0]
        keys = [e[0] for e in elems]

        if any(k is not None for k in keys):
            res = {(k if k is not None else i): v for i, (k, v) in enumerate(elems)}
        else:
            res = [v for k, v in elems]

        return res


def build_terminal_elem(terminal, transform_f=None):
    if not transform_f:
        transform_f = str

    class TerminalElement(DSLElement):
        def create_rule(self, grammar_constructor):
            self.rule_name = grammar_constructor.add_rule(self.tag, terminal)

        def transform(self, *args):
            return transform_f(args[0][0])

    return TerminalElement


def build_list_elem(inner_class):
    def inner(tag, attributes, content, grammar_constructor):
        return ListElement(
            tag,
            attributes,
            [inner_class(tag + "_inner", dict(), [], grammar_constructor)],
            grammar_constructor,
        )

    return inner


IntElement = build_terminal_elem("INT", int)
WordElement = build_terminal_elem("ALPHANUMWORD")
NameElement = build_terminal_elem("CNAME")


TAG_TO_CLASS = {
    "elem": ListElement,
    "int": IntElement,
    "word": WordElement,
    "name": NameElement,
    "intlist": build_list_elem(IntElement),
    "wordlist": build_list_elem(WordElement),
    "namelist": build_list_elem(NameElement),
}
