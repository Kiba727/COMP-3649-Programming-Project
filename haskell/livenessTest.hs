module LivenessTest where

import ThreeAddress

-- A sequence representing: 
-- a = 5; b = a + 1; live: b
testCase1 :: IntermediateCode
testCase1 = makeIntermediateCode 
    [ makeInstruction "a" "5" Nothing Nothing
    , makeInstruction "b" "a" (Just "+") (Just "1")
    ] ["b"]

-- A more complex sequence with overlapping ranges
testCase2 :: IntermediateCode
testCase2 = makeIntermediateCode
    [ makeInstruction "a" "a" (Just "+") (Just "1")   -- Line 1
    , makeInstruction "t1" "a" (Just "*") (Just "4")  -- Line 2
    , makeInstruction "t2" "t1" (Just "+") (Just "1") -- Line 3
    , makeInstruction "b" "t2" (Just "-") (Just "a")  -- Line 4
    ] ["b"]