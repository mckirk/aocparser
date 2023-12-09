import ast
from dataclasses import dataclass, field
import re
from typing import Type
from lark import Lark, Token, Transformer, v_args

from aocparser.grammar_constructor import GrammarConstructor
from aocparser.elements import TAG_TO_CLASS, DSLElement, DSLMultiElement, ContainerElement, SequenceElement


dsl_grammar = """
start: sequence

sequence: (element | multi_element | TEXT)*

element: "{" CNAME (":" (CNAME | multi_element))? "}"
multi_element: "[" sequence "]" | "[" sequence "|" TEXT "]"

TEXT: /(?:`.|[^\[{}\]|`])+/

%ignore " "
%import common.CNAME
"""


def interpret_as_literal(value):
    return ast.literal_eval(value)


def unescape(text):
    return re.sub(r"`(.)", r"\1", text)


@dataclass
class DSLTransformer(Transformer):
    grammar_constructor: GrammarConstructor = field(default_factory=GrammarConstructor)

    def element(self, args):
        if len(args) == 1:
            tag = args[0]
            name = None
        else:
            name, tag = args

        if isinstance(tag, str):
            class_: Type[DSLElement] = TAG_TO_CLASS[tag]
            return class_(tag=tag, name=name, grammar_constructor=self.grammar_constructor)
        else:
            assert isinstance(tag, DSLMultiElement)
            tag.name = name
            return tag
    
    def multi_element(self, args):
        if len(args) == 2:
            content, join = args
        else:
            content, join = args[0], None

        return ContainerElement(tag="container", name=None, join=join, content=content, grammar_constructor=self.grammar_constructor)

    def sequence(self, items):
        return list(items)

    def start(self, items):
        return SequenceElement(tag="start", name=None, content=items[0], grammar_constructor=self.grammar_constructor)

    TEXT = lambda self, s: unescape(str(s))
    CNAME = str


def get_parser():
    transformer = DSLTransformer()
    return transformer, Lark(dsl_grammar, parser="lalr", transformer=transformer)
