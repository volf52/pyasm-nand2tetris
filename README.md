# PyASM Assembler

![Python Tests](https://github.com/volf52/pyasm-nand2tetris/workflows/Run%20Python%20Tests/badge.svg?branch=main)

ASM Assembler for the "Hack" Architecture from [Nand2Tetris](https://www.nand2tetris.org)

---
### Installation (shorter way):

- Download the wheel file from the [latest release](https://github.com/volf52/pyasm-nand2tetris/releases/latest).
- Install using pip (preferably in a separate virtual environment). You can use [pipx](https://pipxproject.github.io/pipx) to easily install the wheel file in a separate env, and expose the cli command.
- Have fun using `pyasm`. Run `pyasm --help` to check the commands and related options.

---
### Build from source:
- Install poetry from https://python-poetry.org.
- Clone this repo and cd into it.
- Run poetry install to create the virtualenv and install the packages.
- `poetry run pytest` to run the tests.
- `poetry build` to build the package into `dist`.
- Now you can install the package from the `dist` dir.

