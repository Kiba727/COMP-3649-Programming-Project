module InterferenceTest where
    
import ThreeAddress
import Liveness
import Interference

runInterferenceTest :: IO ()
runInterferenceTest = do
    let code = makeIntermediateCode 
            [ makeInstruction "a" "a" (Just "+") (Just "1")
            , makeInstruction "t1" "a" (Just "*") (Just "4")
            , makeInstruction "t2" "t1" (Just "+") (Just "1")
            , makeInstruction "t3" "a" (Just "*") (Just "3")
            , makeInstruction "b" "t2" (Just "-") (Just "t3")
            , makeInstruction "t4" "b" (Just "/") (Just "2")
            , makeInstruction "d" "c" (Just "+") (Just "t4")
            ] ["d"]

    let ranges = analyze code 
    let graph = buildAdjList ranges
    let vars = getUniqueVars ranges
    
    -- Solve (Now returns a list of all solutions)
    let result = colouringSolver graph vars 4 []

    case result of
        [] -> putStrLn "Allocation failed (No solutions found)."
        (firstSolution:_) -> do
            putStrLn "Success! Here is the first valid allocation:"
            print firstSolution
            putStrLn $ "Total number of valid allocations found: " ++ show (length result)