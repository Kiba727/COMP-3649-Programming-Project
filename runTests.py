import sys
from main import main

def run_test(test_name, args):
    print(f"\n--- Running test: {test_name} ---")
    sys.argv = ["main.py"] + args
    try:
        main()
    except SystemExit as e:
        print("Program exited with code:", e.code)
    print("-------------------------------\n")

if __name__ == "__main__":
    # Command Line and Argument Validation Tests
    run_test("Missing Arguments",           ["4"])
    run_test("Non-integer Register Count",  ["abc", "input.txt"])
    run_test("Negative Register Count",     ["-1", "input.txt"])
    run_test("Zero Register Count",         ["0", "input.txt"])
    run_test("Non-existent Input File",     ["4", "nonexistent.txt"])

    # Parser and Syntax Validation Tests
    run_test("Bad Variable Name",           ["4", "tests/bad_var.txt"])
    run_test("Unsupported Operator (%)",    ["4", "tests/bad_op.txt"])
    run_test("Missing 'live:' Prefix",      ["4", "tests/no_live_prefix.txt"])
    run_test("Missing 'live:' Line",        ["4", "tests/missing_live.txt"])
    run_test("Live Var Not in Code",        ["4", "tests/invalid_live_var.txt"])
    run_test("Incomplete Instruction",      ["4", "tests/incomplete_instr.txt"])

    # Standard Functionality Tests
    run_test("Standard Example 1",          ["4", "tests/test1.txt"])
    run_test("Standard Example 2",          ["4", "tests/test2.txt"])
    run_test("Standard Example 3",          ["4", "tests/test3.txt"])
    run_test("Standard Example 4",          ["4", "tests/test4.txt"])
    run_test("Long Arithmetic Chain",       ["4", "tests/test5.txt"])
    run_test("High Register Pressure",      ["4", "tests/test6.txt"])
    run_test("Variable Reuse Logic",        ["4", "tests/test7.txt"])
    run_test("Complex Temp Usage",          ["4", "tests/test8.txt"])
    run_test("Live on Entry (x, y)",        ["4", "tests/test9.txt"])
    run_test("Multiple Live on Exit",       ["4", "tests/test10.txt"])
    run_test("Live on Entry + Exit",        ["4", "tests/entry_and_exit.txt"])

    # Register Allocation Failure Tests
    run_test("Alloc Failure (1 reg)",                   ["1", "tests/alloc_fail_1reg.txt"])
    run_test("Alloc Failure (High Pressure, 2 regs)",   ["2", "tests/alloc_fail_pressure.txt"])
    run_test("Alloc Min Success (2 regs, should pass)", ["2", "tests/alloc_min_success.txt"])
    run_test("Alloc Min Failure (1 reg, should fail)",  ["1", "tests/alloc_min_success.txt"])

    # Edge Cases and Stress Tests
    run_test("Single Instruction Block",    ["4", "tests/single_line.txt"])
    run_test("Dead Definition Detection",   ["4", "tests/dead_def.txt"])
    run_test("Large Integer Values",        ["4", "tests/large_ints.txt"])
    run_test("Many Temps (t100+)",          ["8", "tests/many_temps.txt"])
    run_test("Unary Negation Stress",       ["4", "tests/zero_init.txt"])
    run_test("Mixed Absolute/Immediate",    ["4", "tests/mixed_types.txt"])
    run_test("Empty Block",                 ["4", "tests/no_instr.txt"])
    run_test("Extreme Whitespace",          ["4", "tests/whitespace.txt"])
    run_test("Overlapping Live Ranges",     ["4", "tests/overlapping_ranges.txt"])
    run_test("Empty File",                  ["4", "tests/test11.txt"])