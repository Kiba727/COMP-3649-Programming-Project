-- assemblyInstructions.hs
-- ADT for representing target assembly instructions.
module AssemblyInstructions
  ( Opcode (..),
    OperandType (..),
    Operand (..),
    AssemblyInstruction (..),
    formatOperand,
    formatInstruction,
    formatTargetCode,
  )
where

data Opcode = ADD | SUB | MUL | DIV | MOV
  deriving (Show, Eq)

data OperandType = Immediate | Register | Variable
  deriving (Show, Eq)

data Operand = Operand OperandType String
  deriving (Eq)

data AssemblyInstruction = AssemblyInstruction Opcode Operand Operand
  deriving (Eq)

-- Format a single operand for display
formatOperand :: Operand -> String
formatOperand (Operand Immediate val) = "#" ++ val
formatOperand (Operand Register val) = "R" ++ val
formatOperand (Operand Variable val) = val

-- Format a single assembly instruction for display
formatInstruction :: AssemblyInstruction -> String
formatInstruction (AssemblyInstruction opc src dst) =
  show opc ++ " " ++ formatOperand src ++ "," ++ formatOperand dst

-- Format a full list of instructions, one per line
formatTargetCode :: [AssemblyInstruction] -> String
formatTargetCode = unlines . map formatInstruction

instance Show Operand where
  show = formatOperand

instance Show AssemblyInstruction where
  show = formatInstruction