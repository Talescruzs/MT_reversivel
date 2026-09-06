from tape import Tape

class turingMachineReversive:
    def __init__(self, input_string):
        self.tape1 = Tape()
        self.tape2 = Tape()
        self.tape3 = Tape()

        for char in input_string:
            self.tape1.write(char)
            self.tape1.move_right()

    def get_tape_contents(self):
        return self.tape1.get_tape(), self.tape2.get_tape(), self.tape3.get_tape()

if __name__ == "__main__":
    # Testando a classe turingMachineReversive
    input_string = "abc"
    machine = turingMachineReversive(input_string)
    tape1_contents, tape2_contents, tape3_contents = machine.get_tape_contents()
    print("Tape 1 contents:", tape1_contents)  # Output: ['a', 'b', 'c']
    print("Tape 2 contents:", tape2_contents)  # Output: []
    print("Tape 3 contents:", tape3_contents)  # Output: []
