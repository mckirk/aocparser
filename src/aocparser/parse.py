from lark import Lark, Transformer

import aocparser.dsl as dsl


def parse(spec, input, return_types_by_name: dict = None):
    transformer, dsl_parser = dsl.get_parser(return_types_by_name)
    parsed_dsl = dsl_parser.parse(spec)

    constructed_grammar = transformer.grammar_constructor.construct()

    constructed_transformer = Transformer()
    parsed_dsl.register_transforms(constructed_transformer)

    constructed_parser = Lark(
        constructed_grammar, parser="lalr", transformer=constructed_transformer
    )

    parsed_example = constructed_parser.parse(input)
    return parsed_example[1]
