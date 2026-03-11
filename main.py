# main.py
# Usage: python main.py <num_registers> <input_file>

import sys
import os
from collections import defaultdict

from parser import readIntermediateCode
from liveness import LivenessAnalyzer
from interference import InterferenceGraph
from codegen import generate_target_code


def main():
    if len(sys.argv) != 3:
        print("Usage: python main.py <num_registers> <input_file>", file=sys.stderr)
        sys.exit(1)

    try:
        num_regs = int(sys.argv[1])
        if num_regs < 1:
            raise ValueError
    except ValueError:
        print("Error: <num_registers> must be a positive integer.", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[2]

    intermediate_code = readIntermediateCode(input_file)
    if intermediate_code is None:
        sys.exit(1)

    print("=== Three-Address Code ===")
    print(intermediate_code)

    analyzer = LivenessAnalyzer(intermediate_code)
    analyzer.analyze()
    analyzer.print_liveness()

    graph = InterferenceGraph(analyzer)
    graph.print_graph()

    success = graph.allocate_registers(num_regs)
    if not success:
        print(f"Register allocation failed: {num_regs} register(s) are not sufficient to colour the interference graph.")
        sys.exit(0)

    # Build and print register colouring table (R0: a, b, d format)
    reg_to_vars = defaultdict(list)
    for var in graph.variables:
        reg_to_vars[graph.allocations[var]].append(var)

    print("\n--- Register Colouring Table ---")
    for reg in sorted(reg_to_vars.keys()):
        print(f"  R{reg}: {', '.join(sorted(reg_to_vars[reg]))}")
    print("--------------------------------")

    # Variables live on entry have a range starting at 0 
    live_on_entry = {
        var for var, ranges in analyzer.live_ranges.items()
        if any(r.start_line == 0 for r in ranges)
    }
    
    target = generate_target_code(intermediate_code, graph.allocations, live_on_entry)

    print("\n=== Assembly Output ===")
    print(target)

    base, _ = os.path.splitext(input_file)
    output_file = base + ".s"
    target.write_to_file(output_file)
    print(f"\nAssembly written to: {output_file}")

    sys.exit(0)


if __name__ == "__main__":
    main()