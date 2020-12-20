import re
from enum import Enum
from functools import lru_cache
from typing import List, Optional


class CommandType(Enum):
    A_COMMAND = "A_COMMAND"
    L_COMMAND = "L_COMMAND"
    C_COMMAND = "C_COMMAND"

    def __str__(self):
        return super().__str__().split(".")[-1]


class InvalidCommandException(Exception):
    def __init__(self, command: str):
        self.message = f"Invalid Command: {command}"
        super(InvalidCommandException, self).__init__(self.message)


@lru_cache(maxsize=1)
def generate_possible_c_commands():
    possible_comps = [
        "0",
        "1",
        "-1",
        "D",
        "A",
        "M",
        "!D",
        "!A",
        "!M",
        "-D",
        "-A",
        "-M",
        "D+1",
        "A+1",
        "M+1",
        "D-1",
        "A-1",
        "M-1",
        "D+A",
        "D-A",
        "D+M",
        "M+D",
        "D-M",
        "M-D",
        "A+D",
        "A-D",
        "D&A",
        "A&D",
        "A|D",
        "D|A",
        "D&M",
        "M&D",
        "M|D",
        "D|M",
    ]

    possible_dests = ["M", "D", "MD", "A", "AM", "AD", "AMD"]
    possible_jmps = ["JGT", "JEQ", "JGE", "JLT", "JNE", "JLE", "JMP"]

    result = []
    for comp in possible_comps:
        for dest in possible_dests:
            result.append(f"{dest}={comp}")
            for jmp in possible_jmps:
                result.append(f"{dest}={comp};{jmp}")

        for jmp in possible_jmps:
            result.append(f"{comp};{jmp}")

    return set(result)


POSSIBLE_C_COMMANDS = generate_possible_c_commands()


class Parser:
    COMMENT_RE = re.compile(r"\s*//.*\n?")
    NEWLINE_RE = re.compile(r"(?:\n){2,}")

    A_COMMAND_RE = re.compile(r"^@([^-][\w\d.]*)$")
    L_COMMAND_RE = re.compile(r"^\(([A-Za-z].*)\)$")

    __slots__ = (
        "__raw_txt",
        "__log",
        "__lines",
        "__counter",
        "__num_lines",
        "__symbol",
        "__curr_command_type",
        "__comp",
        "__dest",
        "__jmp",
    )

    def __init__(self, raw_text: str, /, *, log_func=print):
        self.__raw_txt = raw_text
        self.__log = log_func
        self.__counter = 0

        self.__lines: List[str] = Parser.process(raw_text)
        self.__num_lines = len(self.__lines)
        if self.__num_lines < 1:
            raise ValueError("The input must contain some code")

        self.__curr_command_type: Optional[CommandType] = None
        self.__symbol = ""
        self.__comp = ""
        self.__dest = ""
        self.__jmp = ""

    @staticmethod
    def process(txt: str) -> List[str]:
        # Remove comments and trailing whitespace
        txt = Parser.COMMENT_RE.sub("\n", txt).strip()

        # Remove multiple '\n' to a single '\n'
        txt = Parser.NEWLINE_RE.sub("\n", txt)
        txt = txt.replace(" ", "")

        return [x.strip() for x in txt.splitlines()]

    def _reset_counter(self) -> None:
        self.__counter = 0

    def _reset_symbols(self) -> None:
        self.__curr_command_type = None
        self.__symbol = ""
        self.__comp = ""
        self.__dest = ""
        self.__jmp = ""

    def has_more_commands(self) -> bool:
        return self.__counter < self.__num_lines

    def advance(self) -> None:
        if self.has_more_commands():
            self.__counter += 1

    @property
    def counter(self):
        return self.__counter

    @property
    def current_command(self) -> str:
        if not self.has_more_commands():
            raise ValueError("No more commands")

        return self.__lines[self.__counter]

    def command_type(self, command: str) -> CommandType:
        a_match = Parser.A_COMMAND_RE.findall(command)
        l_match = Parser.L_COMMAND_RE.findall(command)
        self._reset_symbols()

        if a_match:
            self.__symbol = a_match[0]
            self.__curr_command_type = CommandType.A_COMMAND
        elif l_match:
            self.__symbol = l_match[0]
            self.__curr_command_type = CommandType.L_COMMAND
        else:
            command = command.upper()
            if command in POSSIBLE_C_COMMANDS:
                self.__curr_command_type = CommandType.C_COMMAND

                equal_sign_present = "=" in command
                semicolon_present = ";" in command
                split = re.split("=|;", command)
                if len(split) in (2, 3):
                    self.__curr_command_type = CommandType.C_COMMAND
                    if equal_sign_present:
                        self.__dest = split[0]
                        self.__comp = split[1]
                    if semicolon_present:
                        self.__comp = split[-2]
                        self.__jmp = split[-1]

        if self.__curr_command_type is None:
            raise InvalidCommandException(command)

        return self.__curr_command_type

    @property
    def symbol(self) -> str:
        command_type = self.__curr_command_type
        if command_type not in (CommandType.A_COMMAND, CommandType.L_COMMAND):
            msg = (
                f"Command type must be {CommandType.A_COMMAND} or "
                f"{CommandType.L_COMMAND} when accessing symbol. "
                f"Current type: {command_type}"
            )

            raise ValueError(msg)

        return self.__symbol

    @property
    def dest(self):
        if self.__curr_command_type is not CommandType.C_COMMAND:
            msg = f"Command type must be {CommandType.C_COMMAND} to access `dest`"
            raise ValueError(msg)

        return self.__dest

    @property
    def comp(self):
        if self.__curr_command_type is not CommandType.C_COMMAND:
            msg = f"Command type must be {CommandType.C_COMMAND} to access `comp`"
            raise ValueError(msg)

        return self.__comp

    @property
    def jmp(self):
        if self.__curr_command_type is not CommandType.C_COMMAND:
            msg = (
                f"Command type must be {CommandType.C_COMMAND} to access `jmp`"
            )
            raise ValueError(msg)

        return self.__jmp
