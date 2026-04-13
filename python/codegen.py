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
    Main router for converting intermediate code into assembly instructions.
    """
    target = TargetCode()

    # 1. Handle entry: load variables from memory 
    _load_live_on_entry(target, live_on_entry, allocations)

    # 2. Translate each instruction
    for instr in intermediate_code.instructions:
        _translate_instruction(target, instr, allocations)

    # 3. Handle exit: store live variables to memory 
    _store_live_on_exit(target, intermediate_code.live_on_exit, allocations)

    return target

def _load_live_on_entry(target, live_on_entry, allocations):
    """Emits MOV instructions for variables live upon block entry."""
    for var in sorted(live_on_entry):
        if var in allocations:
            target.add(AssemblyInstruction(
                Opcode.MOV,
                Operand(OperandType.VARIABLE, var),
                Operand(OperandType.REGISTER, allocations[var])
            ))

def _translate_instruction(target, instr, allocations):
    """Translates a single Three Address Code Instruction into one or more assembly instructions."""
    # Skip dead definitions (Requirement: no register allocated)
    if instr.dst not in allocations:
        return

    dst_reg = Operand(OperandType.REGISTER, allocations[instr.dst])

    if instr.is_binary():
        # dst = src1 op src2
        src1 = make_operand(instr.src1, allocations)
        src2 = make_operand(instr.src2, allocations)
        target.add(AssemblyInstruction(Opcode.MOV, src1, dst_reg))
        target.add(AssemblyInstruction(_OP_MAP[instr.op], src2, dst_reg))

    elif instr.is_unary_negation():
        # dst = 0 - src => -src
        src = make_operand(instr.src1, allocations)
        target.add(AssemblyInstruction(Opcode.MOV, Operand(OperandType.IMMEDIATE, "0"), dst_reg))
        target.add(AssemblyInstruction(Opcode.SUB, src, dst_reg))

    else:
        # dst = src (simple assignment)
        src = make_operand(instr.src1, allocations)
        target.add(AssemblyInstruction(Opcode.MOV, src, dst_reg))

def _store_live_on_exit(target, live_on_exit, allocations):
    """Emits MOV instructions to store live-on-exit variables back to memory."""
    for var in sorted(live_on_exit):
        if var in allocations:
            target.add(AssemblyInstruction(
                Opcode.MOV,
                Operand(OperandType.REGISTER, allocations[var]),
                Operand(OperandType.VARIABLE, var)
            ))