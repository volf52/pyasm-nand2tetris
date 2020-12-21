from typing import Dict, Optional

TranslationTable = Dict[str, str]


class InvalidMnemonicError(LookupError):
    def __init__(self, field: str, mnemonic: str):
        msg = f"Invalid mnemonic for `{field}`: {mnemonic}"
        super(InvalidMnemonicError, self).__init__(msg)


class Coder:
    __DEST = {
        "": "000",
        "M": "001",
        "D": "010",
        "MD": "011",
        "DM": "011",
        "A": "100",
        "AM": "101",
        "MA": "101",
        "AD": "110",
        "DA": "110",
        "AMD": "111",
        "ADM": "111",
        "MAD": "111",
        "MDA": "111",
        "DAM": "111",
        "DMA": "111",
    }
    __COMP = {
        "0": "0101010",
        "1": "0111111",
        "-1": "0111010",
        "D": "0001100",
        "A": "0110000",
        "M": "1110000",
        "!D": "0001101",
        "!A": "0110001",
        "!M": "1110001",
        "-D": "0001111",
        "-A": "0110011",
        "-M": "1110011",
        "D+1": "0011111",
        "A+1": "0110111",
        "M+1": "1110111",
        "D-1": "0001110",
        "A-1": "0110010",
        "M-1": "1110010",
        "D+A": "0000010",
        "A+D": "0000010",
        "D+M": "1000010",
        "M+D": "1000010",
        "D-A": "0010011",
        "D-M": "1010011",
        "A-D": "0000111",
        "M-D": "1000111",
        "D&A": "0000000",
        "A&D": "0000000",
        "D&M": "1000000",
        "M&D": "1000000",
        "D|A": "0010101",
        "A|D": "0010101",
        "D|M": "1010101",
        "M|D": "1010101",
    }

    __JMP = {
        "": "000",
        "JGT": "001",
        "JEQ": "010",
        "JGE": "011",
        "JLT": "100",
        "JNE": "101",
        "JLE": "110",
        "JMP": "111",
    }

    def __init__(self):
        raise RuntimeError("Cannot instantiate this class")

    @staticmethod
    def get_dest_table() -> TranslationTable:
        return Coder.__DEST

    @staticmethod
    def get_comp_table() -> TranslationTable:
        return Coder.__COMP

    @staticmethod
    def get_jmp_table() -> TranslationTable:
        return Coder.__JMP

    @staticmethod
    def __get_mnemonic(mnemonic: str, table: TranslationTable, field: str):
        code = table.get(mnemonic.upper())
        if code is None:
            raise InvalidMnemonicError(field, mnemonic)

        return code

    @staticmethod
    def translate_dest(mnemonic: str) -> str:
        return Coder.__get_mnemonic(mnemonic, Coder.__DEST, "dest")

    @staticmethod
    def translate_comp(mnemonic: str) -> str:
        return Coder.__get_mnemonic(mnemonic, Coder.__COMP, "comp")

    @staticmethod
    def translate_jmp(mnemonic: str) -> str:
        return Coder.__get_mnemonic(mnemonic, Coder.__JMP, "jmp")


class SymbolTable:
    __RESERVED = {
        "r0": 0,
        "r1": 1,
        "r2": 2,
        "r3": 3,
        "r4": 4,
        "r5": 5,
        "r6": 6,
        "r7": 7,
        "r8": 8,
        "r9": 9,
        "r10": 10,
        "r11": 11,
        "r12": 12,
        "r13": 13,
        "r14": 14,
        "r15": 15,
        "sp": 0,
        "lcl": 1,
        "arg": 2,
        "this": 3,
        "that": 4,
        "screen": 16384,
        "kbd": 24576,
    }

    __slots__ = "__lookup_table", "__counter"

    def __init__(self):
        self.__lookup_table = {}
        self.__counter = 16

    def add_variable(self, variable: str) -> None:
        self.__lookup_table.__setitem__(variable, self.__counter)
        self.__counter += 1

    def __setitem__(self, key: str, value: int) -> None:
        if key.lower() in SymbolTable.__RESERVED:
            raise ValueError(f"Cannot set a reserved symbol. {key}")

        self.__lookup_table[key] = value

    def __getitem__(self, key: str):
        reserved = SymbolTable.__RESERVED.get(key.lower())
        if reserved is not None:
            return reserved

        return self.__lookup_table[key]

    def get(self, key: str, default=None) -> Optional[int]:
        reserved = SymbolTable.__RESERVED.get(key.lower())
        if reserved is not None:
            return reserved

        return self.__lookup_table.get(key, default)

    def __len__(self) -> int:
        return len(self.__lookup_table)

    def clear(self) -> None:
        self.__lookup_table.clear()
        self.__counter = 16

    def delete(self, symbol: str) -> bool:
        if symbol.lower() in SymbolTable.__RESERVED:
            return False

        val = self.__lookup_table.get(symbol)
        if val is None:
            return False

        self.__lookup_table.__delitem__(symbol)
        return True
