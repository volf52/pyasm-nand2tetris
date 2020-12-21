import pytest

from pyasm.coder import Coder, InvalidMnemonicError


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
