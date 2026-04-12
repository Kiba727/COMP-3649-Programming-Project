-- interference.hs
-- Builds a variable interference graph from live ranges and solves
-- register allocation using graph colouring with backtracking.
module Interference
  ( InterferenceGraph, -- Type exported, constructor hidden
    AdjList,
    Allocations,
    buildAdjList,
    colouringSolver,
    getUniqueVars,
  )
where

import Data.List (nub)
import Liveness

-- An AdjList is a list of tuples. 
-- Each tuple contains a variable name and a list of its "interfering" neighbors.
type AdjList = [(String, [String])]

-- Allocations maps a variable name to its assigned register number (0, 1, 2...).
type Allocations = [(String, Int)]

-- This locks the data structure so other files can't change the graph directly. 
-- They must use our helper functions instead, following Week 10's encapsulation rules.
data InterferenceGraph = InterferenceGraph
  { adjList :: AdjList,
    variables :: [String]
  } deriving (Show)

-- Checks if any live range from the first variable overlaps with any from the second.
checkInterference :: [LiveRange] -> [LiveRange] -> Bool
checkInterference range1 range2 =
  any (\r1 -> any (\r2 -> overlaps r1 r2) range2) range1

-- Builds an adjacency list from a list of live ranges.
-- Each variable is mapped to the list of variables whose live ranges overlap with it.
buildAdjList :: [LiveRange] -> AdjList
buildAdjList ranges =
  let vars = getUniqueVars ranges
      liveList = [(v, [r | r <- ranges, varName r == v]) | v <- vars]
   in [ ( v,
          [ neighbor | neighbor <- vars, neighbor /= v, checkInterference (getRanges v liveList) (getRanges neighbor liveList)
          ]
        )
        | v <- vars
      ]

-- Looks up the live ranges for a given variable in the pre-built name/range list.
getRanges :: String -> [(String, [LiveRange])] -> [LiveRange]
getRanges var nameList =
  case lookup var nameList of
    Just rs -> rs
    Nothing -> []

-- Returns a deduplicated list of all variable names found in the live ranges.
-- 'nub' is a standard Haskell utility that strips out duplicate elements from a list.
getUniqueVars :: [LiveRange] -> [String]
getUniqueVars rs = nub [varName r | r <- rs]

-- Checks that assigning a register to a variable doesn't conflict with its neighbors.
safeColour :: String -> Int -> AdjList -> Allocations -> Bool
safeColour var reg graph allocs =
  case lookup var graph of
    Nothing -> True
    Just neighbors ->
      not (any (\nb -> lookup nb allocs == Just reg) neighbors)

-- Uses a list comprehension to perform a non-deterministic search (backtracking).
-- 'c <- [0 .. numRegs - 1]' branches the search to try every possible color.
-- Because Haskell evaluates code lazily, it won't actually compute all possible solutions.
-- The moment the caller requests the first valid allocation, the search stops immediately.
colouringSolver :: AdjList -> [String] -> Int -> Allocations -> [Allocations]
colouringSolver _ [] _ allocations = [allocations]
colouringSolver graph (v : vs) numRegs allocs =
  [ finalSolution
    | c <- [0 .. numRegs - 1],
      safeColour v c graph allocs,
      let newAllocs = (v, c) : allocs,
      finalSolution <- colouringSolver graph vs numRegs newAllocs
  ]