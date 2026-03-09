# codegen.py
# Week 6: Generate assembly from three-address code

from assemblyInstructions import (
    TargetCode,
    AssemblyInstruction,
    Operand,
    OperandType,
    Opcode
)

_OP_MAP = {
    "+": Opcode.ADD,
    "-": Opcode.SUB,
    "*": Opcode.MUL,
    "/": Opcode.DIV,
}


def make_operand(value, allocations):
    """Converts a variable name or integer literal into an Operand."""
    try:
        int(value)
        return Operand(OperandType.IMMEDIATE, value)
    except ValueError:
        pass
    return Operand(OperandType.REGISTER, allocations[value])


def generate_target_code(intermediate_code, allocations, live_on_entry):
    """
    Converts three-address instructions into assembly instructions.
    Emits a prologue to load live-on-entry variables from memory,
    translates each instruction, then emits an epilogue to store
    live-on-exit variables back to memory.
    """
    target = TargetCode()

    # load live-on-entry variables from memory
    for var in sorted(live_on_entry):
        if var in allocations:
            target.add(AssemblyInstruction(
                Opcode.MOV,
                Operand(OperandType.VARIABLE, var),
                Operand(OperandType.REGISTER, allocations[var])
            ))

    for instr in intermediate_code.instructions:
        # Skip dead definitions (no register allocated)
        if instr.dst not in allocations:
            continue

        dst = Operand(OperandType.REGISTER, allocations[instr.dst])

        if instr.is_binary():
            src1 = make_operand(instr.src1, allocations)
            src2 = make_operand(instr.src2, allocations)
            target.add(AssemblyInstruction(Opcode.MOV, src1, dst))
            target.add(AssemblyInstruction(_OP_MAP[instr.op], src2, dst))

        elif instr.is_unary_negation():
            # dst = 0 - src => -src
            src = make_operand(instr.src1, allocations)
            target.add(AssemblyInstruction(Opcode.MOV, Operand(OperandType.IMMEDIATE, "0"), dst))
            target.add(AssemblyInstruction(Opcode.SUB, src, dst))

        else:
            src = make_operand(instr.src1, allocations)
            target.add(AssemblyInstruction(Opcode.MOV, src, dst))

    # store live-on-exit variables back to memory
    for var in sorted(intermediate_code.live_on_exit):
        if var in allocations:
            target.add(AssemblyInstruction(
                Opcode.MOV,
                Operand(OperandType.REGISTER, allocations[var]),
                Operand(OperandType.VARIABLE, var)
            ))

    return target