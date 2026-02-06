# threeAddress.py
# Week 3 intermediate-code data structures + support routines

class ThreeAddressInstruction:
    """
    Represents a single three-address instruction.
    
    3 Cases:
      - dst = src1 op src2  (binary operation)
      - dst = -src          (unary negation)
      - dst = src           (simple assignment)
    
    Where:
      - dst: destination variable
      - src, src1, src2: source operand (variable or literal)
      - op: operator (+, -, *, /)
    """
    def __init__(self, dst, src1, op=None, src2=None):
        self.dst = dst     
        self.src1 = src1   
        self.op = op       
        self.src2 = src2   
    
    def is_binary(self):
        """Returns True if this is a binary operation (dst = src1 op src2)"""
        return self.op is not None and self.src2 is not None
    
    def is_unary_negation(self):
        """Returns True if this is unary negation (dst = -src)"""
        return self.op == '-' and self.src2 is None
    
    def is_assignment(self):
        """Returns True if this is simple assignment (dst = src)"""
        return self.op is None and self.src2 is None
    
    def get_used_variables(self):
        """Returns a list of all variables used by this instruction"""
        used = []
        
        # Check src1 
        if self._is_variable(self.src1):
            used.append(self.src1)
        
        # Check src2 if applicable
        if self.src2 is not None and self._is_variable(self.src2):
            used.append(self.src2)
        
        return used
    
    def get_defined_variable(self):
        """Returns the variable defined by this instruction"""
        return self.dst
    
    def _is_variable(self, operand):
        """Helper to check if an operand is a variable, not a literal"""
        if isinstance(operand, str):
            # Try to parse as integer literal
            try:
                int(operand)
                return False
            except ValueError:
                return True
        return False
    
    def __repr__(self):
        """String representation for debugging"""
        if self.is_binary():
            return f"{self.dst} = {self.src1} {self.op} {self.src2}"
        elif self.is_unary_negation():
            return f"{self.dst} = -{self.src1}"
        else:  # is_assignment
            return f"{self.dst} = {self.src1}"
    
    def __str__(self):
        """String representation"""
        return self.__repr__()


class IntermediateCode:
    """
    Represents a sequence of three-address instructions plus live-on-exit variables.
    """
    def __init__(self):
        self.instructions = []
        self.live_on_exit = []
    
    def add_instruction(self, instruction):
        """Add a three-address instruction to the sequence"""
        if not isinstance(instruction, ThreeAddressInstruction):
            raise TypeError("Not ThreeAddressInstruction Type")
        self.instructions.append(instruction)
    
    def set_live_on_exit(self, variables):
        """Set the list of variables that are live on exit"""
        self.live_on_exit = variables
    
    def get_all_variables(self):
        """Returns a set of all variables mentioned in the code"""
        variables = set()
        for instr in self.instructions:
            variables.add(instr.get_defined_variable())
            for var in instr.get_used_variables():
                variables.add(var)
        return variables
    
    def validate_live_on_exit(self):
        """
        Validates that all live-on-exit variables appear in the code.
        Returns (is_valid, error_message).
        """
        all_vars = self.get_all_variables()
        for var in self.live_on_exit:
            if var not in all_vars:
                return False, f"Variable '{var}' listed as live but does not appear in code"
        return True, None
    
    def __len__(self):
        """Returns the number of instructions"""
        return len(self.instructions)
    
    def __repr__(self):
        """String representation showing all instructions and live variables"""
        lines = []
        for instr in self.instructions:
            lines.append(str(instr))
        lines.append(f"live: {', '.join(self.live_on_exit) if self.live_on_exit else '(none)'}")
        return '\n'.join(lines)
    
    def __str__(self):
        """User-friendly string representation"""
        return self.__repr__()


# Test code - runs when module is executed directly
if __name__ == "__main__":
    print("Testing ThreeAddressInstruction and IntermediateCode classes...")
    print()
    
    # Test case 1: Binary operation
    instr1 = ThreeAddressInstruction("a", "a", "+", "1")
    print(f"Binary operation: {instr1}")
    print(f"  Used vars: {instr1.get_used_variables()}")
    print(f"  Defined var: {instr1.get_defined_variable()}")
    print()
    
    # Test case 2: Unary negation
    instr2 = ThreeAddressInstruction("b", "a", "-", None)
    print(f"Unary negation: {instr2}")
    print(f"  Used vars: {instr2.get_used_variables()}")
    print(f"  Defined var: {instr2.get_defined_variable()}")
    print()
    
    # Test case 3: Simple assignment
    instr3 = ThreeAddressInstruction("c", "10", None, None)
    print(f"Assignment: {instr3}")
    print(f"  Used vars: {instr3.get_used_variables()}")
    print(f"  Defined var: {instr3.get_defined_variable()}")
    print()
    
    # Test case 4: Full intermediate code sequence
    code = IntermediateCode()
    code.add_instruction(ThreeAddressInstruction("a", "a", "+", "1"))
    code.add_instruction(ThreeAddressInstruction("t1", "a", "*", "4"))
    code.add_instruction(ThreeAddressInstruction("t2", "t1", "+", "1"))
    code.add_instruction(ThreeAddressInstruction("t3", "a", "*", "3"))
    code.add_instruction(ThreeAddressInstruction("b", "t2", "-", "t3"))
    code.add_instruction(ThreeAddressInstruction("t4", "b", "/", "2"))
    code.add_instruction(ThreeAddressInstruction("d", "c", "+", "t4"))
    code.set_live_on_exit(["d"])
    
    print("Full intermediate code sequence:")
    print(code)
    print(f"All variables: {code.get_all_variables()}")
    print(f"Number of instructions: {len(code)}")
    
    # Test validation
    valid, error = code.validate_live_on_exit()
    print(f"Live-on-exit validation: {'PASS' if valid else 'FAIL'}")
    if not valid:
        print(f"  Error: {error}")
