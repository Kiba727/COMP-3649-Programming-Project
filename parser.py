# parser.py
# Week 3 input file parsing logic

import sys
from threeAddress import ThreeAddressInstruction, IntermediateCode
from parserHelper import parseLiveLine, isValidVariable, isValidOperand

def readIntermediateCode(filename):
    """Reads and parses input file into an IntermediateCode object."""
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except (FileNotFoundError, IOError) as e:
        print(f"Error reading file '{filename}': {e}", file=sys.stderr)
        return None
    
    if not lines:
        print("Error: Input file is empty", file=sys.stderr)
        return None
    
    code = IntermediateCode()
    last_line_index = len(lines) - 1

    # Process all but the last line (instructions)
    for i in range(last_line_index):
        instr = read3AddrInstruction(lines[i], i + 1)
        if instr is None:
            return None 
        code.add_instruction(instr)
    
    # Process the last line (live-on-exit)
    live_vars = parseLiveLine(lines[-1], len(lines))
    if live_vars is None:
        return None  
    
    code.set_live_on_exit(live_vars)
    return code

def read3AddrInstruction(line, line_num):
    """Main router for parsing a single line of TAC."""
    line = line.strip()
    if not line:
        print(f"Error on line {line_num}: Empty line", file=sys.stderr)
        return None
    
    tokens = line.split()
    if not (3 <= len(tokens) <= 5):
        print(f"Error on line {line_num}: Invalid token count", file=sys.stderr)
        return None
    
    # Validate destination and equals sign
    if not isValidVariable(tokens[0]):
        print(f"Error on line {line_num}: Invalid destination '{tokens[0]}'", file=sys.stderr)
        return None
    if tokens[1] != '=':
        print(f"Error on line {line_num}: Missing '=' sign", file=sys.stderr)
        return None

    return _parse_by_token_count(tokens, line_num)

def _parse_by_token_count(tokens, line_num):
    """Helper to delegate parsing based on the number of tokens."""
    dst = tokens[0]
    
    if len(tokens) == 3:
        # Case 1: dst = src
        return _create_assignment(dst, tokens[2], line_num)
    
    elif len(tokens) == 4:
        # Case 2: dst = -src
        return _create_unary(dst, tokens[2], tokens[3], line_num)
    
    elif len(tokens) == 5:
        # Case 3: dst = src1 op src2
        return _create_binary(dst, tokens[2], tokens[3], tokens[4], line_num)
    
    return None

def _create_assignment(dst, src, line_num):
    # Check for compact unary negation: dst = -src
    if src.startswith('-') and len(src) > 1:
        operand = src[1:]
        if not isValidOperand(operand):
            print(f"Error on line {line_num}: Invalid operand '{operand}'", file=sys.stderr)
            return None
        return ThreeAddressInstruction(dst, operand, '-', None)
    
    if not isValidOperand(src):
        print(f"Error on line {line_num}: Invalid operand '{src}'", file=sys.stderr)
        return None
    return ThreeAddressInstruction(dst, src, None, None)

def _create_unary(dst, op, src, line_num):
    if op != '-':
        print(f"Error on line {line_num}: Expected '-' negation", file=sys.stderr)
        return None
    if not isValidOperand(src):
        print(f"Error on line {line_num}: Invalid operand '{src}'", file=sys.stderr)
        return None
    return ThreeAddressInstruction(dst, src, '-', None)

def _create_binary(dst, src1, op, src2, line_num):
    if not isValidOperand(src1) or not isValidOperand(src2):
        print(f"Error on line {line_num}: Invalid operand(s)", file=sys.stderr)
        return None
    if op not in ['+', '-', '*', '/']:
        print(f"Error on line {line_num}: Invalid operator '{op}'", file=sys.stderr)
        return None
    return ThreeAddressInstruction(dst, src1, op, src2)


# Test cases for parser module
if __name__ == "__main__":
    # Test valid variable names
    print("Testing variable validation:")
    test_vars = ["a", "b", "z", "t", "t1", "t23", "t100", "A", "ab", "1", "t", "tt"]
    for var in test_vars:
        result = isValidVariable(var)
        print(f"  '{var}': {result}")
    print()
    
    # Test valid operands
    print("Testing operand validation:")
    test_ops = ["a", "t1", "5", "-10", "abc", "1.5"]
    for op in test_ops:
        result = isValidOperand(op)
        print(f"  '{op}': {result}")
    print()
    
    # Test instruction parsing
    print("Testing instruction parsing:")
    test_lines = [
        ("a = a + 1", 1),
        ("t1 = a * 4", 2),
        ("b = t2 - t3", 3),
        ("x = 10", 4),
        ("y = -a", 5),
        ("invalid line", 6)
    ]
    for line, num in test_lines:
        instr = read3AddrInstruction(line, num)
        if instr:
            print(f"  Line {num}: {instr}")
        else:
            print(f"  Line {num}: Parsing Error")
    print()
    
    # Test live line parsing
    print("Testing live line parsing:")
    test_lives = [
        ("live: d", 1),
        ("live: a, b, c", 2),
        ("live:", 3),
        ("live: t1, t2", 4)
    ]
    for line, num in test_lives:
        result = parseLiveLine(line, num)
        print(f"  '{line}': {result}")
