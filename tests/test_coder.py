import pytest

from pyasm.coder import Coder, InvalidMnemonicError, SymbolTable


def test_coder_cannot_be_instantiated():
    with pytest.raises(RuntimeError):
        Coder()


def test_dest_code_length():
    table = Coder.get_dest_table()
    code_values = set(table.values())

    assert len(code_values) == 8
    for code in code_values:
        assert len(code) == 3


def test_comp_code_length():
    table = Coder.get_comp_table()
    code_values = set(table.values())

    assert len(code_values) == 28
    for code in code_values:
        assert len(code) == 7


def test_jmp_code_length():
    table = Coder.get_jmp_table()
    code_values = set(table.values())

    assert len(code_values) == 8
    for code in code_values:
        assert len(code) == 3


@pytest.mark.parametrize(
    "mnemonic,expected",
    [("", "000"), ("MAD", "111"), ("DA", "110"), ("M", "001")],
)
def test_valid_dest_(mnemonic: str, expected: str):
    code = Coder.translate_dest(mnemonic)
    assert code == expected


@pytest.mark.parametrize("mnemonic", ["l", "shoot", "MDM", "AA"])
def test_invalid_dest_(mnemonic: str):
    with pytest.raises(InvalidMnemonicError) as err:
        Coder.translate_dest(mnemonic)

    assert mnemonic in str(err.value)
    assert "dest" in str(err.value)


@pytest.mark.parametrize(
    "mnemonic,expected",
    [("", "000"), ("jgt", "001"), ("JLe", "110"), ("jMp", "111")],
)
def test_valid_jmp_(mnemonic: str, expected: str):
    code = Coder.translate_jmp(mnemonic)
    assert code == expected


@pytest.mark.parametrize("mnemonic", ["JA", "jbe", "AD", "bla"])
def test_invalid_jmp_(mnemonic: str):
    with pytest.raises(InvalidMnemonicError) as err:
        Coder.translate_jmp(mnemonic)

    assert mnemonic in str(err.value)
    assert "jmp" in str(err.value)


@pytest.mark.parametrize(
    "mnemonic,expected",
    [
        ("0", "0101010"),
        ("D+1", "0011111"),
        ("D|M", "1010101"),
        ("m-d", "1000111"),
    ],
)
def test_valid_comp_(mnemonic: str, expected: str):
    code = Coder.translate_comp(mnemonic)
    assert code == expected


@pytest.mark.parametrize(
    "mnemonic", ["!1", "1-M", "A+M", "A&M", "! D", "D -1", "A + D"]
)
def test_invalid_comp_(mnemonic: str):
    with pytest.raises(InvalidMnemonicError) as err:
        Coder.translate_comp(mnemonic)

    assert mnemonic in str(err.value)
    assert "comp" in str(err.value)


@pytest.fixture(scope="module")
def symbol_table() -> SymbolTable:
    return SymbolTable()


@pytest.mark.parametrize(
    "symbol", ["r0", "R0", "THIS", "SCREEN", "scReEn", "kbd", "R7"]
)
def test_adding_reserved_symbols_to_symbol_table(
    symbol_table: SymbolTable, symbol: str
):
    with pytest.raises(ValueError):
        symbol_table[symbol] = 3

    assert len(symbol_table) == 0


def test_getting_reserved_symbols(symbol_table: SymbolTable):
    for i in range(1, 15 + 1):
        assert symbol_table.get(f"r{i}") == i
        assert symbol_table.get(f"R{i}") == i

    assert symbol_table.get("sp") == 0
    assert symbol_table.get("SP") == 0
    assert symbol_table.get("lcl") == 1
    assert symbol_table.get("LCL") == 1
    assert symbol_table.get("arg") == 2
    assert symbol_table.get("ARG") == 2
    assert symbol_table.get("this") == 3
    assert symbol_table.get("THIS") == 3
    assert symbol_table.get("that") == 4
    assert symbol_table.get("THAT") == 4


@pytest.mark.integ_test
def test_setting_and_getting_symbol_table_entries_():
    symbol_table = SymbolTable()

    assert len(symbol_table) == 0

    # Get from empty table
    with pytest.raises(KeyError):
        _ = symbol_table["abc"]

    assert symbol_table.get("abc") is None
    assert symbol_table.get("abc", default=14) == 14

    assert len(symbol_table) == 0

    symbol_table["loop"] = 16
    assert symbol_table["loop"] == 16
    assert symbol_table.get("loop") == 16

    assert not symbol_table.delete("r0")
    assert not symbol_table.delete("KBD")
    assert not symbol_table.delete("abc")
    assert symbol_table.delete("loop")
    assert symbol_table.get("loop") is None
    with pytest.raises(KeyError):
        _ = symbol_table["loop"]

    symbol_table["end"] = 256
    assert symbol_table["end"] == 256
    symbol_table["end"] = 147
    assert symbol_table["end"] == 147
    symbol_table["something_else"] = 123
    assert len(symbol_table) == 2

    symbol_table.clear()
    assert len(symbol_table) == 0
