-- threeAddress.hs
-- This module acts as a gatekeeper. We export the names of our data types, 
-- but hide their internal parts so other files can't mess with them directly. 
-- This follows the Week 10 guidance on encapsulation.
module ThreeAddress
    ( ThreeAddressInstruction   
    , IntermediateCode          
    , makeInstruction
    , makeIntermediateCode
    , getDst
    , getSrc1
    , getOp
    , getSrc2
    , getInstructions
    , getLiveOnExit
    , isBinary
    , isUnaryNegation
    , isAssignment
    , addInstruction
    , setLiveOnExit
    ) where

data ThreeAddressInstruction = ThreeAddressInstruction
    { dst  :: String
    , src1 :: String
    -- We use the Maybe type as these fields can either hold something or null.
    , op   :: Maybe String
    , src2 :: Maybe String
    } deriving (Show, Eq) 
    -- 'deriving' tells the compiler to automatically write the background code 
    -- needed to print this object (Show) and check if two are identical (Eq), this is for debugging.

data IntermediateCode = IntermediateCode
    { instruction :: [ThreeAddressInstruction]
    , liveOnExit  :: [String]
    } deriving (Show)

-- The only way for outside modules to create a ThreeAddressInstruction.
-- Keeps construction gated through a single point.
makeInstruction :: String -> String -> Maybe String -> Maybe String -> ThreeAddressInstruction
makeInstruction = ThreeAddressInstruction

-- The only way for outside modules to create an IntermediateCode block.
-- Bundles the instruction list and live-on-exit variables into one object.
makeIntermediateCode :: [ThreeAddressInstruction] -> [String] -> IntermediateCode
makeIntermediateCode = IntermediateCode

-- Retrieves the destination variable of an instruction.
getDst :: ThreeAddressInstruction -> String
getDst = dst

-- Retrieves the first source operand of an instruction.
getSrc1 :: ThreeAddressInstruction -> String
getSrc1 = src1

-- Retrieves the operator of an instruction, if one exists.
getOp :: ThreeAddressInstruction -> Maybe String
getOp = op

-- Retrieves the second source operand of an instruction, if one exists.
getSrc2 :: ThreeAddressInstruction -> Maybe String
getSrc2 = src2

-- Retrieves the list of instructions from an intermediate code block.
getInstructions :: IntermediateCode -> [ThreeAddressInstruction]
getInstructions = instruction

-- Retrieves the list of variables that are live on exit from the block.
getLiveOnExit :: IntermediateCode -> [String]
getLiveOnExit = liveOnExit

-- We use pattern matching to look directly inside the object. 
-- If both the operator and the second source have 'Just' a value, it must be binary.
isBinary :: ThreeAddressInstruction -> Bool
isBinary (ThreeAddressInstruction _ _ (Just _) (Just _)) = True
isBinary _ = False

-- Matches exactly when the operator is Just "-" and there is Nothing in src2.
isUnaryNegation :: ThreeAddressInstruction -> Bool
isUnaryNegation (ThreeAddressInstruction _ _ (Just "-") Nothing) = True
isUnaryNegation _ = False

-- If both the operator and the second source are Nothing, it is a simple assignment.
isAssignment :: ThreeAddressInstruction -> Bool
isAssignment (ThreeAddressInstruction _ _ Nothing Nothing) = True
isAssignment _ = False

-- Variables in Haskell are immutable. This syntax doesn't modify the existing 
-- object, but creates a brand new copy of 'code' with the updated field.
addInstruction :: IntermediateCode -> ThreeAddressInstruction -> IntermediateCode
addInstruction code instr = code { instruction = instruction code ++ [instr] }

-- Updates the live-on-exit list, returning a new IntermediateCode object.
setLiveOnExit :: IntermediateCode -> [String] -> IntermediateCode
setLiveOnExit code liveVars = code { liveOnExit = liveVars }