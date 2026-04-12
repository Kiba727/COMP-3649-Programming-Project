# assemblyInstructions.py
from enum import Enum

class Opcode(Enum): 
    """Creates a binary operation instruction (5-token case: dst = src1 op src2)."""
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    MOV = "MOV"


class OperandType(Enum): 
    """The three ways a value can be referenced in an instruction: literal, register, or memory."""
    IMMEDIATE = 1   # #5
    VARIABLE = 2    # a, b, t1
    REGISTER = 3    # R0, R1, ...


class Operand: 
    """Pairs an operand type with its value, e.g. (Register, 0) represents R0."""
    def __init__(self, operand_type, value):
        self.type = operand_type
        self.value = value

    def __repr__(self):
        if self.type == OperandType.IMMEDIATE:
            return f"#{self.value}"
        if self.type == OperandType.REGISTER:
            return f"R{self.value}"
        if self.type == OperandType.VARIABLE:
            return str(self.value)
        return f"<Operand {self.type} {self.value}>"


class AssemblyInstruction:
    """
    Represents one target instruction, e.g.:
      MOV a,R0
      ADD #1,R0
      MOV R0,a
    """
    def __init__(self, opcode, src, dst):
        self.opcode = opcode      # Opcode
        self.src = src            # Operand
        self.dst = dst            # Operand

    def __repr__(self):
        return f"{self.opcode.value} {self.src},{self.dst}"


class TargetCode:
    """Represents a target code sequence (list of AssemblyInstruction)."""
    def __init__(self):
        self.instructions = []

    def add(self, instr): 
        """Appends a single assembly instruction to the sequence."""
        self.instructions.append(instr)

    def extend(self, instr_list): 
        """Appends a list of assembly instructions to the sequence."""
        for i in instr_list:
            self.add(i)

    def __repr__(self):
        return "\n".join([repr(i) for i in self.instructions])

    def write_to_file(self, filename): 
        """Writes the full assembly sequence to a text file."""
        with open(filename, "w") as f:
            f.write(repr(self) + "\n") 
            

if __name__ == "__main__":
    prog = TargetCode()
    prog.add(AssemblyInstruction(
        Opcode.MOV,
        Operand(OperandType.VARIABLE, "a"),
        Operand(OperandType.REGISTER, 0)
    ))
    prog.add(AssemblyInstruction(
        Opcode.ADD,
        Operand(OperandType.IMMEDIATE, 1),
        Operand(OperandType.REGISTER, 0)
    ))
    prog.add(AssemblyInstruction(
        Opcode.MOV,
        Operand(OperandType.REGISTER, 0),
        Operand(OperandType.VARIABLE, "a")
    ))
    print(prog)

