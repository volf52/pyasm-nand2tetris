from pathlib import Path

from pyasm.cli import cli
from typer.testing import CliRunner

runner = CliRunner()

rootPth = Path(__file__).parent


def test_hello():
    result = runner.invoke(cli, ["hello"])
    assert result.exit_code == 0
    # assert "Hello there" in result.stdout
    assert "Hello there\n" == result.stdout


def test_invalid_path():
    result = runner.invoke(cli, ["assemble", str(rootPth.joinpath("asm_files/Add"))])
    assert result.exit_code == 2
    assert "Invalid value for 'FILEPTH'" in result.stdout


def test_invalid_extension():
    result = runner.invoke(
        cli, ["assemble", str(rootPth.joinpath("asm_files/Add.hack"))]
    )
    assert result.exit_code == 1
    assert "The file name must end with " in result.stdout


def test_empty_file():
    inpPth = rootPth.joinpath("asm_files/Empty.asm")
    inpPth.touch(exist_ok=False)  # must not exist beforehand

    result = runner.invoke(cli, ["assemble", str(inpPth)])
    inpPth.unlink(missing_ok=False)
    assert not inpPth.exists()

    assert result.exit_code == 1
    assert "The input must contain some code" in result.stdout


def test_valid_assembly():
    txt = rootPth.joinpath("asm_files/Add.asm").read_text()
    expected_out = rootPth.joinpath("asm_files/Add.hack").read_text()

    inpPth = rootPth.joinpath("asm_files/TestAdd.asm")
    inpPth.touch(exist_ok=False)
    inpPth.write_text(txt)

    result = runner.invoke(cli, ["assemble", str(inpPth)])
    inpPth.unlink(missing_ok=False)
    assert not inpPth.exists()

    assert result.exit_code == 0
    assembledPth = inpPth.parent.joinpath(f"{inpPth.stem}.hack")
    assert assembledPth.exists()
    output = assembledPth.read_text()
    assembledPth.unlink(missing_ok=False)
    assert not assembledPth.exists()

    assert output == expected_out


def test_valid_assembly_with_given_out_path():
    txt = rootPth.joinpath("asm_files/Add.asm").read_text()
    expected_out = rootPth.joinpath("asm_files/Add.hack").read_text()

    inpPth = rootPth.joinpath("asm_files/TestAdd.asm")
    inpPth.touch(exist_ok=False)
    inpPth.write_text(txt)
    assembledPth = inpPth.parent.joinpath(f"CustomAddOut.hack")

    result = runner.invoke(cli, ["assemble", str(inpPth), "--out", str(assembledPth)])
    inpPth.unlink(missing_ok=False)
    assert not inpPth.exists()

    assert result.exit_code == 0
    assert assembledPth.exists()
    output = assembledPth.read_text()
    assembledPth.unlink(missing_ok=False)
    assert not assembledPth.exists()

    assert output == expected_out
