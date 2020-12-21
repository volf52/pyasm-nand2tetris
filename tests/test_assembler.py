from pathlib import Path

import pytest

from pyasm.assembler import AddressOutOfRange, Assembler
from pyasm.parser import Parser


def test_addr_out_of_range():
    parser = Parser("@24579")
    assembler = Assembler(parser)

    with pytest.raises(AddressOutOfRange):
        _ = assembler.assemble()


@pytest.mark.integ_test
def test_assembler_with_add():
    code = "// Compute RAM[0] = 2 + 3\n@2\nD = A\n@3\n\nD = A+ D\n@0\nM=d"
    parser = Parser(code)
    assembler = Assembler(parser)

    output = assembler.assemble()
    expected = [
        "0000000000000010",
        "1110110000010000",
        "0000000000000011",
        "1110000010010000",
        "0000000000000000",
        "1110001100001000",
    ]

    assert output == expected


def load_file(name: str):
    return (
        Path(__file__).parent.joinpath("asm_files").joinpath(name).read_text()
    )


@pytest.mark.integ_test
@pytest.mark.integ_assembler
def test_assembler_with_add_file():
    code = load_file("Add.asm")
    parser = Parser(code)
    assembler = Assembler(parser)

    output = assembler.assemble()
    expected = load_file("Add.hack").splitlines()

    assert output == expected


@pytest.mark.integ_test
@pytest.mark.integ_assembler
def test_assembler_with_max_file():
    code = load_file("Max.asm")
    parser = Parser(code)
    assembler = Assembler(parser)

    output = assembler.assemble()
    expected = load_file("Max.hack").splitlines()

    assert output == expected


@pytest.mark.integ_test
@pytest.mark.integ_assembler
def test_assembler_with_max_l_file():
    code = load_file("MaxL.asm")
    parser = Parser(code)
    assembler = Assembler(parser)

    output = assembler.assemble()
    expected = load_file("MaxL.hack").splitlines()

    assert output == expected
