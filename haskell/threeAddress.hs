-- ADT pattern
module ThreeAddress 
    ( ThreeAddressInstruction(..)
    , IntermediateCode(..) -- Exporting IntermediateCode and its fields
    , isBinary
    , isUnaryNegation
    , isAssignment
    , addInstruction
    , setLiveOnExit
    ) where

data ThreeAddressInstruction = ThreeAddressInstruction
    { dst :: String
    , src1 :: String
    , op :: Maybe String
    , src2 :: Maybe String
    } deriving (Show, Eq) 

data IntermediateCode = IntermediateCode
    { instruction :: [ThreeAddressInstruction]
    , liveOnExit :: [String]
    } deriving (Show)

-- Pattern Matching For Cases
isBinary :: ThreeAddressInstruction -> Bool
isBinary (ThreeAddressInstruction _ _ (Just _) (Just _)) = True
isBinary _ = False

isUnaryNegation :: ThreeAddressInstruction -> Bool
isUnaryNegation (ThreeAddressInstruction _ _ (Just "-") Nothing) = True
isUnaryNegation _ = False

isAssignment :: ThreeAddressInstruction -> Bool
isAssignment (ThreeAddressInstruction _ _ Nothing Nothing) = True
isAssignment _ = False

addInstruction :: IntermediateCode -> ThreeAddressInstruction -> IntermediateCode
addInstruction code instr = code { instruction = instruction code ++ [instr] }

setLiveOnExit :: IntermediateCode -> [String] -> IntermediateCode
setLiveOnExit code liveVars = code { liveOnExit = liveVars }