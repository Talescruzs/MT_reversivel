from tape import Tape
from transition import ActionType, TapeAction, Transition


class TuringMachineReversive:
    def __init__(self, input_string: str, initial_state: str = "q0"):
        self.tape1 = Tape()
        self.tape2 = Tape()
        self.tape3 = Tape()

        self.state = initial_state
        self.halted = False
        self.transitions: list[Transition] = []
        self.final_states: set[str] = set()

        # Carrega a entrada na primeira fita e volta o cabeçote para o início.
        for char in input_string:
            self.tape1.write(char)
            self.tape1.move_right()

        for _ in range(len(input_string)):
            self.tape1.move_left()

    def add_transition(self, transition: Transition) -> None:
        self.transitions.append(transition)

    def add_final_state(self, state: str) -> None:
        self.final_states.add(state)

    def is_final_state(self) -> bool:
        return self.state in self.final_states

    def has_halted(self) -> bool:
        return self.halted

    def has_finished(self) -> bool:
        return self.halted or self.is_final_state()

    def is_accepted(self) -> bool:
        return self.has_finished() and self.is_final_state()

    def get_tape_contents(self):
        return self.tape1.get_tape(), self.tape2.get_tape(), self.tape3.get_tape()

    def _current_symbols(self) -> tuple[str | None, str | None, str | None]:
        return self.tape1.read(), self.tape2.read(), self.tape3.read()

    def _apply_action(self, tape: Tape, action: TapeAction) -> None:
        if action.type == ActionType.WRITE:
            tape.write(action.write)
            return

        if action.delta is None:
            raise ValueError("MOVE action precisa de delta")

        if action.delta > 0:
            for _ in range(action.delta):
                tape.move_right()
        elif action.delta < 0:
            for _ in range(-action.delta):
                tape.move_left()

    def step(self) -> bool:
        if self.has_finished():
            return False

        if self.is_final_state():
            self.halted = True
            return False

        scanned = self._current_symbols()

        for transition in self.transitions:
            if not transition.matches(self.state, scanned):
                continue

            for tape, action in zip((self.tape1, self.tape2, self.tape3), transition.actions):
                self._apply_action(tape, action)

            self.state = transition.next_state
            if self.is_final_state():
                self.halted = True
            return True

        self.halted = True
        return False

    def run(self, max_steps: int = 100) -> int:
        steps = 0
        while steps < max_steps and not self.has_finished() and self.step():
            steps += 1
        return steps


if __name__ == "__main__":
    # Teste simples do núcleo inicial da máquina reversível.
    machine = TuringMachineReversive("abc")
    machine.add_final_state("q1")

    machine.add_transition(
        Transition(
            state="q0",
            expected=("a", None, None),
            actions=(
                TapeAction.write_action("a", "x"),
                TapeAction.move_action(-1),
                TapeAction.move_action(-1),
            ),
            next_state="q1",
        )
    )

    print("Antes:", machine.get_tape_contents())
    machine.step()
    print("Depois:", machine.get_tape_contents())
    print("Estado atual:", machine.state)
    print("Terminou a computação?", machine.has_finished())
    print("Está em estado final?", machine.is_final_state())
    print("Foi aceita?", machine.is_accepted())
