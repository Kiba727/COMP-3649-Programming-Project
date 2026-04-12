-- codegen.hs
-- Translates three-address code into assembly instructions
-- given a register colouring (allocations).
module CodeGen
    ( generateTargetCode
    ) where

import Data.List (sort)

import ThreeAddress
    ( ThreeAddressInstruction
    , IntermediateCode
    , getDst, getSrc1, getOp, getSrc2
    , getInstructions, getLiveOnExit
    , isBinary, isUnaryNegation
    )
import AssemblyInstructions
    ( Opcode(..), OperandType(..), Operand(..)
    , AssemblyInstruction(..)
    )
import Interference (Allocations)

-- Operand Construction 

-- | Converts a token to an Operand: integer literal → Immediate, variable → Register.
makeOperand :: String -> Allocations -> Operand
makeOperand val allocs
    | isIntLiteral val = Operand Immediate val
    | otherwise        = case lookup val allocs of
        Just r  -> Operand Register (show r)
        Nothing -> error $ "Unallocated variable: " ++ val

-- | Checks whether a string represents an integer literal.
isIntLiteral :: String -> Bool
isIntLiteral ""          = False
isIntLiteral ('-':rest)  = not (null rest) && all (`elem` ['0'..'9']) rest
isIntLiteral s           = all (`elem` ['0'..'9']) s

-- Operator Mapping 

-- | Maps a three-address operator symbol to an assembly Opcode.
opMap :: String -> Opcode
opMap "+" = ADD
opMap "-" = SUB
opMap "*" = MUL
opMap "/" = DIV
opMap o   = error $ "Unknown operator: " ++ o

-- Core Translation 

-- | Three-phase pipeline: load live-on-entry, translate body, store live-on-exit.
generateTargetCode :: IntermediateCode -> Allocations -> [String] -> [AssemblyInstruction]
generateTargetCode ic allocs liveOnEntry =
    loadLiveOnEntry liveOnEntry allocs
        ++ concatMap (`translateInstr` allocs) (getInstructions ic)
        ++ storeLiveOnExit (getLiveOnExit ic) allocs

-- Phase 1: Load Live-on-Entry 

-- | Emits MOV instructions for variables live upon block entry.
loadLiveOnEntry :: [String] -> Allocations -> [AssemblyInstruction]
loadLiveOnEntry vars allocs =
    [ AssemblyInstruction MOV (Operand Variable v) (Operand Register (show r))
    | v <- sort vars
    , Just r <- [lookup v allocs]
    ]

--  Phase 2: Instruction Translation 

-- | Translates one three-address instruction. Dead definitions produce nothing.
translateInstr :: ThreeAddressInstruction -> Allocations -> [AssemblyInstruction]
translateInstr instr allocs = case lookup (getDst instr) allocs of
    Nothing     -> []
    Just dstReg -> translateLive instr allocs (Operand Register (show dstReg))

-- | Translates an instruction whose destination has an allocated register.
translateLive :: ThreeAddressInstruction -> Allocations -> Operand -> [AssemblyInstruction]
translateLive instr allocs dstOp
    | isBinary instr        = translateBinary instr allocs dstOp
    | isUnaryNegation instr = translateNeg instr allocs dstOp
    | otherwise             = [AssemblyInstruction MOV (makeOperand (getSrc1 instr) allocs) dstOp]

-- | Translates a binary instruction: dst = src1 op src2.
translateBinary :: ThreeAddressInstruction -> Allocations -> Operand -> [AssemblyInstruction]
translateBinary instr allocs dstOp =
    let src1Op = makeOperand (getSrc1 instr) allocs
        src2Op = makeOperand (maybe "" id (getSrc2 instr)) allocs
        oper   = opMap (maybe "+" id (getOp instr))
    in [ AssemblyInstruction MOV src1Op dstOp
       , AssemblyInstruction oper src2Op dstOp
       ]

-- | Translates unary negation: dst = -src  →  MOV #0,dst ; SUB src,dst.
translateNeg :: ThreeAddressInstruction -> Allocations -> Operand -> [AssemblyInstruction]
translateNeg instr allocs dstOp =
    let srcOp = makeOperand (getSrc1 instr) allocs
    in [ AssemblyInstruction MOV (Operand Immediate "0") dstOp
       , AssemblyInstruction SUB srcOp dstOp
       ]

--  Phase 3: Store Live-on-Exit 

-- | Emits MOV instructions to store live-on-exit variables back to memory.
storeLiveOnExit :: [String] -> Allocations -> [AssemblyInstruction]
storeLiveOnExit vars allocs =
    [ AssemblyInstruction MOV (Operand Register (show r)) (Operand Variable v)
    | v <- sort vars
    , Just r <- [lookup v allocs]
    ]