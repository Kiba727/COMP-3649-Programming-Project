module Liveness where

import ThreeAddress
import Parser (isValidVariable)
import Data.Set (Set)
import qualified Data.Set as Set
import qualified Data.Map as Map

-- Represents the [start, end) interval for a variable
data LiveRange = LiveRange 
    { varName   :: String
    , startLine :: Int
    , endLine   :: Int
    } deriving (Show, Eq)

-- The state we carry through our backward scan (the "fold")
data LivenessState = LivenessState
    { currentLive :: Set String          -- Variables currently alive
    , rangeEnds   :: Map.Map String Int  -- The "last use" line found so far
    , activeRanges :: [LiveRange]        -- Completed ranges
    } deriving (Show) 

-- Helper to get variables used on the RHS (Right Hand Side)
getUsedVars :: ThreeAddressInstruction -> [String]
getUsedVars instr = 
    filter isValidVariable ([src1 instr] ++ maybe [] (:[]) (src2 instr))

-- Helper to get the variable defined on the LHS (Left Hand Side)
getDefinedVar :: ThreeAddressInstruction -> String
getDefinedVar = dst 

analyze :: IntermediateCode -> [LiveRange]
analyze (IntermediateCode instrs exitVars) = 
    let 
        numInstrs = length instrs
        -- Initial state: variables live on exit are active
        initialState = LivenessState 
            { currentLive = Set.fromList exitVars
            , rangeEnds   = Map.fromList [(v, numInstrs + 1) | v <- exitVars]
            , activeRanges = []
            }
        -- Zip with line numbers [1..n] to track the current position
        indexedInstrs = zip [1..] instrs
        finalState = foldr processStep initialState indexedInstrs
        
        -- Finalize variables live at the start (line 0)
        entryRanges = [LiveRange v 0 (Map.findWithDefault 1 v (rangeEnds finalState))
                    | v <- Set.toList (currentLive finalState)]
    in 
        activeRanges finalState ++ entryRanges

processStep :: (Int, ThreeAddressInstruction) -> LivenessState -> LivenessState
processStep (line, instr) state =
    let
        def = getDefinedVar instr
        uses = getUsedVars instr
        
        -- 1. Handle Definition: If def is live, close its range
        (newLive, newRanges, newEnds) = if Set.member def (currentLive state)
            then ( Set.delete def (currentLive state)
                 , LiveRange def line (Map.findWithDefault (line + 1) def (rangeEnds state)) : activeRanges state
                 , Map.delete def (rangeEnds state)
                 )
            else (currentLive state, activeRanges state, rangeEnds state)
            
        -- 2. Handle Uses: Add new variables to live set and record their "end" line
        updatedEnds = foldl (\m v -> if Set.member v newLive then m else Map.insert v (line + 1) m) newEnds uses
        updatedLive = Set.union newLive (Set.fromList uses)
    in
        state { currentLive = updatedLive, rangeEnds = updatedEnds, activeRanges = newRanges } 

-- Checks if two variable lifespans overlap
overlaps :: LiveRange -> LiveRange -> Bool
overlaps r1 r2 = 
    startLine r1 < endLine r2 && startLine r2 < endLine r1