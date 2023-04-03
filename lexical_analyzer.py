import pyparsing as pp
import pprint
import json

def ignore_comments():
    """Reads source program strips it of any occurring comments
       Returns:
            comment free code for lexical analysis
    """

    with open('main.c', 'r') as sf:
        prog = sf.read()

    single_comment = pp.Literal("//") + pp.restOfLine
    multi_line_comment = pp.nestedExpr("/*", "*/")

    comment = (single_comment | multi_line_comment).suppress()

    return comment.transformString(prog)


symbol_table = dict()


def fill_symbol_table(name):
    symbol_table[name] = {'data type': None,
                          'value': None, 'address': None, 'scope': None}


def look_up(name):
    if name in symbol_table:
       return True
    else:
       return False


def add_to(result):
    if 't_identifier' in result:
        name = result.t_identifier
        if look_up(name) is False:
            fill_symbol_table(name)


def lexeme_grammar():
    """ 
       Returns:
            grammar for subset of C

    """

    key_words = pp.oneOf(['int', 'float', 'continue', 'default', 'switch', 'case', 'goto', 'for', 'printf',
                          'double', 'long', 'unsigned', 'auto', 'if', 'break', 'while', 'else', 'short', 'const',
                          'scanf',
                          'void', 'char', 'static', 'union', 'struct', 'typedef', 'main', 'return',
                          'else if']).setResultsName('t_reserved')

    identifiers = pp.Word(pp.alphas + "_" + pp.alphanums +
                          "_").setResultsName('t_identifier').addParseAction(add_to)

    integers = pp.Combine(pp.Optional(pp.oneOf("+ -")) + pp.Word(pp.nums) + pp.Optional(pp.oneOf("e E") +
                                                                                        pp.Optional(
                                                                                            pp.oneOf("+ -")) + pp.Word(
        pp.nums))).setResultsName('t_integer')

    floats = pp.Combine(pp.Optional(pp.oneOf('+ -')) + (pp.Word(pp.nums) + pp.Literal('.')
                                                        # float with decimal point
                                                        + pp.Optional(pp.Word(pp.nums)) |
                                                        # float with leading decimal point
                                                        pp.Literal(
                                                            '.') + pp.Optional(pp.oneOf('+ -')) + pp.Word(pp.nums)
                                                        ) + (pp.Optional(pp.oneOf('e E') + pp.Optional(pp.oneOf('+ -')) + pp.Word(pp.nums)))).setResultsName('t_float')

    chars = pp.QuotedString("'", escChar='\\').setResultsName('t_char')

    increment_ops = pp.oneOf('++ --').setResultsName('t_inc')
    arithmetic_ops = pp.oneOf('+ * - / % =').setResultsName('t_arith')
    comparison_ops = pp.oneOf(
        '<< >>  < <= > >= == !=').setResultsName('t_compare')
    logical_ops = pp.oneOf('&& ||').setResultsName('t_logic')
    compound_assignment_ops = pp.oneOf(
        '+= -= *= /= %= <<= >>= &= ^= |=').setResultsName('t_compound_assignment')
    bitwise_logical_ops = pp.oneOf('| ^ ~ &').setResultsName('t_bit_op')

    separators = (pp.Literal(',') | pp.Literal(';') | pp.Literal(':') | pp.Literal('[') | pp.Literal(']') |
                  pp.Literal('{') | pp.Literal('}') | pp.Literal(
                      '(') | pp.Literal(')')
                  ).setResultsName('t_separator')

    format_specifiers = pp.oneOf(
        '%d %f %x %u %c %s %e %p %lu %ld %lf').setResultsName('t_format')

    string_literal = pp.QuotedString(
        '"', escChar='\\').setResultsName('t_string')

    grammar = (key_words | floats | integers | identifiers | chars | format_specifiers | increment_ops |
               arithmetic_ops | comparison_ops | logical_ops | compound_assignment_ops | bitwise_logical_ops |
               separators | string_literal)

    return grammar


def tokenize():
    """
        Generates tokens based on grammar and fills the symbol table

    """
    input_stream = ignore_comments()
    x = lexeme_grammar()
    toks = list()

    for i, line in enumerate(input_stream.splitlines()):
        for tokens in x.scanString(line):
            # token ,start position and end position
            try:

                print(
                    f'Token: {tokens[0].getName()}, Attribute: {tokens[0]}, At Position: {tokens[1] + 1} Line: {i + 1}\n')

                toks.append((tokens[0].getName(), tokens[0][0], i))
            except pp.ParseException as e:
                print(f'Parsing error: {e.msg} at position {e.loc}')
                continue

    with open('symbol_table_data.json', 'w') as st, open('tokens.json', 'w') as tk:
        json.dump(symbol_table, st,indent=2)
        json.dump(toks, tk,indent=2)

    # pprint.pprint(toks)
    # pprint.pprint(symbol_table)


tokenize()
