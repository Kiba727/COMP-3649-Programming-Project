# main.py
import sys
import os
from parser import readIntermediateCode
from liveness import LivenessAnalyzer
from interference import InterferenceGraph
from codegen import generate_target_code

def main():
    num_regs, input_file, intermediate_code = handle_input()
    
    is_valid, error_msg = intermediate_code.validate_live_on_exit()
    if not is_valid:
        print(f"Error: {error_msg}", file=sys.stderr)
        sys.exit(1)
    
    graph, analyzer = create_interference_table(intermediate_code, num_regs)

    build_colouring_table(graph)

    live_on_entry = build_live_on_entry(analyzer)

    target = generate_target_code(intermediate_code, graph.allocations, live_on_entry)

    print_target_code(target)

    write_to_assembly_file(target, input_file)
    sys.exit(0)

def handle_input():
    if len(sys.argv) != 3:
        print("Usage: python main.py <num_registers> <input_file>", file=sys.stderr)
        sys.exit(1)

    try:
        num_regs = int(sys.argv[1])
        if num_regs < 1:
            print("Error: Argument one must be an integer greater than zero.", file=sys.stderr)
            sys.exit(1)
    except ValueError:
        print("Error: Argument one must be an integer.", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[2]
    if not os.path.isfile(input_file):
        print(f"Error: File '{input_file}' is not a readable file.", file=sys.stderr)
        sys.exit(1)

    intermediate_code = readIntermediateCode(input_file)
    if intermediate_code is None:
        sys.exit(1)

    return num_regs, input_file, intermediate_code

def create_interference_table(code, num_regs):
    analyzer = LivenessAnalyzer(code)
    
    analyzer.analyze()
    
    graph = InterferenceGraph(analyzer)

    success = graph.allocate_registers(num_regs)
    if not success:
        print(f"Register allocation failed: {num_regs} register(s) are not sufficient to colour the interference graph.")
        sys.exit(1) 
        
    print_interference_table(graph)
    return graph, analyzer

def print_interference_table(graph):
    graph.print_graph()
    return 0

def build_colouring_table(graph):
    reg_to_vars = {}
    for var in graph.variables:
        reg = graph.allocations[var]
        if reg not in reg_to_vars:
            reg_to_vars[reg] = []
        reg_to_vars[reg].append(var)
        
    print_colouring_table(reg_to_vars)
    return 0

def print_colouring_table(reg_to_vars):
    print("\n--- Register Colouring Table ---")
    for reg in sorted(reg_to_vars.keys()):
        print(f"  R{reg}: {', '.join(sorted(reg_to_vars[reg]))}")
    print("--------------------------------")
    return 0

def build_live_on_entry(analyzer):
    # Variables that are live at line 0 were never defined in this block
    live_on_entry = {
        var for var, ranges in analyzer.live_ranges.items()
        if any(r.start_line == 0 for r in ranges)
    }
    return live_on_entry

def write_to_assembly_file(target, input_file):
    base, _ = os.path.splitext(input_file)
    output_file = base + ".s"
    target.write_to_file(output_file)
    print(f"\nAssembly written to: {output_file}")
    return 0

def print_target_code(target):
    print(f"\n-----Assembly-Instructions------")
    print(target)
    return 0

if __name__ == "__main__":
    main()