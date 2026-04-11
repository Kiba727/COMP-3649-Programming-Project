module CodeGenTest where

import ThreeAddress
import AssemblyInstructions
import Interference (Allocations)
import CodeGen (generateTargetCode)

-- Helper to print a labeled test result
runTest :: String -> [AssemblyInstruction] -> IO ()
runTest label instrs = do
    putStrLn $ "--- " ++ label ++ " ---"
    mapM_ (putStrLn . formatInstruction) instrs
    putStrLn ""

-- Test 1: Simple assignment (a = 5; b = a + 1; live: b)
test1 :: IO ()
test1 =
    let code   = makeIntermediateCode
                     [ makeInstruction "a" "5" Nothing Nothing
                     , makeInstruction "b" "a" (Just "+") (Just "1")
                     ] ["b"]
        allocs = [("a", 0), ("b", 1)] :: Allocations
        entry  = ["a"]
        result = generateTargetCode code allocs entry
    in runTest "Test 1: Simple assignment" result

-- Test 2: Full 7-line example from project spec
test2 :: IO ()
test2 =
    let code   = makeIntermediateCode
                     [ makeInstruction "a"  "a"  (Just "+") (Just "1")
                     , makeInstruction "t1" "a"  (Just "*") (Just "4")
                     , makeInstruction "t2" "t1" (Just "+") (Just "1")
                     , makeInstruction "t3" "a"  (Just "*") (Just "3")
                     , makeInstruction "b"  "t2" (Just "-") (Just "t3")
                     , makeInstruction "t4" "b"  (Just "/") (Just "2")
                     , makeInstruction "d"  "c"  (Just "+") (Just "t4")
                     ] ["d"]
        allocs = [("a",0),("t1",1),("t2",2),("t3",3),("b",5),("t4",4),("c",6),("d",6)]
        entry  = ["a", "c"]
        result = generateTargetCode code allocs entry
    in runTest "Test 2: Full 7-line spec example" result

-- Test 3: Unary negation (b = -a)
test3 :: IO ()
test3 =
    let code   = makeIntermediateCode
                     [ makeInstruction "a" "5" Nothing Nothing
                     , makeInstruction "b" "a" (Just "-") Nothing
                     ] ["b"]
        allocs = [("a", 0), ("b", 1)]
        entry  = []
        result = generateTargetCode code allocs entry
    in runTest "Test 3: Unary negation" result

-- Test 4: Dead definition (t1 not allocated, should be skipped)
test4 :: IO ()
test4 =
    let code   = makeIntermediateCode
                     [ makeInstruction "a"  "5"  Nothing Nothing
                     , makeInstruction "t1" "a"  (Just "*") (Just "2")
                     , makeInstruction "b"  "a"  (Just "+") (Just "1")
                     ] ["b"]
        allocs = [("a", 0), ("b", 1)]
        entry  = []
        result = generateTargetCode code allocs entry
    in runTest "Test 4: Dead definition skipped" result

-- Test 5: Two-register optimized version from spec
test5 :: IO ()
test5 =
    let code   = makeIntermediateCode
                     [ makeInstruction "a"  "a"  (Just "+") (Just "1")
                     , makeInstruction "t1" "a"  (Just "*") (Just "4")
                     , makeInstruction "t2" "t1" (Just "+") (Just "1")
                     , makeInstruction "t3" "a"  (Just "*") (Just "3")
                     , makeInstruction "b"  "t2" (Just "-") (Just "t3")
                     , makeInstruction "t4" "b"  (Just "/") (Just "2")
                     , makeInstruction "d"  "c"  (Just "+") (Just "t4")
                     ] ["d"]
        allocs = [("a",0),("t1",1),("t2",1),("t3",0),("b",1),("t4",1),("c",1),("d",1)]
        entry  = ["a", "c"]
        result = generateTargetCode code allocs entry
    in runTest "Test 5: Two-register allocation" result

-- Run all codegen tests
runCodeGenTest :: IO ()
runCodeGenTest = do
    putStrLn "=== CodeGen Tests ===\n"
    test1
    test2
    test3
    test4
    test5
    putStrLn "=== All CodeGen tests complete ==="