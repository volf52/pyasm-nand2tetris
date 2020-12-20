import typer

cli = typer.Typer()


@cli.command(name="hello")
def hello():
    typer.echo("Hello there")


if __name__ == "__main__":
    cli()
