# liveness.py
# Week 4: Liveness Analysis Logic

from threeAddress import IntermediateCode, ThreeAddressInstruction

class LiveRange:
    """
    Represents a continuous range where a variable is live.
    Range is HALF-OPEN: [start, end)
    - start: The line where the variable is defined (becomes live).
    - end: The first line where the variable is DEAD (no longer needed).
    """
    def __init__(self, var_name, start_line, end_line):
        self.var_name = var_name
        self.start_line = start_line 
        self.end_line = end_line      
        
    def overlaps_with(self, other):
        """
        Check if this live range overlaps with another live range.
        Logic: Range A overlaps Range B if A.start < B.end AND B.start < A.end
        """
        return (self.start_line < other.end_line and other.start_line < self.end_line)
        
    def __repr__(self):
        # UPDATED: Print with bracket-parenthesis to show half-open interval
        return f"{self.var_name}[{self.start_line}, {self.end_line})"
        
    def __str__(self):
        return self.__repr__()


class LivenessAnalyzer:
    """
    Analyzes an IntermediateCode object to find out which variables
    are 'live' at each step, and calculates their specific live ranges.
    """
    def __init__(self, code):
        self.code = code
        
        # Stores the sets of live variables after each instruction
        self.liveness_results = []
        
        # Stores variables live at the very start (before line 1)
        self.live_at_entry = set()
        
        # Dictionary to track live ranges. 
        # Key: variable name, Value: list of LiveRange objects
        self.live_ranges = {} 
        
        # UPDATED: Track dead definitions (assignments that are never used)
        self.dead_definitions = []

    def analyze(self):
        """
        Runs the backward scan to determine liveness and ranges.
        """
        # 1. Setup
        num_instructions = len(self.code.instructions)
        
        # This map tracks the 'End' point of a range.
        var_range_ends = {} 
        
        # Initialize with variables live on exit (they 'end' after the last line)
        current_live_vars = set(self.code.live_on_exit)
        for var in self.code.live_on_exit:
            var_range_ends[var] = num_instructions + 1
            
        results = [None] * num_instructions

        # 2. Backward Scan (From last line up to first)
        for i in range(num_instructions - 1, -1, -1):
            line_num = i + 1
            
            # Save the current state (Live-Out)
            results[i] = current_live_vars.copy()
            
            instr = self.code.instructions[i]
            
            # --- KILL STEP (Definition) ---
            defined_var = instr.get_defined_variable()
            
            # UPDATED Logic: Handle Dead Definitions vs Live Definitions
            if defined_var in current_live_vars:
                # Case A: The variable is LIVE. We found the start of its range.
                start = line_num
                end = var_range_ends[defined_var]
                
                self._add_live_range(defined_var, start, end)
                
                # It is no longer live above this line
                current_live_vars.remove(defined_var)
                del var_range_ends[defined_var]
            
            elif defined_var is not None:
                # Case B: The variable is defined, but NOT in current_live_vars.
                # This means it is never used later. It is a DEAD DEFINITION.
                self.dead_definitions.append((line_num, defined_var))
                
            # --- GEN STEP (Usage) ---
            used_vars = instr.get_used_variables()
            
            for var in used_vars:
                if var not in current_live_vars:
                    # Variable becomes live here (scanning backwards)
                    # So this line is the 'End' of its need (the sentinel point).
                    current_live_vars.add(var)
                    var_range_ends[var] = line_num
        
        # 3. Handle Live-At-Entry
        for var in current_live_vars:
            start = 0
            end = var_range_ends[var]
            self._add_live_range(var, start, end)
            
        self.live_at_entry = current_live_vars
        self.liveness_results = results
        
        return results

    def _add_live_range(self, var_name, start, end):
        """Helper to add a live range to the dictionary"""
        if var_name not in self.live_ranges:
            self.live_ranges[var_name] = []
        
        # Create the object and add it
        new_range = LiveRange(var_name, start, end)
        self.live_ranges[var_name].append(new_range)

    def print_liveness(self):
        """Prints the results in a readable format."""
        print("\n--- Liveness Analysis Results ---")
        
        # Print Live Ranges
        print("Live Ranges [Start, End):")
        for var in sorted(self.live_ranges.keys()):
            ranges = self.live_ranges[var]
            range_str = ", ".join([str(r) for r in ranges])
            print(f"  {var}: {range_str}")
            
        # UPDATED: Print Dead Definitions
        if self.dead_definitions:
            print("\nDead Definitions (Superfluous Code):")
            for line, var in sorted(self.dead_definitions):
                print(f"  Line {line}: defines '{var}' (never used)")
        
        print("-" * 30)
        
        # Print Line-by-Line
        for i, instr in enumerate(self.code.instructions):
            line_num = i + 1
            live_set = sorted(list(self.liveness_results[i]))
            print(f"Line {line_num}: {str(instr):<20} => Live After: {live_set}")
            
        print("---------------------------------\n")

# Test code
if __name__ == "__main__":
    print("Testing LivenessAnalyzer...")
    
    # Test Case with a DEAD definition
    # 1: a = 5
    # 2: x = 100   <-- Dead! 'x' is never used.
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
    code.add_instruction(ThreeAddressInstruction("a", "a", "+", "1"))
    code.add_instruction(ThreeAddressInstruction("t1", "a", "*", "4"))
    code.add_instruction(ThreeAddressInstruction("t2", "t1", "+", "1"))
    code.add_instruction(ThreeAddressInstruction("t3", "a", "*", "3"))
    code.add_instruction(ThreeAddressInstruction("b", "t2", "-", "t3"))
    code.add_instruction(ThreeAddressInstruction("t4", "b", "/", "2"))
    code.add_instruction(ThreeAddressInstruction("d", "c", "+", "t4"))
    code.set_live_on_exit(["d"])
    
    analyzer = LivenessAnalyzer(code)
    analyzer.analyze()
    analyzer.print_liveness()