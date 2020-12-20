from functools import lru_cache
from pathlib import Path

import pytest

from pyasm.parser import CommandType, InvalidCommandException, Parser


def generate_valid_parser():
    txt = "//comment\n\n@23\nA=D\n\n(END)\nM = A + D\n// Another comment \n"
    parser = Parser(txt)

    return parser


@pytest.fixture(scope="module")
def parser() -> Parser:
    return generate_valid_parser()


@pytest.mark.parametrize(
    "attrib",
    [
        "__log",
        "__counter",
        "__lines",
        "__num_lines",
        "__curr_command_type",
        "__symbol",
        "__comp",
        "__dest",
        "__jmp",
    ],
)
def test_private_attribute_access_for(parser: Parser, attrib: str):
    with pytest.raises(AttributeError):
        _ = getattr(parser, attrib)


def test_value_error_on_empty_input():
    txt = "// this is a comment\n\n\n // Another comment //\n // "

    with pytest.raises(ValueError) as e_info:
        Parser(txt)

    assert str(e_info.value) == "The input must contain some code"


@pytest.mark.parametrize(
    "txt,expected",
    [
        ("// this is a comment\n\n\n//Another comment\n", []),
        ("@value", ["@value"]),
        ("M=A+D", ["M=A+D"]),
        ("AMD=A", ["AMD=A"]),
        (" M = A + D ", ["M=A+D"]),
        ("D=A+D;jmp", ["D=A+D;jmp"]),
        ("(LOOP)", ["(LOOP)"]),
        (
            "//comment\n\n@23\nA=D\n\n(END)\nM = A + D\n// Another comment \n",
            ["@23", "A=D", "(END)", "M=A+D"],
        ),
    ],
    ids=[
        "just comments",
        "A command",
        "C command",
        "bigger c command",
        "C command with spaces",
        "full C command",
        "l command",
        "comments plus code",
    ],
)
def test_parser_process_func_with_(txt: str, expected: str):
    processed = Parser.process(txt)

    assert processed == expected


@pytest.mark.parametrize(
    "command,symbol",
    [("@23", "23"), ("@value", "value"), ("@anything", "anything")],
)
def test_valid_a_commands(parser: Parser, command: str, symbol: str):
    assert parser.command_type(command) is CommandType.A_COMMAND
    assert parser.symbol == symbol


@pytest.mark.parametrize(
    "command,symbol",
    [
        ("(end)", "end"),
        ("(loop)", "loop"),
        ("(anything_goes)", "anything_goes"),
    ],
)
def test_valid_l_commands(parser: Parser, command: str, symbol: str):
    assert parser.command_type(command) is CommandType.L_COMMAND
    assert parser.symbol == symbol


@lru_cache(maxsize=1)
def get_possible_c_commands():
    possible_comps = [
        "0",
        "1",
        "-1",
        "D",
        "A",
        "M",
        "!D",
        "!A",
        "!M",
        "-D",
        "-A",
        "-M",
        "D+1",
        "A+1",
        "M+1",
        "D-1",
        "A-1",
        "M-1",
        "D+A",
        "D-A",
        "D+M",
        "M+D",
        "D-M",
        "M-D",
        "A+D",
        "A-D",
        "D&A",
        "A&D",
        "A|D",
        "D|A",
        "D&M",
        "M&D",
        "M|D",
        "D|M",
    ]

    possible_dests = ["M", "D", "MD", "A", "AM", "AD", "AMD"]
    possible_jmps = ["JGT", "JEQ", "JGE", "JLT", "JNE", "JLE", "JMP"]

    result = []
    for comp in possible_comps:
        for dest in possible_dests:
            result.append((f"{dest}={comp}", dest, comp, ""))
            for jmp in possible_jmps:
                result.append((f"{dest}={comp};{jmp}", dest, comp, jmp))

        for jmp in possible_jmps:
            result.append((f"{comp};{jmp}", "", comp, jmp))

    return result


possible_c_commands = get_possible_c_commands()


@pytest.mark.parametrize("command,dest,comp,jmp", possible_c_commands)
def test_valid_c_commands(
    parser: Parser, command: str, dest: str, comp: str, jmp: str
):
    assert parser.command_type(command) is CommandType.C_COMMAND
    assert parser.comp == comp
    assert parser.dest == dest
    assert parser.jmp == jmp


@pytest.mark.parametrize(
    "command", ["kbasb", "A;M=D;JMP", "MM=A;JLE", "AM=MD;;jmp", "(asd"]
)
def test_invalid_commands(parser: Parser, command: str):
    with pytest.raises(InvalidCommandException):
        parser.command_type(command)


@pytest.mark.integ_test
@pytest.mark.integ_parser
def test_parser_with_proper_code():
    code = (
        "// this is a comment\n\n\n // Another comment //  \n"
        " @value // comment\nA = A + D \n(LOOP)\n//comm\n\nD;jle\n"
    )

    parser = Parser(code)

    # Raise error if we try to access anything right now
    for attrib in ["symbol", "dest", "comp", "jmp"]:
        with pytest.raises(ValueError):
            getattr(parser, attrib)

    assert parser.counter == 0
    assert parser.has_more_commands()
    command = parser.current_command
    assert parser.command_type(command) == CommandType.A_COMMAND
    assert parser.symbol == "value"
    with pytest.raises(ValueError):
        _ = parser.jmp
        _ = parser.dest
        _ = parser.comp

    parser.advance()

    assert parser.counter == 1
    assert parser.has_more_commands()
    command = parser.current_command
    assert parser.command_type(command) == CommandType.C_COMMAND
    assert parser.dest == "A"
    assert parser.comp == "A+D"
    assert parser.jmp == ""
    with pytest.raises(ValueError):
        _ = parser.symbol

    parser.advance()

    assert parser.counter == 2
    assert parser.has_more_commands()
    command = parser.current_command
    assert parser.command_type(command) == CommandType.L_COMMAND
    assert parser.symbol == "LOOP"
    with pytest.raises(ValueError):
        _ = parser.jmp
        _ = parser.dest
        _ = parser.comp

    parser.advance()

    assert parser.counter == 3
    assert parser.has_more_commands()
    command = parser.current_command
    assert parser.command_type(command) == CommandType.C_COMMAND
    assert parser.dest == ""
    assert parser.comp == "D"
    assert parser.jmp == "JLE"
    with pytest.raises(ValueError):
        _ = parser.symbol

    parser.advance()
    assert parser.counter == 4
    assert not parser.has_more_commands()
    with pytest.raises(ValueError):
        _ = parser.current_command


def load_file(name: str):
    return Path(__file__).parent.joinpath(name).read_text()


@pytest.mark.integ_test
@pytest.mark.integ_parser
def test_parser_with_add_asm_file():
    code = load_file("Add.asm")
    parser = Parser(code)

    expected_commands = ["@2", "D=A", "@3", "D=D+A", "@0", "M=D"]
    expected_types = [
        CommandType.A_COMMAND,
        CommandType.C_COMMAND,
        CommandType.A_COMMAND,
        CommandType.C_COMMAND,
        CommandType.A_COMMAND,
        CommandType.C_COMMAND,
    ]
    expected_symbols = ["2", None, "3", None, "0", None]
    expected_dest = [None, "D", None, "D", None, "M"]
    expected_comp = [None, "A", None, "D+A", None, "D"]

    zip_obj = zip(
        expected_commands,
        expected_types,
        expected_symbols,
        expected_dest,
        expected_comp,
    )

    for i, (command, tp, symbol, dest, comp) in enumerate(zip_obj):
        assert parser.has_more_commands()
        assert parser.counter == i
        comm = parser.current_command
        assert comm == command
        assert parser.command_type(comm) == tp
        if symbol is None:
            assert parser.dest == dest
            assert parser.comp == comp
            assert parser.jmp == ""
            with pytest.raises(ValueError):
                _ = parser.symbol
        else:
            assert parser.symbol == symbol
            with pytest.raises(ValueError):
                _ = parser.dest
                _ = parser.comp
                _ = parser.jmp

        parser.advance()

    assert parser.counter == 6
    assert not parser.has_more_commands()


@pytest.mark.integ_test
@pytest.mark.integ_parser
def test_parser_with_max_L_asm_file():
    code = load_file("MaxL.asm")
    parser = Parser(code)

    expected_commands = [
        "@0",
        "D=M",
        "@1",
        "D=D-M",
        "@10",
        "D;JGT",
        "@1",
        "D=M",
        "@12",
        "0;JMP",
        "@0",
        "D=M",
        "@2",
        "M=D",
        "@14",
        "0;JMP",
    ]
    expected_types = [
        CommandType.A_COMMAND,
        CommandType.C_COMMAND,
        CommandType.A_COMMAND,
        CommandType.C_COMMAND,
        CommandType.A_COMMAND,
        CommandType.C_COMMAND,
        CommandType.A_COMMAND,
        CommandType.C_COMMAND,
        CommandType.A_COMMAND,
        CommandType.C_COMMAND,
        CommandType.A_COMMAND,
        CommandType.C_COMMAND,
        CommandType.A_COMMAND,
        CommandType.C_COMMAND,
        CommandType.A_COMMAND,
        CommandType.C_COMMAND,
    ]
    expected_symbols = [
        "0",
        None,
        "1",
        None,
        "10",
        None,
        "1",
        None,
        "12",
        None,
        "0",
        None,
        "2",
        None,
        "14",
        None,
    ]
    expected_dest = expected_dest = [
        None,
        "D",
        None,
        "D",
        None,
        "",
        None,
        "D",
        None,
        "",
        None,
        "D",
        None,
        "M",
        None,
        "",
    ]

    expected_comp = [
        None,
        "M",
        None,
        "D-M",
        None,
        "D",
        None,
        "M",
        None,
        "0",
        None,
        "M",
        None,
        "D",
        None,
        "0",
    ]

    expected_jmp = [
        None,
        "",
        None,
        "",
        None,
        "JGT",
        None,
        "",
        None,
        "JMP",
        None,
        "",
        None,
        "",
        None,
        "JMP",
    ]

    zip_obj = zip(
        expected_commands,
        expected_types,
        expected_symbols,
        expected_dest,
        expected_comp,
        expected_jmp,
    )

    for i, (command, tp, symbol, dest, comp, jmp) in enumerate(zip_obj):
        assert parser.has_more_commands()
        assert parser.counter == i
        comm = parser.current_command
        assert comm == command
        assert parser.command_type(comm) == tp
        if symbol is None:
            assert parser.dest == dest
            assert parser.comp == comp
            assert parser.jmp == jmp
            with pytest.raises(ValueError):
                _ = parser.symbol
        else:
            assert parser.symbol == symbol
            with pytest.raises(ValueError):
                _ = parser.dest
                _ = parser.comp
                _ = parser.jmp

        parser.advance()

    assert parser.counter == 16
    assert not parser.has_more_commands()


@pytest.mark.integ_test
@pytest.mark.integ_parser
def test_parser_with_max_asm_file():
    code = load_file("Max.asm")
    parser = Parser(code)

    expected_commands = [
        "@R0",
        "D=M",
        "@R1",
        "D=D-M",
        "@OUTPUT_FIRST",
        "D;JGT",
        "@R1",
        "D=M",
        "@OUTPUT_D",
        "0;JMP",
        "(OUTPUT_FIRST)",
        "@R0",
        "D=M",
        "(OUTPUT_D)",
        "@R2",
        "M=D",
        "(INFINITE_LOOP)",
        "@INFINITE_LOOP",
        "0;JMP",
    ]
    expected_types = [
        CommandType.A_COMMAND,
        CommandType.C_COMMAND,
        CommandType.A_COMMAND,
        CommandType.C_COMMAND,
        CommandType.A_COMMAND,
        CommandType.C_COMMAND,
        CommandType.A_COMMAND,
        CommandType.C_COMMAND,
        CommandType.A_COMMAND,
        CommandType.C_COMMAND,
        CommandType.L_COMMAND,
        CommandType.A_COMMAND,
        CommandType.C_COMMAND,
        CommandType.L_COMMAND,
        CommandType.A_COMMAND,
        CommandType.C_COMMAND,
        CommandType.L_COMMAND,
        CommandType.A_COMMAND,
        CommandType.C_COMMAND,
    ]
    expected_symbols = [
        "R0",
        None,
        "R1",
        None,
        "OUTPUT_FIRST",
        None,
        "R1",
        None,
        "OUTPUT_D",
        None,
        "OUTPUT_FIRST",
        "R0",
        None,
        "OUTPUT_D",
        "R2",
        None,
        "INFINITE_LOOP",
        "INFINITE_LOOP",
        None,
    ]
    expected_dest = [
        None,
        "D",
        None,
        "D",
        None,
        "",
        None,
        "D",
        None,
        "",
        None,
        None,
        "D",
        None,
        None,
        "M",
        None,
        None,
        "",
    ]
    expected_comp = [
        None,
        "M",
        None,
        "D-M",
        None,
        "D",
        None,
        "M",
        None,
        "0",
        None,
        None,
        "M",
        None,
        None,
        "D",
        None,
        None,
        "0",
    ]

    expected_jmp = [
        None,
        "",
        None,
        "",
        None,
        "JGT",
        None,
        "",
        None,
        "JMP",
        None,
        None,
        "",
        None,
        None,
        "",
        None,
        None,
        "JMP",
    ]

    zip_obj = zip(
        expected_commands,
        expected_types,
        expected_symbols,
        expected_dest,
        expected_comp,
        expected_jmp,
    )

    for i, (command, tp, symbol, dest, comp, jmp) in enumerate(zip_obj):
        assert parser.has_more_commands()
        assert parser.counter == i
        comm = parser.current_command
        assert comm == command
        assert parser.command_type(comm) == tp
        if symbol is None:
            assert parser.dest == dest
            assert parser.comp == comp
            assert parser.jmp == jmp
            with pytest.raises(ValueError):
                _ = parser.symbol
        else:
            assert parser.symbol == symbol
            with pytest.raises(ValueError):
                _ = parser.dest
                _ = parser.comp
                _ = parser.jmp

        parser.advance()

    assert parser.counter == 19
    assert not parser.has_more_commands()
