from lark import Lark, Transformer

import aocparser.dsl as dsl


def parse(spec, input):
    transformer, dsl_parser = dsl.get_parser()
    parsed_dsl = dsl_parser.parse(spec)

    constructed_grammar = transformer.grammar_constructor.construct()

    constructed_transformer = Transformer()
    parsed_dsl.register_transforms(constructed_transformer)

    constructed_parser = Lark(
        constructed_grammar, parser="earley"
    )

    parse_tree = constructed_parser.parse(input)

    return constructed_transformer.transform(parse_tree)[1]
