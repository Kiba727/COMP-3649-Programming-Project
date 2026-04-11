module AssemblyInstructionsTest where

import AssemblyInstructions

-- Test formatting of each operand type
testOperands :: IO ()
testOperands = do
    putStrLn "--- Test: Operand formatting ---"
    putStrLn $ "Immediate: " ++ formatOperand (Operand Immediate "5")
    putStrLn $ "Register:  " ++ formatOperand (Operand Register "0")
    putStrLn $ "Variable:  " ++ formatOperand (Operand Variable "a")
    putStrLn ""

-- Test formatting of individual instructions
testInstructions :: IO ()
testInstructions = do
    putStrLn "--- Test: Instruction formatting ---"
    let mov1 = AssemblyInstruction MOV (Operand Variable "a") (Operand Register "0")
    let add1 = AssemblyInstruction ADD (Operand Immediate "1") (Operand Register "0")
    let sub1 = AssemblyInstruction SUB (Operand Register "1") (Operand Register "0")
    let mul1 = AssemblyInstruction MUL (Operand Immediate "4") (Operand Register "1")
    let div1 = AssemblyInstruction DIV (Operand Immediate "2") (Operand Register "3")
    let mov2 = AssemblyInstruction MOV (Operand Register "0") (Operand Variable "a")
    mapM_ (putStrLn . formatInstruction) [mov1, add1, sub1, mul1, div1, mov2]
    putStrLn ""

-- Test Show instances produce the same output as format functions
testShowInstances :: IO ()
testShowInstances = do
    putStrLn "--- Test: Show instances ---"
    let op = Operand Immediate "42"
    putStrLn $ "show Operand:     " ++ show op
    let instr = AssemblyInstruction MOV (Operand Variable "c") (Operand Register "2")
    putStrLn $ "show Instruction: " ++ show instr
    putStrLn ""

-- Test formatTargetCode on a small program
testTargetCode :: IO ()
testTargetCode = do
    putStrLn "--- Test: Full target code ---"
    let prog = [ AssemblyInstruction MOV (Operand Variable "a") (Operand Register "0")
               , AssemblyInstruction ADD (Operand Immediate "1") (Operand Register "0")
               , AssemblyInstruction MOV (Operand Register "0") (Operand Variable "a")
               ]
    putStr $ formatTargetCode prog

-- Run all assembly instruction tests
runAssemblyInstructionsTest :: IO ()
runAssemblyInstructionsTest = do
    putStrLn "=== AssemblyInstructions Tests ===\n"
    testOperands
    testInstructions
    testShowInstances
    testTargetCode
    putStrLn "=== All AssemblyInstructions tests complete ==="