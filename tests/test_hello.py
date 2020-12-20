from typer.testing import CliRunner
from pyasm.cli import cli

runner = CliRunner()

def test_hello():
    result = runner.invoke(cli)
    assert result.exit_code == 0
    # assert "Hello there" in result.stdout
    assert "Hello there\n" == result.stdout
