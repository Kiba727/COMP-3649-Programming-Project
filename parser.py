# parser.py
# Week 3 input file parsing logic

import sys
from threeAddress import ThreeAddressInstruction, IntermediateCode
from parserHelper import parseLiveLine, isValidVariable, isValidOperand


def readIntermediateCode(filename):
    """
    Primary parsing routine: reads and parses an entire input file.
    
    Args:
        filename: path to input file
        
    Returns:
        IntermediateCode object on success, None on error
    """
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found", file=sys.stderr)
        return None
    except IOError as e:
        print(f"Error: Could not read file '{filename}': {e}", file=sys.stderr)
        return None
    
    if len(lines) == 0:
        print("Error: Input file is empty", file=sys.stderr)
        return None
    
    # Create intermediate code container
    code = IntermediateCode()
    
    # Calculate the index of the last line so we know where to stop
    # We want to process everything up to the last line, but not the last line itself.
    last_line_index = len(lines) - 1

    # Loop from 0 up to but not including the last_line_index
    for i in range(last_line_index):
        line = lines[i]       # Get the line at the current index
        line_num = i + 1      # Calculate the human-readable line number (starts at 1)

        instr = read3AddrInstruction(line, line_num)
        
        if instr is None:
            return None  # Error already printed by read3AddrInstruction
            
        code.add_instruction(instr)
    
    # Parse the last line (live-on-exit variables)
    live_vars = parseLiveLine(lines[-1], len(lines))
    if live_vars is None:
        return None  # Error already printed by parseLiveLine
    
    code.set_live_on_exit(live_vars)
    
    return code


def read3AddrInstruction(line, line_num):
    """
    Parses a single line of three-address code.
    
    Args:
        line: string containing one instruction
        line_num: line number for error messages
        
    Returns:
        ThreeAddressInstruction object on success, None on error
    """
    # Remove leading/trailing whitespace
    line = line.strip()
    
    # Skip empty lines
    if not line:
        print(f"Error on line {line_num}: Empty line", file=sys.stderr)
        return None
    
    # Split by whitespace (handles multiple spaces/tabs)
    tokens = line.split()
    
    # Valid instruction format: dst = src1 [op src2]
    # Minimum: 3 tokens (dst = src)
    # Maximum: 5 tokens (dst = src1 op src2)
    
    if len(tokens) < 3:
        print(f"Error on line {line_num}: Less than 3 tokens on line", file=sys.stderr)
        return None
    
    if len(tokens) > 5:
        print(f"Error on line {line_num}: More than 5 tokens on line", file=sys.stderr)
        return None
    
    # Extract destination
    dst = tokens[0]
    if not isValidVariable(dst):
        print(f"Error on line {line_num}: Invalid destination variable '{dst}'", file=sys.stderr)
        return None
    
    # Check for equals sign
    if tokens[1] != '=':
        print(f"Error on line {line_num}: Missing '=' sign", file=sys.stderr)
        return None
    
    # Parse based on number of remaining tokens
    # Simple assignment: dst = src
    if len(tokens) == 3:
        src = tokens[2]
        if not isValidOperand(src):
            print(f"Error on line {line_num}: Invalid operand '{src}'", file=sys.stderr)
            return None
        return ThreeAddressInstruction(dst, src, None, None)
    
    # Unary negation: dst = -src
    elif len(tokens) == 4:
        if tokens[2] != '-':
            print(f"Error on line {line_num}: Missing '-' negation sign", file=sys.stderr)
            return None
        src = tokens[3]
        if not isValidOperand(src):
            print(f"Error on line {line_num}: Invalid operand '{src}'", file=sys.stderr)
            return None
        return ThreeAddressInstruction(dst, src, '-', None)
    
    # Binary operation: dst = src1 op src2
    elif len(tokens) == 5:
        src1 = tokens[2]
        op = tokens[3]
        src2 = tokens[4]
        
        if not isValidOperand(src1):
            print(f"Error on line {line_num}: Invalid operand '{src1}'", file=sys.stderr)
            return None
        
        if op not in ['+', '-', '*', '/']:
            print(f"Error on line {line_num}: Invalid operator '{op}' (expected +, -, *, or /)", file=sys.stderr)
            return None
        
        if not isValidOperand(src2):
            print(f"Error on line {line_num}: Invalid operand '{src2}'", file=sys.stderr)
            return None
        
        return ThreeAddressInstruction(dst, src1, op, src2)
    
    # Should not reach here
    return None


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
