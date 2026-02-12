# interference.py
# Week 4: Interference Graph Construction

import sys
from liveness import LivenessAnalyzer

class InterferenceGraph:
    """
    Represents the interference graph where:
    - Nodes = Variables
    - Edges = Overlapping live ranges (Interference)
    """
    def __init__(self, analyzer):
        """
        Args:
            analyzer: A LivenessAnalyzer object that has already run .analyze()
        """
        self.analyzer = analyzer
        # Adjacency list: key = variable name, value = set of interfering variables
        self.adj_list = {}
        
        # Build the graph immediately upon initialization
        self.build()

    def build(self):
        """
        Constructs the graph by adding nodes for all variables 
        and edges for interfering variables.
        """
        # 1. Initialize nodes for every variable found in the liveness analysis
        # We sort them to ensure deterministic behavior (important for testing)
        variables = sorted(self.analyzer.live_ranges.keys())
        
        for var in variables:
            self.adj_list[var] = set()

        # 2. Check every pair of variables for interference
        # We use a nested loop to compare every unique pair (A, B)
        for i in range(len(variables)):
            for j in range(i + 1, len(variables)):
                var1 = variables[i]
                var2 = variables[j]

                if self._check_interference(var1, var2):
                    self.add_edge(var1, var2)

    def _check_interference(self, var1, var2):
        """
        Helper: Returns True if ANY live range of var1 overlaps with ANY live range of var2.
        """
        ranges1 = self.analyzer.live_ranges[var1]
        ranges2 = self.analyzer.live_ranges[var2]

        # A variable might have multiple live ranges (e.g. lines 2-4 and 8-10).
        # We must check all combinations.
        for r1 in ranges1:
            for r2 in ranges2:
                if r1.overlaps_with(r2):
                    return True
        return False

    def add_edge(self, u, v):
        """Adds an undirected edge between u and v."""
        if u in self.adj_list and v in self.adj_list:
            self.adj_list[u].add(v)
            self.adj_list[v].add(u)

    def print_graph(self):
        """
        Prints the 'Variable Interference Table' formatted exactly as required 
        by the project requirements.
        """
        print("\n--- Variable Interference Table ---")
        for var in sorted(self.adj_list.keys()):
            # Sort neighbors for consistent output
            neighbors = sorted(list(self.adj_list[var]))
            neighbor_str = ", ".join(neighbors)
            print(f"{var}: {neighbor_str}")
        print("-----------------------------------")
        
    def __repr__(self):
        return f"<InterferenceGraph: {len(self.adj_list)} nodes>"


# --- Test Code ---
if __name__ == "__main__":
    from threeAddress import IntermediateCode, ThreeAddressInstruction
    
    print("Testing InterferenceGraph module...")
    
    # Create the example from the Project Requirements (Page 4 & 7)
    # 1: a = a + 1
    # 2: t1 = a * 4
    # 3: t2 = t1 + 1
    # 4: t3 = a * 3
    # 5: b = t2 - t3
    # 6: t4 = b / 2
    # 7: d = c + t4   <-- Typo in PDF? It says t5 in one place and t4 in another. Using t4.
    # live: d
    
    code = IntermediateCode()
    # Assume 'a' and 'c' are live at entry (implicitly)
    
    code.add_instruction(ThreeAddressInstruction("a", "a", "+", "1"))     # 1
    code.add_instruction(ThreeAddressInstruction("t1", "a", "*", "4"))    # 2
    code.add_instruction(ThreeAddressInstruction("t2", "t1", "+", "1"))   # 3
    code.add_instruction(ThreeAddressInstruction("t3", "a", "*", "3"))    # 4
    code.add_instruction(ThreeAddressInstruction("b", "t2", "-", "t3"))   # 5
    code.add_instruction(ThreeAddressInstruction("t4", "b", "/", "2"))    # 6
    code.add_instruction(ThreeAddressInstruction("d", "c", "+", "t4"))    # 7
    code.set_live_on_exit(["d"])
        
    print("\n1. Running Liveness Analysis...")
    analyzer = LivenessAnalyzer(code)
    analyzer.analyze()
    analyzer.print_liveness()
    
    print("2. Building Interference Graph...")
    graph = InterferenceGraph(analyzer)
    graph.print_graph()
    
    # Expected Interferences (Mental Check):
    # 'a' is used at line 4, so it is live 1-4.
    # 't1' is defined at 2, used at 3. Live 2-3.
    # Do 'a' and 't1' overlap? Yes (at line 2 and 3).
    # Check output to see if "a: ..., t1, ..." exists.