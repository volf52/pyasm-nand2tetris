from typing import List

from pyasm.coder import Coder, SymbolTable
from pyasm.parser import CommandType, Parser


class AddressOutOfRange(Exception):
    def __init__(self, line: int, command: str):
        msg = f"Address out of range at line : {line}\tCommand: {command}"
        super(AddressOutOfRange, self).__init__(msg)


class Assembler:
    __MAX_ADDR = 24576
    __slots__ = "__parser", "__sym_table"

    def __init__(self, parser: Parser):
        self.__parser = parser
        self.__sym_table = SymbolTable()

    def assemble(self) -> List[str]:
        buffer = []
        parser = self.__parser
        table = self.__sym_table

        # Read symbols and update sym_table
        while parser.has_more_commands():
            command = parser.current_command
            command_type = parser.command_type(command)
            if command_type is CommandType.L_COMMAND:
                symbol = parser.symbol
                if table.get(symbol) is None:
                    table[symbol] = parser.line_idx

            parser.advance()

        parser.reset()

        # Decode commands using Coder and sym_table
        while parser.has_more_commands():
            command = parser.current_command
            command_type = parser.command_type(command)
            if command_type is CommandType.C_COMMAND:
                dest = Coder.translate_dest(parser.dest)
                comp = Coder.translate_comp(parser.comp)
                jmp = Coder.translate_jmp(parser.jmp)

                buffer.append(f"111{comp}{dest}{jmp}")
            elif command_type is CommandType.A_COMMAND:
                symbol = parser.symbol
                if symbol.isnumeric():
                    n = int(symbol)
                    if n > Assembler.__MAX_ADDR:
                        raise AddressOutOfRange(parser.counter + 1, command)
                    buffer.append("{:0>16b}".format(n))
                else:
                    addr = table.get(symbol)
                    if addr is None:
                        table.add_variable(symbol)
                    else:
                        buffer.append("{:0>16b}".format(addr))

            parser.advance()

        return buffer
