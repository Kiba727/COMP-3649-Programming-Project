import sys
from main import main

def run_test(test_name, args):

    print(f"\n--- Running test {test_name} ---")

    sys.argv = ["main.py"] + args

    try:
        main()
    except SystemExit as e:
        print("Program exited with code:", e.code)

    print("-------------------------------\n")


if __name__ == "__main__":
    # main argument tests
    run_test("Missing Arguments", ["4"])
    run_test("Non-integer Register Count", ["abc", "input.txt"])
    run_test("Negative Register Count", ["-1", "input.txt"])
    run_test("Non-existent Input File", ["4", "nonexistent.txt"])

    # valid input file tests

    run_test("Bad Variable", ["4", "/tests/bad_var.txt"])
    run_test("Missing live on exit", ["4", "/tests/missing_live_on_exit.txt"])

    