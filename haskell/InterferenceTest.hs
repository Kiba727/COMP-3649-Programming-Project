module InterferenceTest where
    
import ThreeAddress
import Liveness
import Interference
import qualified Data.Map as Map

runInterferenceTest :: IO ()
runInterferenceTest = do
    let code = IntermediateCode 
            { instruction = 
                [ ThreeAddressInstruction "a" "a" (Just "+") (Just "1")
                , ThreeAddressInstruction "t1" "a" (Just "*") (Just "4")
                , ThreeAddressInstruction "t2" "t1" (Just "+") (Just "1")
                , ThreeAddressInstruction "t3" "a" (Just "*") (Just "3")
                , ThreeAddressInstruction "b" "t2" (Just "-") (Just "t3")
                , ThreeAddressInstruction "t4" "b" (Just "/") (Just "2")
                , ThreeAddressInstruction "d" "c" (Just "+") (Just "t4")
                ]
            , liveOnExit = ["d"]
            }

    -- run analyzer
    let ranges = analyze code 

    -- build adjacent list
    let graph = buildAdjList ranges

    -- get list of unique variables for solver
    let vars = getUniqueVars ranges
    
    -- 4. Solve
    let result = colouringSolver graph vars 4 []

    case result of
        Nothing -> putStrLn "Allocation failed."
        Just allocs -> print allocs