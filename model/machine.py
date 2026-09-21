from __future__ import annotations

from enum import Enum, auto

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


if __name__ == "__main__":
    # Exemplo mínimo no formato de Bennett:
    # fase 1: escreve e anda
    # fase 2: copia o resultado para a fita 3
    # fase 3: faz o retrace usando a fita 2
    states = [
        State("q0", is_initial=True),
        State("q1"),
        State("q2"),
        State("q3", is_final=True),
    ]
    transitions = [
        Transition(states[0], "a", "x", 1, states[1]),
        Transition(states[1], "b", "y", 1, states[2]),
        Transition(states[2], "c", "z", 1, states[3]),
    ]
    states[0].transitions = [
        transitions[0],
    ]
    states[1].transitions = [
        transitions[1],
    ]
    states[2].transitions = [
        transitions[2],
    ]
    states[3].transitions = []

    final_states = {states[3]}
    
    machine = TuringMachineReversive("abc", states[0], states, transitions, final_states)

    print("Antes:", machine.get_tape_contents())
    while not machine.has_finished():
        machine.step()
        print("Passo:", machine.phase, machine.get_tape_contents())

    print("Depois:", machine.get_tape_contents())
    print("Estado atual:", machine.state.name)
    print("Fase atual:", machine.phase)
    print("Terminou a computação?", machine.has_finished())
    print("Foi aceita?", machine.is_accepted())
