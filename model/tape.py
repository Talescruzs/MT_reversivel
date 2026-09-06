class Tape:
    def __init__(self):
        self._tape = []
        self._position = 0

    def write(self, value):
        if self._position < len(self._tape):
            self._tape[self._position] = value
        else:
            self._tape.append(value)

    def read(self):
        if self._position < len(self._tape):
            return self._tape[self._position]
        return None

    def move_left(self):
        if self._position > 0:
            self._position -= 1

    def move_right(self):
        self._position += 1
        if(self._position >= len(self._tape)):
            self._tape.append(None)  # Adiciona None se mover para a direita além do tamanho atual da fita

    def dont_move(self):
        # não é necessário, mas vai ajudar a entender depois
        pass

    def get_tape(self):
        return self._tape

    def get_position(self):
        return self._position

if __name__ == "__main__":
    # Testando a classe Tape
    tape = Tape()
    tape.write(1)
    tape.move_right()
    tape.write(2)
    tape.move_left()
    print(tape.read())  # Output: 1
    tape.move_right()
    print(tape.read())  # Output: 2
    print(tape.get_tape())  # Output: [1, 2]
    print(tape.get_position())  # Output: 1
    tape.write(3)
    print(tape.get_tape())  # Output: [1, 3]
    tape.move_right()
    print(tape.read())  # Output: None
    print(tape.get_tape())  # Output: [1, 3, None]
    tape.move_right()
    tape.write(4)
    print(tape.get_tape())  # Output: [1, 3, None, 4]