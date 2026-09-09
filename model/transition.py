from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

class ActionType(Enum):
    WRITE = auto()
    MOVE = auto()

class HistoryTapeSymbol(Enum):
    START = "#"
    TRANSITION = "T"
    FINAL = "F"
    END = ";"
    BLANK = "_"

@dataclass(frozen=True)
class TapeAction:
    type: ActionType
    read: Optional[str] = None # símbolos de leitura/escrita/delta de cada fita
    write: Optional[str] = None
    delta: Optional[int] = None

    ## verifica se valores read, write e delta (deslocamento) estão de acordo com a ActionType
    ## ex: se a ação é de escrita, não pode haver delta
    def __post_init__(self):
        if self.type == ActionType.WRITE:
            if self.read is None or self.write is None or self.delta is not None:
                raise ValueError("action WRITE needs a 'read' and 'write' input, and no delta value")
        elif self.type == ActionType.MOVE:
            if self.delta is None or self.write is not None or self.read is not None:
                raise ValueError("action MOVE needs a delta input and no read/write values")

    @classmethod
    def write_action(cls, read_value: str | None, write_value: str) -> "TapeAction":
        return cls(type=ActionType.WRITE, read=read_value, write=write_value)

    @classmethod
    def move_action(cls, delta_value: int) -> "TapeAction":
        return cls(type=ActionType.MOVE, delta=delta_value)

    def invert(self) -> "TapeAction":
        if self.type == ActionType.WRITE:
            return TapeAction.write_action(read_value=self.write, write_value=self.read)
        else:
            return TapeAction.move_action(delta_value=-self.delta)

@dataclass(frozen=True)
class Transition:
    state: str
    read: str | None
    write: str | None
    move: int
    next_state: str

    @staticmethod
    def _move_symbol(delta: int) -> str:
        if delta > 0:
            return f"+{delta}"
        if delta < 0:
            return str(delta)
        return "0"

    def history_tokens(self) -> list[str]:
        return [
            HistoryTapeSymbol.START.value,
            HistoryTapeSymbol.TRANSITION.value,
            self.state,
            self.read if self.read is not None else HistoryTapeSymbol.BLANK.value,
            self.write if self.write is not None else HistoryTapeSymbol.BLANK.value,
            self._move_symbol(self.move),
            self.next_state,
            HistoryTapeSymbol.END.value,
        ]

    @classmethod
    def final_tokens(cls, state: str) -> list[str]:
        return [
            HistoryTapeSymbol.START.value,
            HistoryTapeSymbol.FINAL.value,
            state,
            HistoryTapeSymbol.END.value,
        ]