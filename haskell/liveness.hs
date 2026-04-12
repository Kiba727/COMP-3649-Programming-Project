-- liveness.hs
-- Liveness analysis via backward scan using a fold over indexed instructions.
module Liveness
    ( LiveRange         -- type only, constructor hidden
    , analyze
    , overlaps
    , varName
    , startLine
    , endLine
    ) where

import ThreeAddress
import Parser (isValidVariable)
import Data.Set (Set)
import qualified Data.Set as Set
import qualified Data.Map as Map

-- Represents the [start, end) interval for a variable.
-- The bracket '[' means startLine is included, the parenthesis ')' means endLine is not.
data LiveRange = LiveRange
    { varName   :: String
    , startLine :: Int
    , endLine   :: Int
    } deriving (Show, Eq)

-- The state carried through the backward scan.
data LivenessState = LivenessState
    { currentLive  :: Set String
    , rangeEnds    :: Map.Map String Int
    , activeRanges :: [LiveRange]
    } deriving (Show)

-- Variables used on the RHS of an instruction.
getUsedVars :: ThreeAddressInstruction -> [String]
getUsedVars instr =
    filter isValidVariable
        ([getSrc1 instr] ++ maybe [] (:[]) (getSrc2 instr))

-- Variable defined on the LHS of an instruction.
getDefinedVar :: ThreeAddressInstruction -> String
getDefinedVar = getDst

-- Closes a variable's live range when its definition is encountered.
processDef :: String -> Int -> LivenessState -> (Set String, [LiveRange], Map.Map String Int)
processDef def line state =
    if Set.member def (currentLive state)
        then ( Set.delete def (currentLive state)
             , LiveRange def line
                   (Map.findWithDefault (line + 1) def (rangeEnds state))
                   : activeRanges state
             , Map.delete def (rangeEnds state)
             )
        else (currentLive state, activeRanges state, rangeEnds state)

-- Adds newly seen variables to the live set and records where their range ends.
processUses :: [String] -> Int -> (Set String, Map.Map String Int) -> (Set String, Map.Map String Int)
processUses uses line (live, ends) =
    let updatedEnds = foldl (\m v -> if Set.member v live
                                     then m
                                     else Map.insert v (line + 1) m) ends uses
        updatedLive = Set.union live (Set.fromList uses)
    in (updatedLive, updatedEnds)

-- Creates a brand new record with updated fields to pass to the next step.
processStep :: (Int, ThreeAddressInstruction) -> LivenessState -> LivenessState
processStep (line, instr) state =
    let def                           = getDefinedVar instr
        uses                          = getUsedVars instr
        (newLive, newRanges, newEnds) = processDef def line state
        (updatedLive, updatedEnds)    = processUses uses line (newLive, newEnds)
    in state { currentLive  = updatedLive
             , rangeEnds    = updatedEnds
             , activeRanges = newRanges
             }

-- Finalizes ranges for variables that were never defined in this block.
-- These are live at the start (line 0), meaning they came from outside memory.
buildEntryRanges :: LivenessState -> [LiveRange]
buildEntryRanges finalState =
    [ LiveRange v 0 (Map.findWithDefault 1 v (rangeEnds finalState))
    | v <- Set.toList (currentLive finalState)
    ]

-- Takes an intermediate code block and returns a list of live ranges.
-- Because liveness must be calculated from the bottom of the block to the top, 
-- 'foldr' (fold right) is used to iterate through the instruction list backwards.
analyze :: IntermediateCode -> [LiveRange]
analyze code =
    let instrs        = getInstructions code
        exitVars      = getLiveOnExit code
        numInstrs     = length instrs
        initialState  = LivenessState
            { currentLive  = Set.fromList exitVars
            , rangeEnds    = Map.fromList [(v, numInstrs + 1) | v <- exitVars]
            , activeRanges = []
            }
        finalState    = foldr processStep initialState (zip [1..] instrs)
    in activeRanges finalState ++ buildEntryRanges finalState

-- Checks if two live ranges overlap using half-open interval intersection.
overlaps :: LiveRange -> LiveRange -> Bool
overlaps r1 r2 =
    startLine r1 < endLine r2 && startLine r2 < endLine r1