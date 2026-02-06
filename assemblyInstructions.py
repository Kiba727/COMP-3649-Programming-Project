# assemblyInstructions.py
# Week 3 target-code data structures + support routines (no codegen yet)

from enum import Enum


class Opcode(Enum):
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    MOV = "MOV"


class OperandType(Enum):
    IMMEDIATE = 1   # #5
    VARIABLE = 2    # a, b, t1
    REGISTER = 3    # R0, R1, ...


class Operand:
    def __init__(self, operand_type, value):
        self.type = operand_type
        self.value = value

    def __repr__(self):
        # Print in the exact assembly syntax required by the spec
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
    """
    Represents a target code sequence (list of AssemblyInstruction).
    """
    def __init__(self):
        self.instructions = []

    def add(self, instr):
        self.instructions.append(instr)

    def extend(self, instr_list):
        for i in instr_list:
            self.add(i)

    def __repr__(self):
        return "\n".join([repr(i) for i in self.instructions])

    def write_to_file(self, filename):
        """
        Later (Week 6), you'll use this to write to <filename>.s.
        For now it's safe to include as a support routine.
        """
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

