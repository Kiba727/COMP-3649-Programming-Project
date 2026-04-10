-- threeAddress.hs
-- ADT with hidden constructors for encapsulation.
-- Outside modules must use the smart constructors and getter functions below.
module ThreeAddress
    ( ThreeAddressInstruction   -- type exported, constructor hidden
    , IntermediateCode          -- type exported, constructor hidden
    -- Constructors
    , makeInstruction
    , makeIntermediateCode
    -- Getters for ThreeAddressInstruction
    , getDst
    , getSrc1
    , getOp
    , getSrc2
    -- Getters for IntermediateCode
    , getInstructions
    , getLiveOnExit
    -- Predicates
    , isBinary
    , isUnaryNegation
    , isAssignment
    -- Builders
    , addInstruction
    , setLiveOnExit
    ) where

data ThreeAddressInstruction = ThreeAddressInstruction
    { dst  :: String
    , src1 :: String
    , op   :: Maybe String
    , src2 :: Maybe String
    } deriving (Show, Eq)

data IntermediateCode = IntermediateCode
    { instruction :: [ThreeAddressInstruction]
    , liveOnExit  :: [String]
    } deriving (Show)

-- Smart constructor for a single instruction.
-- Validates nothing here (validation is the parser's job),
-- but construction is now gated through a single point.
makeInstruction :: String -> String -> Maybe String -> Maybe String -> ThreeAddressInstruction
makeInstruction = ThreeAddressInstruction

-- Smart constructor for an intermediate code block.
makeIntermediateCode :: [ThreeAddressInstruction] -> [String] -> IntermediateCode
makeIntermediateCode = IntermediateCode

-- Getters for ThreeAddressInstruction
getDst :: ThreeAddressInstruction -> String
getDst = dst

getSrc1 :: ThreeAddressInstruction -> String
getSrc1 = src1

getOp :: ThreeAddressInstruction -> Maybe String
getOp = op

getSrc2 :: ThreeAddressInstruction -> Maybe String
getSrc2 = src2

-- Getters for IntermediateCode
getInstructions :: IntermediateCode -> [ThreeAddressInstruction]
getInstructions = instruction

getLiveOnExit :: IntermediateCode -> [String]
getLiveOnExit = liveOnExit

-- Predicates using pattern matching
isBinary :: ThreeAddressInstruction -> Bool
isBinary (ThreeAddressInstruction _ _ (Just _) (Just _)) = True
isBinary _ = False

isUnaryNegation :: ThreeAddressInstruction -> Bool
isUnaryNegation (ThreeAddressInstruction _ _ (Just "-") Nothing) = True
isUnaryNegation _ = False

isAssignment :: ThreeAddressInstruction -> Bool
isAssignment (ThreeAddressInstruction _ _ Nothing Nothing) = True
isAssignment _ = False

-- Builders
addInstruction :: IntermediateCode -> ThreeAddressInstruction -> IntermediateCode
addInstruction code instr = code { instruction = instruction code ++ [instr] }

setLiveOnExit :: IntermediateCode -> [String] -> IntermediateCode
setLiveOnExit code liveVars = code { liveOnExit = liveVars }