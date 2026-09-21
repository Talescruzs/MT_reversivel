from __future__ import annotations

import argparse
import re
from enum import Enum, auto
from pathlib import Path

from tape import Tape
from transition import Transition
from state import State


class MachinePhase(Enum):
    FORWARD = auto()    # fase de execução normal da máquina de Turing reversiva
    COPY = auto()       # fase de cópia do conteúdo da fita 1 para a fita 3
    RETRACE = auto()    # fase de retrocesso da máquina de Turing reversiva, usando a fita 2 como histórico
    HALT = auto()       # fase de parada da máquina de Turing reversiva


class TuringMachineReversive:
    def __init__(self, input_string: str, initial_state: State, states: list[State], transitions: list[Transition], final_states: set[State] | None = None):
        self.tape1 = Tape()     #input tape
        self.tape2 = Tape()     #history tape
        self.tape3 = Tape()     #output tape

        self.initial_state = initial_state
        self.state = initial_state
        self.phase = MachinePhase.FORWARD
        self.accepted = False

        self.states = list(states) if states is not None else []
        self.transitions = list(transitions) if transitions is not None else []
        self.final_states = set(final_states) if final_states is not None else set()

        self._copy_index = 0
        self._history_tokens = 0

        self.atual_transition_index = 0

        self._setup(input_string)

    def _setup(self, input_string: str):
        # Carrega a entrada na fita 1 e volta o cabeçote para o início.
        for char in input_string:
            self.tape1.write(char)
            self.tape1.move_right()

        for _ in range(len(input_string)):
            self.tape1.move_left()

    def is_final_state(self) -> bool:
        return self.state in self.final_states

    def has_finished(self) -> bool:
        return self.phase is MachinePhase.HALT

    def is_accepted(self) -> bool:
        return self.has_finished() and self.accepted

    def get_tape_contents(self):
        return self.tape1.get_tape(), self.tape2.get_tape(), self.tape3.get_tape()

    def _current_input_symbol(self) -> str | None:
        return self.tape1.read()

    def _find_transition(self) -> Transition | None:
        scanned = self._current_input_symbol()
        transition = self.state.get_next_transition(scanned)
        for ind_transition in self.transitions:
            if ind_transition == transition:
                self.atual_transition_index = self.transitions.index(transition)
                return transition
        return None

    def _state_by_name(self, name: str) -> State:
        for state in self.states:
            if state.name == name:
                return state
        raise ValueError(f"estado desconhecido no histórico: {name!r}")

    @staticmethod
    def _meaningful_length(tape: Tape) -> int:
        cells = tape.get_tape()
        end = len(cells)
        while end > 0 and cells[end - 1] is None:
            end -= 1
        return end

    @staticmethod
    def _move_tape(tape: Tape, delta: int) -> None:
        if delta > 0:
            for _ in range(delta):
                tape.move_right()
        elif delta < 0:
            for _ in range(-delta):
                tape.move_left()

    def _append_history_record(self) -> None:
        self.tape2.write(self.atual_transition_index)
        self.tape2.move_right()

        self._history_tokens += 1

    def _enter_copy_phase(self) -> None:
        self.phase = MachinePhase.COPY
        self._copy_index = 0
        self.accepted = True

    def _enter_retrace_phase(self) -> None:
        self.phase = MachinePhase.RETRACE
        if self._history_tokens > 0 and self.tape2.get_position() > 0:
            self.tape2.move_left()

    def _forward_step(self) -> bool:
        transition = self._find_transition()
        if transition is None:
            if self.state in self.final_states:
                self.phase = MachinePhase.COPY
                self.accepted = True
                return True

            self.phase = MachinePhase.HALT
            self.accepted = False
            return False

        self.tape1.write(transition.write)
        self._move_tape(self.tape1, transition.move)
        self.state = transition.next_state
        self._append_history_record()
        return True

    def _copy_step(self) -> bool:
        limit = self._meaningful_length(self.tape1)
        if self._copy_index >= limit:
            self._enter_retrace_phase()
            return True

        symbol = self.tape1.get_tape()[self._copy_index]
        self.tape3.write(symbol)
        self._copy_index += 1

        if self._copy_index < limit:
            self.tape3.move_right()

        return True

    def _retrace_step(self) -> bool:
        if self._history_tokens == 0:
            self.tape2 = Tape()
            self.phase = MachinePhase.HALT
            return False

        while self.tape1.read() is None:
            self.tape1.move_left()

        while self.tape2.read() is None:
            self.tape2.move_left()

        record = self.tape2.read()

        if isinstance(record, int):
            transition = self.transitions[record]
            self.state = transition.next_state
            self.tape1.write(transition.read)
            self._move_tape(self.tape1, -transition.move)
        else:
            raise ValueError(f"registro de histórico inválido: {record!r}")

        self.tape2.move_left()
        self._history_tokens -= 1
        if self._history_tokens == 0:
            self.tape2 = Tape()
            self.phase = MachinePhase.HALT
            return False

        return True

    def step(self) -> bool:
        if self.phase is MachinePhase.HALT:
            return False

        if self.phase is MachinePhase.FORWARD:
            return self._forward_step()

        if self.phase is MachinePhase.COPY:
            return self._copy_step()

        if self.phase is MachinePhase.RETRACE:
            return self._retrace_step()

        return False

    def run(self, max_steps: int = 100) -> int:
        steps = 0
        while steps < max_steps and not self.has_finished() and self.step():
            steps += 1
        return steps


def _parse_symbol(symbol: str) -> str | None:
    return None if symbol == "B" else symbol


def load_quintupla(path: str | Path) -> tuple[str, State, list[State], list[Transition], set[State]]:
    lines = [line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(lines) < 5:
        raise ValueError("arquivo de quíntupla incompleto")

    try:
        number_of_states, _, _, number_of_transitions = map(int, lines[0].split())
    except ValueError as error:
        raise ValueError("o cabeçalho deve conter: estados alfabeto_entrada alfabeto_fita transições") from error

    states = [State(name) for name in lines[1].split()]
    if len(states) != number_of_states:
        raise ValueError("a quantidade de estados não corresponde ao cabeçalho")
    states_by_name = {state.name: state for state in states}

    transition_pattern = re.compile(
        r"^\(([^,]+),([^\)]+)\)=\(([^,]+),([^,]+),([LR])\)$"
    )
    transitions: list[Transition] = []
    for line in lines[4:4 + number_of_transitions]:
        match = transition_pattern.match(line.replace(" ", ""))
        if match is None:
            raise ValueError(f"transição inválida: {line!r}")

        state_name, read, next_state_name, write, direction = match.groups()
        try:
            state = states_by_name[state_name]
            next_state = states_by_name[next_state_name]
        except KeyError as error:
            raise ValueError(f"estado desconhecido na transição: {error.args[0]!r}") from error

        transition = Transition(
            state,
            _parse_symbol(read),
            _parse_symbol(write),
            1 if direction == "R" else -1,
            next_state,
        )
        state.add_transition(transition)
        transitions.append(transition)

    if len(transitions) != number_of_transitions:
        raise ValueError("a quantidade de transições não corresponde ao cabeçalho")

    final_states = {state for state in states if not state.transitions}
    input_string = lines[4 + number_of_transitions]
    states[0].is_initial = True
    return input_string, states[0], states, transitions, final_states


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Executa uma máquina de Turing reversível a partir de uma quíntupla.")
    parser.add_argument("arquivo", type=Path, help="arquivo .txt com a quíntupla e a entrada")
    parser.add_argument("--max-steps", type=int, default=10000, help="limite de passos (padrão: 10000)")
    args = parser.parse_args()

    input_string, initial_state, states, transitions, final_states = load_quintupla(args.arquivo)
    machine = TuringMachineReversive(input_string, initial_state, states, transitions, final_states)
    
    while not machine.has_finished():
        machine.step()
        print("Passo:", machine.phase, machine.get_tape_contents())

    print("Fase atual:", machine.phase.name)
    print("Estado atual:", machine.state.name)
    print("Foi aceita?", machine.is_accepted())
    print("Fitas:", machine.get_tape_contents())
