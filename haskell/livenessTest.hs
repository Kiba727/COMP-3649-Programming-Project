module LivenessTest where

import ThreeAddress

-- A sequence representing: 
-- a = 5; b = a + 1; live: b
testCase1 :: IntermediateCode
testCase1 = IntermediateCode 
    [ ThreeAddressInstruction "a" "5" Nothing Nothing
    , ThreeAddressInstruction "b" "a" (Just "+") (Just "1")
    ] ["b"]

-- A more complex sequence with overlapping ranges
testCase2 :: IntermediateCode
testCase2 = IntermediateCode
    [ ThreeAddressInstruction "a" "a" (Just "+") (Just "1")   -- Line 1
    , ThreeAddressInstruction "t1" "a" (Just "*") (Just "4")  -- Line 2
    , ThreeAddressInstruction "t2" "t1" (Just "+") (Just "1") -- Line 3
    , ThreeAddressInstruction "b" "t2" (Just "-") (Just "a")  -- Line 4
    ] ["b"]

