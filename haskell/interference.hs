module Interference where

import Data.List (nub)
import Liveness

type AdjList = [(String, [String])]

type Allocations = [(String, Int)]

data InterferenceGraph = InterferenceGraph
    { adjList :: AdjList
    , variables :: [String]
    } 

checkInterference :: [LiveRange] -> [LiveRange] -> Bool
checkInterference range1 range2 = 
    any (\r1 -> any (\r2 -> overlaps r1 r2) range2) range1

buildAdjList :: [LiveRange] -> AdjList
buildAdjList ranges = 
    let vars = getUniqueVars ranges
        liveList = [(v, [r | r <- ranges, varName r == v]) | v <- vars]
    in [ (v, [ neighbor | neighbor <- vars
                        , neighbor /= v
                        , checkInterference (getRanges v liveList) (getRanges neighbor liveList) ])
        | v <- vars ]

getRanges :: String -> [(String, [LiveRange])] -> [LiveRange]
getRanges var nameList = 
    case lookup var nameList of
        Just rs -> rs
        Nothing -> []

getUniqueVars :: [LiveRange] -> [String]
getUniqueVars rs = nub [varName r | r <- rs]

safeColour :: String -> Int -> AdjList -> Allocations -> Bool
safeColour var reg graph allocs = 
    case lookup var graph of
        Nothing -> True
        Just neighbors ->
            not (any (\nb -> lookup nb allocs == Just reg) neighbors) 

colouringSolver :: AdjList -> [String] -> Int -> Allocations -> Maybe Allocations 
colouringSolver _ [] _ allocations = Just allocations
colouringSolver graph (v:vs) numRegs allocs =
    let tryColour [] = Nothing
        tryColour (c:cs) = 
            if safeColour v c graph allocs
                then case colouringSolver graph vs numRegs ((v,c) : allocs) of
                    Just final -> Just final
                    Nothing -> tryColour cs
                else tryColour cs
    in tryColour [0 .. numRegs - 1]
