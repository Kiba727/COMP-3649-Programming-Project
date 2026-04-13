# liveness.py
# Week 4: Liveness Analysis Logic

from threeAddress import IntermediateCode, ThreeAddressInstruction

class LiveRange:
    """
    Represents the lifespan of a variable.
    - start: The line where the variable is assigned a value.
    - end: The first line where the variable is no longer needed.
    """
    def __init__(self, var_name, start_line, end_line):
        self.var_name = var_name
        self.start_line = start_line 
        self.end_line = end_line      
        
    def overlaps_with(self, other):
        """
        Checks if this variable's lifespan overlaps with another variable's lifespan.
        If they overlap, they cannot share the same CPU register.
        
        Range A overlaps Range B if A starts before B ends, AND B starts before A ends.
        """
        return (self.start_line < other.end_line and other.start_line < self.end_line)
        
    def __repr__(self):
        # The bracket '[' means the start line is included
        # The parenthesis ')' means the end line is not included
        return f"{self.var_name}[{self.start_line}, {self.end_line})"
        
    def __str__(self):
        return self.__repr__()

class LivenessAnalyzer:
    def __init__(self, code):
        self.code = code
        self.liveness_results = []
        self.live_at_entry = set()
        self.live_ranges = {} 
        self.dead_definitions = []

    def analyze(self):
        """
        Coordinates the backward scan to determine live ranges.
        """
        num_instr = len(self.code.instructions)
        var_range_ends = {var: num_instr + 1 for var in self.code.live_on_exit}
        current_live_vars = set(self.code.live_on_exit)
        results = [None] * num_instr

        # Backward loop
        for i in range(num_instr - 1, -1, -1):
            line_num = i + 1
            results[i] = current_live_vars.copy()
            instr = self.code.instructions[i]

            # Process definition and uses separately
            self._process_instruction_def(instr, line_num, current_live_vars, var_range_ends)
            self._process_instruction_uses(instr, line_num, current_live_vars, var_range_ends)
        
        self._finalize_analysis(current_live_vars, var_range_ends, results)
        return results

    def _process_instruction_def(self, instr, line_num, current_live, range_ends):
        """
        Handles the variable being defined (left side of the equals).
        """
        defined_var = instr.get_defined_variable()
        if not defined_var:
            return

        if defined_var in current_live:
            # Mark start of live range, the variable is dead before this line
            self._add_live_range(defined_var, line_num, range_ends[defined_var])
            current_live.remove(defined_var)
            del range_ends[defined_var]
        else:
            # Variable defined but not currently live is a dead definition
            self.dead_definitions.append((line_num, defined_var))

    def _process_instruction_uses(self, instr, line_num, current_live, range_ends):
        """
        Handles variables being used on the right side of the equals sign.
        """
        for var in instr.get_used_variables():
            if var not in current_live:
                # First time seeing a var used (scanning backward) is its 'end' line
                current_live.add(var)
                range_ends[var] = line_num + 1

    def _finalize_analysis(self, current_live, range_ends, results):
        """
        Handles variables live at entry and saves final results.
        """
        for var in current_live:
            self._add_live_range(var, 0, range_ends[var])
            
        self.live_at_entry = current_live
        self.liveness_results = results

    def _add_live_range(self, var_name, start, end):
        """Helper to create and store a LiveRange object."""
        if var_name not in self.live_ranges:
            self.live_ranges[var_name] = []
        self.live_ranges[var_name].append(LiveRange(var_name, start, end))

    def print_liveness(self):
        print("\n--- Liveness Analysis Results ---")
        
        print("Live Ranges [Start, End):")
        for var in sorted(self.live_ranges.keys()):
            ranges = self.live_ranges[var]
            range_str = ", ".join([str(r) for r in ranges])
            print(f"  {var}: {range_str}")
            
        if self.dead_definitions:
            print("\nDead Definitions (Superfluous Code):")
            for line, var in sorted(self.dead_definitions):
                print(f"  Line {line}: defines '{var}' (never used)")
            
        print("---------------------------------\n")

# Test code
if __name__ == "__main__":
    print("Testing LivenessAnalyzer")
    
    print("--- Test Case 1: Dead Definition ---")
    code1 = IntermediateCode()
    code1.add_instruction(ThreeAddressInstruction("a", "5", None, None))
    code1.add_instruction(ThreeAddressInstruction("x", "100", None, None)) # x is never used
    code1.add_instruction(ThreeAddressInstruction("b", "a", "+", "1"))
    code1.set_live_on_exit(["b"])
    
    analyzer1 = LivenessAnalyzer(code1)
    analyzer1.analyze()
    analyzer1.print_liveness()

    print("--- Test Case 2: Full Program ---")
    code2 = IntermediateCode()
    code2.add_instruction(ThreeAddressInstruction("a", "a", "+", "1"))     # 1
    code2.add_instruction(ThreeAddressInstruction("t1", "a", "*", "4"))    # 2
    code2.add_instruction(ThreeAddressInstruction("t2", "t1", "+", "1"))   # 3
    code2.add_instruction(ThreeAddressInstruction("t3", "a", "*", "3"))    # 4
    code2.add_instruction(ThreeAddressInstruction("b", "t2", "-", "t3"))   # 5
    code2.add_instruction(ThreeAddressInstruction("t4", "b", "/", "2"))    # 6
    code2.add_instruction(ThreeAddressInstruction("d", "c", "+", "t4"))    # 7
    code2.set_live_on_exit(["d"])
    
    analyzer2 = LivenessAnalyzer(code2)
    analyzer2.analyze()
    analyzer2.print_liveness()