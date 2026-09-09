from __future__ import annotations

from enum import Enum, auto

from tape import Tape
from transition import BennettTransition, HistoryTapeSymbol


class MachinePhase(Enum):
    FORWARD = auto()    # fase de execução normal da máquina de Turing reversiva
    COPY = auto()       # fase de cópia do conteúdo da fita 1 para a fita 3
    RETRACE = auto()    # fase de retrocesso da máquina de Turing reversiva, usando a fita 2 como histórico
    HALT = auto()       # fase de parada da máquina de Turing reversiva


class TuringMachineReversive:
    def __init__(
        self,
        input_string: str,
        initial_state: str = "q0",
        transitions: list[BennettTransition] | None = None,
        final_states: set[str] | None = None
    ):
        self.tape1 = Tape()     #input tape
        self.tape2 = Tape()     #history tape
        self.tape3 = Tape()     #output tape

        self.initial_state = initial_state
        self.state = initial_state
        self.phase = MachinePhase.FORWARD
        self.accepted = False

        self.transitions = transitions if transitions is not None else []
        self.final_states = final_states if final_states is not None else set()

        self._pending_transition: BennettTransition | None = None
        self._copy_index = 0
        self._history_tokens = 0

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

    def get_tape_histories(self):
        return self.tape2.get_tape()

    def _current_input_symbol(self) -> str | None:
        return self.tape1.read()

    def _find_transition(self) -> BennettTransition | None:
        scanned = self._current_input_symbol()
        for transition in self.transitions:
            if transition.state == self.state and transition.read == scanned:
                return transition
        return None

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

    def _append_history_record(self, kind: str, transition: BennettTransition | None = None) -> None:
        if kind == "transition":
            if transition is None:
                raise ValueError("transition precisa ser informada para registrar histórico")

            tokens = transition.history_tokens()
        elif kind == "final":
            tokens = BennettTransition.final_tokens(self.state)
        else:
            raise ValueError(f"tipo de histórico desconhecido: {kind!r}")

        for token in tokens:
            self.tape2.write(token)
            self.tape2.move_right()

        self._history_tokens += 1

    def _enter_copy_phase(self) -> None:
        self.phase = MachinePhase.COPY
        self._copy_index = 0
        self._pending_transition = None
        self.accepted = True

    def _enter_retrace_phase(self) -> None:
        self.phase = MachinePhase.RETRACE
        self._pending_transition = None
        if self._history_tokens > 0 and self.tape2.get_position() > 0:
            self.tape2.move_left()

    def _forward_step(self) -> bool:
        if self._pending_transition is None:
            transition = self._find_transition()
            if transition is None:
                if self.state in self.final_states:
                    self._append_history_record("final")
                    self._enter_copy_phase()
                    return True
                

                self.phase = MachinePhase.HALT
                return False

            self._pending_transition = transition
            self.tape1.write(transition.write)
            self._append_history_record("transition", transition)
            return True

        transition = self._pending_transition
        self._move_tape(self.tape1, transition.move)
        self.state = transition.next_state
        self._pending_transition = None

        if self.state in self.final_states:
            self._append_history_record("final")
            self._enter_copy_phase()

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

        while self.tape2.read() is None and self.tape2.get_position() > 0:
            self.tape2.move_left()

        if self.tape2.read() != HistoryTapeSymbol.END.value:
            while self.tape2.get_position() > 0 and self.tape2.read() != HistoryTapeSymbol.END.value:
                self.tape2.move_left()

        if self.tape2.read() != HistoryTapeSymbol.END.value:
            raise ValueError("histórico da fita 2 terminou sem marcador de fim de registro")

        record: list[str | None] = []
        while True:
            symbol = self.tape2.read()
            record.append(symbol)
            self.tape2.write(None)
            if symbol == HistoryTapeSymbol.START.value:
                break
            if self.tape2.get_position() == 0:
                break
            self.tape2.move_left()

        record.reverse()

        if len(record) < 4 or record[0] != HistoryTapeSymbol.START.value or record[-1] != HistoryTapeSymbol.END.value:
            raise ValueError(f"registro de histórico inválido: {record!r}")

        tag = record[1]
        if tag == HistoryTapeSymbol.FINAL.value:
            self.state = record[2] if record[2] is not None else self.state
        elif tag == HistoryTapeSymbol.TRANSITION.value:
            state, read_symbol, _write_symbol, move_symbol, _next_state = record[2:7]
            if state is None or read_symbol is None or move_symbol is None:
                raise ValueError(f"registro de transição inválido: {record!r}")

            move = int(move_symbol)
            self._move_tape(self.tape1, -move)
            self.tape1.write(read_symbol)
            self.state = state
        else:
            raise ValueError(f"marca de histórico desconhecida: {tag!r}")

        self._history_tokens -= 1

        if self._history_tokens == 0:
            self.tape2 = Tape()
            self.phase = MachinePhase.HALT
            return True

        if self.tape2.get_position() > 0:
            self.tape2.move_left()

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
            self.step()
            steps += 1
        return steps


if __name__ == "__main__":
    # Exemplo mínimo no formato de Bennett:
    # fase 1: escreve e anda
    # fase 2: copia o resultado para a fita 3
    # fase 3: faz o retrace usando a fita 2
    transitions = [
        BennettTransition("q0", "a", "x", 1, "q1"),
        BennettTransition("q1", "b", "y", 1, "q2"),
        BennettTransition("q2", "c", "z", 1, "q3"),
    ]
    final_states = {"q3"}

    machine = TuringMachineReversive("abc", "q0", transitions, final_states)

    print("Antes:", machine.get_tape_contents())
    while not machine.has_finished():
        machine.step()
        print("Passo:", machine.phase, machine.get_tape_contents())

    print("Depois:", machine.get_tape_contents())
    print("Estado atual:", machine.state)
    print("Fase atual:", machine.phase)
    print("Terminou a computação?", machine.has_finished())
    print("Foi aceita?", machine.is_accepted())
