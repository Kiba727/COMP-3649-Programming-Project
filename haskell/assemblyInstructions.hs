-- assemblyInstructions.hs
-- ADT for representing target assembly instructions. 
-- Unlike our other modules, we use the (..) symbol here to export everything
-- since assembly instructions are simple data containers that don't need strict gatekeeping.
module AssemblyInstructions
    ( Opcode(..)
    , OperandType(..)
    , Operand(..)
    , AssemblyInstruction(..)
    , formatOperand
    , formatInstruction
    , formatTargetCode
    ) where

-- The five operations supported by our target architecture.
data Opcode = ADD | SUB | MUL | DIV | MOV
    deriving (Show, Eq)

-- The three ways a value can be referenced in an instruction.
-- Immediate = a literal number (#5), Register = a CPU register (R0), Variable = a memory location (a).
data OperandType = Immediate | Register | Variable
    deriving (Show, Eq)

-- Pairs an operand type with its value, e.g. (Register, "0") represents R0.
data Operand = Operand OperandType String
    deriving (Eq)

-- A single target instruction with an opcode, a source operand, and a destination operand.
data AssemblyInstruction = AssemblyInstruction Opcode Operand Operand
    deriving (Eq)

-- Format a single operand for display
formatOperand :: Operand -> String
formatOperand (Operand Immediate val) = "#" ++ val
formatOperand (Operand Register val)  = "R" ++ val
formatOperand (Operand Variable val)  = val

-- Format a single assembly instruction for display
formatInstruction :: AssemblyInstruction -> String
formatInstruction (AssemblyInstruction opc src dst) =
    show opc ++ " " ++ formatOperand src ++ "," ++ formatOperand dst

-- The '.' operator works like a pipe: it maps our format function over the 
-- list, then sends the result to 'unlines' to join them into a single string.
formatTargetCode :: [AssemblyInstruction] -> String
formatTargetCode = unlines . map formatInstruction

-- Plug our formatting functions into Haskell's built in Show class
-- so these types can be printed directly in GHCi and in other modules.
instance Show Operand where
    show = formatOperand

instance Show AssemblyInstruction where
    show = formatInstruction
