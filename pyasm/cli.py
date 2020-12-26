from pathlib import Path

import typer
from typer import Argument, Option

from pyasm.assembler import AddressOutOfRange, Assembler
from pyasm.coder import InvalidMnemonicError
from pyasm.parser import InvalidCommandException, Parser

cli = typer.Typer()


@cli.command(name="hello")
def hello():
    typer.echo("Hello there")


@cli.command(name="assemble", short_help="Assemble the input file")
def assemble(
    filepth: Path = Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=True,
        readable=True,
        resolve_path=True,
    ),
    out: Path = Option(None),
):
    if filepth.suffix != ".asm":
        typer.echo("The file name must end with `.asm`")
        raise typer.Exit(code=1)

    if out is None:
        out = filepth.parent.joinpath(f"{filepth.stem}.hack")

    try:
        parser = Parser(filepth.read_text())
    except ValueError as err:
        typer.echo(err)
        raise typer.Exit(1)

    assembler = Assembler(parser)

    try:
        assembly = assembler.assemble()
    except (InvalidCommandException, InvalidMnemonicError, AddressOutOfRange) as err:
        typer.echo(err)
        raise typer.Exit(code=1)

    typer.echo(f"Writing to {out}")
    with out.open("w") as f:
        f.writelines([x + "\n" for x in assembly])

    typer.echo("Done")


if __name__ == "__main__":
    cli()
