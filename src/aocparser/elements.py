from abc import ABC, abstractmethod
from functools import reduce
import json

from aocparser.grammar_constructor import GrammarConstructor
from aocparser.result import NamespaceDict


class DSLElement(ABC):
    def __init__(
        self,
        *,
        tag: str,
        name: str | None,
        grammar_constructor: GrammarConstructor,
    ):
        self.tag = tag
        self.name = name

        self.rule_name: str | None = None
        self.rule: str | None = None

        self.create_rule(grammar_constructor)

        assert self.rule_name is not None

    def get_name(self, *args):
        """Return the key this element should be stored under in the result"""
        return self.name

    def get_inner_elements(self) -> list["DSLElement"]:
        """Return a list of child-elements that also need their transforms registered"""
        return []

    def register_transforms(self, transformer, override_rule_name: str | None = None):
        """Register the transforms for this element and all its children"""
        transformer.__setattr__(
            override_rule_name or self.rule_name,
            lambda *args: (self.get_name(*args), self.transform(*args)),
        )

        for c in self.get_inner_elements():
            c.register_transforms(transformer)

    @abstractmethod
    def create_rule(self, grammar_constructor: GrammarConstructor):
        """Create the rule for this element and register it with the grammar constructor"""
        ...

    @abstractmethod
    def transform(self, *args):
        """Transform the result of the parse into the final result"""
        ...


class DSLMultiElement(DSLElement):
    def __init__(
        self,
        *,
        tag: str,
        name: str | None,
        content: list,
        grammar_constructor: GrammarConstructor,
    ):
        self.content = content
        super().__init__(tag=tag, name=name, grammar_constructor=grammar_constructor)

    def get_inner_elements(self):
        return [c for c in self.content if isinstance(c, DSLElement)]


class SequenceElement(DSLMultiElement):
    def create_rule(self, grammar_constructor):
        """Create a rule that simply concatenates the rules of all child-elements"""
        rule_parts = []
        for c in self.content:
            if isinstance(c, DSLElement):
                rule_parts.append(c.rule_name)
            else:
                rule_parts.append(f"{json.dumps(c)}")

        self.rule = f"{' '.join(rule_parts)}"
        self.rule_name = grammar_constructor.add_rule(self.tag, self.rule)

    def get_name(self, *args):
        """If the sequence has an element of name 'key', use that as the key in the result"""
        elems = args[0]
        keys = [e[0] for e in elems]
        if "key" in keys:
            return elems[keys.index("key")][1]
        else:
            return super().get_name(*args)

    def transform(self, *args):
        """If we have any named child-elements, return a dict; otherwise, return a list (or the only element directly)"""
        elems = args[0]
        keys = [e[0] for e in elems]
        vals = [e[1] for e in elems]

        if any(k is not None for k in keys):
            res = NamespaceDict()
            for i, (k, v) in enumerate(elems):
                if k is not None:
                    res[k] = v
                else:
                    res[i] = v
            return res

        if len(vals) == 1:
            return vals[0]
        else:
            return vals


class ContainerElement(DSLMultiElement):
    def __init__(self, *, tag, name, join, content, grammar_constructor):
        self.inner = SequenceElement(
            tag=tag + "_inner",
            name=None,
            content=content,
            grammar_constructor=grammar_constructor,
        )
        self.join = join
        super().__init__(
            tag=tag, name=name, content=content, grammar_constructor=grammar_constructor
        )

    def get_inner_elements(self):
        return [self.inner]

    def create_rule(self, grammar_constructor):
        """Create a rule that matches the inner rule one or more times, separated by the 'join' argument"""
        inner_rule_name = self.inner.rule_name

        if self.join is None:
            self.rule = f"{inner_rule_name}*"
        else:
            self.rule = (
                f"{inner_rule_name} ({json.dumps(self.join)} {inner_rule_name})*"
            )
        self.rule_name = grammar_constructor.add_rule(self.tag, self.rule)

    def transform(self, *args):
        """
        If we have any named child-elements, return a dict; otherwise, return a list
        Difference from SequenceElement: if there's only one element, we still return a list
        """
        elems = args[0]
        keys = [e[0] for e in elems]

        if any(k is not None for k in keys):
            res = NamespaceDict()
            for i, (k, v) in enumerate(elems):
                if k is not None:
                    res[k] = v
                else:
                    res[i] = v
            return res
        else:
            res = [v for k, v in elems]

        return res


class ChoiceElement(DSLElement):
    def __init__(
        self,
        *,
        tag: str,
        choices: list[SequenceElement],
        grammar_constructor: GrammarConstructor,
    ):
        names = [c.name for c in choices]
        assert len(names) == len(set(names))

        self.choices = choices
        super().__init__(tag=tag, name=None, grammar_constructor=grammar_constructor)

        # find names that are common to both sides (minus the names of the choices themselves)
        inner_names = [set(c.name for c in choice.get_inner_elements()) for choice in choices]
        self.common_names = reduce(lambda a, b: a & b, inner_names) - set(names)

    def get_inner_elements(self):
        return self.choices

    def create_rule(self, grammar_constructor):
        """Create a rule that matches either the left or the right rule"""
        self.rule = " | ".join(c.rule_name for c in self.choices)
        self.rule_name = grammar_constructor.add_rule(self.tag, self.rule)

    def transform(self, *args):
        """Return the result of the left or right rule"""
        t, v = args[0][0]
        other_ts = [c.name for c in self.choices if c.name != t]

        res = NamespaceDict()
        res[t] = v
        for name in other_ts:
            res[name] = None

        for name in self.common_names:
            if isinstance(v, dict) and name in v:
                res[name] = v[name]

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
    def inner(tag, name, grammar_constructor):
        return ContainerElement(
            tag=tag,
            name=name,
            join=None,
            content=[
                inner_class(
                    tag=tag + "_inner",
                    name=None,
                    grammar_constructor=grammar_constructor,
                )
            ],
            grammar_constructor=grammar_constructor,
        )

    return inner


IntElement = build_terminal_elem("INT", int)
WordElement = build_terminal_elem("ALPHANUMWORD")
NameElement = build_terminal_elem("CNAME")


TAG_TO_CLASS = {
    "i": IntElement,
    "w": WordElement,
    "n": NameElement,
    "il": build_list_elem(IntElement),
    "wl": build_list_elem(WordElement),
    "nl": build_list_elem(NameElement),
}
