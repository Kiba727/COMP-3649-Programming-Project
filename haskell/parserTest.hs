module ParserTest where

import Parser
import ThreeAddress

runTest :: String -> FilePath -> IO ()
runTest testName filepath = do
    putStrLn $ "--- Running: " ++ testName ++ " ---"
    result <- readIntermediateCode filepath
    case result of
        Right code -> do
            putStrLn "SUCCESS: File parsed correctly."
            print code
        Left errMsg -> 
            putStrLn $ "FAILED: " ++ errMsg
    putStrLn ""

parserTest :: IO ()
parserTest = do
    putStrLn "Starting Parser Tests...\n"
    -- Ensure you have a 'tests' folder with these text files inside!
    runTest "Standard test1" "tests/test1.txt"
    runTest "File with test2" "tests/test2.txt"
    runTest "File with test3" "tests/test3.txt"