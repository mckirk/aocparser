import ast
from dataclasses import dataclass, field
from typing import Type
from lark import Lark, Token, Transformer, v_args

from aocparser.grammar_constructor import GrammarConstructor
from aocparser.elements import TAG_TO_CLASS, DSLElement, SequenceElement


dsl_grammar = """
start: (element | TEXT)*

element: "<" TAG_NAME attribute* ">" content "</" TAG_NAME ">" | "<" TAG_NAME attribute* "/>"
content: (element | TEXT)*

attribute: ATTRIBUTE_NAME "=" ATTRIBUTE_VALUE

TAG_NAME: /[a-zA-Z0-9_]+/
ATTRIBUTE_NAME: /[a-zA-Z0-9_]+/
ATTRIBUTE_VALUE: /'[^']*'/
TEXT: /[^<>]+/

%ignore " "
"""


def interpret_as_literal(value):
    return ast.literal_eval(value)


@dataclass
class DSLTransformer(Transformer):
    grammar_constructor: GrammarConstructor = field(default_factory=GrammarConstructor)

    @v_args(inline=True)
    def element(self, tag, *content):
        if content and isinstance(content[-1], Token):
            assert content[-1] == tag, f"Mismatched closing tag: {tag} != {content[-1]}"
            content = content[:-1]

        attributes = {}
        content_list = []

        for item in content:
            if isinstance(item, tuple):
                attributes[item[0]] = item[1]
            else:
                content_list = item

        class_: Type[DSLElement] = TAG_TO_CLASS[tag]

        return class_(tag, attributes, content_list, self.grammar_constructor)

    @v_args(inline=True)
    def attribute(self, name, value):
        # interpret value as a Python literal
        return (str(name), interpret_as_literal(str(value)))

    def content(self, items):
        return list(items)

    def start(self, items):
        return SequenceElement("start", {}, items, self.grammar_constructor)

    TEXT = str


def get_parser():
    transformer = DSLTransformer()
    return transformer, Lark(dsl_grammar, parser="lalr", transformer=transformer)
