# main.py
# Week 3 main module - command-line entry point

import sys
from parser import readIntermediateCode
# sys.argv = ["main.py", "1", "test2.txt"]


def main():
    """
    Main entry point for the code generator.
    
    Usage: python main.py <num_regs> <input_file>
    
    For Week 3, this reads and prints the intermediate code.
    num_regs will be used in later weeks for register allocation.
    """    
    num_regs = int(sys.argv[1])
    input_file = sys.argv[2]
    
    # Read and parse the input file
    intermediate_code = readIntermediateCode(input_file)
    
    # If parsing failed, readIntermediateCode already printed error
    if intermediate_code is None:
        sys.exit(1)
    
    # Print the intermediate code (Week 3 requirement)
    print(intermediate_code)
    print(f"\nNumber of registers: {num_regs}")
    print(f"Total instructions: {len(intermediate_code)}")
    print(f"All variables used: {sorted(intermediate_code.get_all_variables())}")
    print(f"Live on exit: {intermediate_code.live_on_exit}")
    
    sys.exit(0)


if __name__ == "__main__":
    main()