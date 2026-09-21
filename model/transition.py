from __future__ import annotations

from dataclasses import dataclass

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from state import State

@dataclass(frozen=True)
class Transition:
    state: State
    read: str | None
    write: str | None
    move: int
    next_state: State

    @staticmethod
    def _move_symbol(delta: int) -> str:
        if delta > 0:
            return f"+{delta}"
        if delta < 0:
            return str(delta)
        return "0"