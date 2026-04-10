module ParserTest where

import Parser
import ThreeAddress

runTest :: String -> FilePath -> IO ()
runTest testName filepath = do
    putStrLn $ "--- Running: " ++ testName ++ " ---"
    result <- readIntermediateCode filepath
    case result of
        Just code -> do
            putStrLn "SUCCESS: File parsed correctly."
            print code
        Nothing -> 
            putStrLn "FAILED: Parser returned Nothing."
    putStrLn ""

parserTest :: IO ()
parserTest = do
    putStrLn "Starting Parser Tests...\n"
    
    runTest "Standard test1" "tests/test1.txt"
    runTest "File with test2" "tests/test2.txt"
    runTest "File with test3" "tests/test3.txt"
