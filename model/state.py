from transition import Transition

class State:
    def __init__(self, name: str, transitions: list[Transition] | None = None, is_final: bool = False, is_initial: bool = False):
        self.name = name
        self.transitions = list(transitions) if transitions is not None else []
        self.is_final = is_final
        self.is_initial = is_initial

    def get_next_transition(self, read_symbol: str | None) -> Transition | None:
        for transition in self.transitions:
            if transition.read == read_symbol:
                return transition
        return None

    def add_transition(self, transition: Transition):
        self.transitions.append(transition)

    def set_transitions(self, transitions: list[Transition]):
        self.transitions = transitions