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
    """
    Scans through our code to figure out exactly when variables are used and are no longer used.
    """
    def __init__(self, code):
        self.code = code
        
        # Stores the set of alive variables for each line of code. This is what we will return at the end.
        self.liveness_results = []
        
        # Variables used before line 1 in the input file
        self.live_at_entry = set()
        
        # Dictionary to track the exact Start and End lines for every variable.
        # Key: variable name (e.g., 'a'), Value: list of LiveRange objects (e.g., [a[1, 5), a[10, 12)])
        self.live_ranges = {} 
        
        # Tracks variables that are created but never actually used.
        self.dead_definitions = []

    def analyze(self):
        """
        Runs the backward scan to determine the live ranges as used variables will always exist before their definitions.
        If a variable is used, but we haven't seen its definition yet, we know it must be alive at the start of the program. 
        If a variable is defined, but we never see it being used, then it is a dead definition and can be removed from the code.
        """
        num_instructions = len(self.code.instructions)
        
        # A dictionary to remember the exact line where a variable is last used.
        var_range_ends = {} 
        
        # Start reading backwards from the bottom of the file.
        # Grab the variables from the "live:" line at the bottom of the file.
        current_live_vars = set(self.code.live_on_exit)
        
        for var in self.code.live_on_exit:
            var_range_ends[var] = num_instructions + 1
            
        # Holds the liveness variables for each line.
        results = [None] * num_instructions

        # Loop backwards from the bottom line to the top
        for i in range(num_instructions - 1, -1, -1):
            line_num = i + 1  # 1-indexed
            
            # Save the current list of alive variables for this specific line
            results[i] = current_live_vars.copy()

            instr = self.code.instructions[i]
            
            # Left side of the equals sign where a variable is defined
            defined_var = instr.get_defined_variable()
            
            # Checks if the definied variable is currently used. If it is, we can mark the end of its live range at this line.
            if defined_var in current_live_vars:
                start = line_num
                end = var_range_ends[defined_var]
                self._add_live_range(defined_var, start, end)
                
                # Since we are scanning backwards, this line is the last time this variable is used in the program.
                current_live_vars.remove(defined_var)
                del var_range_ends[defined_var]

            # If the variable defined on this line is not currently used, it means it is a dead definition. We can mark it for removal.
            elif defined_var is not None:
                self.dead_definitions.append((line_num, defined_var))
                
            # Any variables used on the right side of the equals sign must been used.
            used_vars = instr.get_used_variables()
            
            for var in used_vars:
                # When scanning backwards, the first time we see a variable used is its actual "last use".
                # This line marks the end of its lifespan.
                if var not in current_live_vars:
                    current_live_vars.add(var)
                    var_range_ends[var] = line_num + 1  # +1: end is exclusive, include last-use line
        
        # Handle variables that are used at the start of a line but never defined.
        for var in current_live_vars:
            start = 0 
            end = var_range_ends[var]
            self._add_live_range(var, start, end)
            
        # Save our final results
        self.live_at_entry = current_live_vars
        self.liveness_results = results

        return results

    def _add_live_range(self, var_name, start, end):
        """Helper to create a LiveRange object and add it to our dictionary."""
        if var_name not in self.live_ranges:
            self.live_ranges[var_name] = []
        
        new_range = LiveRange(var_name, start, end)
        self.live_ranges[var_name].append(new_range)

    def print_liveness(self):
        """Prints the results in a clean, readable format for testing."""
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
    
    # Test Case with a dead definition
    # 1: a = 5
    # 2: x = 100   
    # 3: b = a + 1
    # live: b
    """"
    code = IntermediateCode()
    code.add_instruction(ThreeAddressInstruction("a", "5", None, None))
    code.add_instruction(ThreeAddressInstruction("x", "100", None, None)) 
    code.add_instruction(ThreeAddressInstruction("b", "a", "+", "1"))
    code.set_live_on_exit(["b"])
    """""
    code = IntermediateCode()
    code.add_instruction(ThreeAddressInstruction("a", "5", None, None))
    code.add_instruction(ThreeAddressInstruction("x", "100", None, None)) 
    code.add_instruction(ThreeAddressInstruction("b", "a", "+", "1"))
    code.set_live_on_exit(["b"])
    #code = IntermediateCode()
    #code.add_instruction(ThreeAddressInstruction("a", "a", "+", "1"))
    #code.add_instruction(ThreeAddressInstruction("t1", "a", "*", "4"))
    #code.add_instruction(ThreeAddressInstruction("t2", "t1", "+", "1"))
    #code.add_instruction(ThreeAddressInstruction("t3", "a", "*", "3"))
    #code.add_instruction(ThreeAddressInstruction("a", "5"))
    #code.add_instruction(ThreeAddressInstruction("b", "a", "+", "1"))
    #code.add_instruction(ThreeAddressInstruction("c", "b", "*", "2"))
    #code.set_live_on_exit(["c"])
    
    analyzer = LivenessAnalyzer(code)
    analyzer.analyze()
    analyzer.print_liveness()