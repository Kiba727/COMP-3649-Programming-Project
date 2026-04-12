module Main where

import System.Environment (getArgs)
import System.Exit (exitFailure)
import System.IO (hPutStrLn, stderr)
import Data.List (nub, sort)
import Data.Char (isDigit)

import ThreeAddress
import Parser (readIntermediateCode, isValidVariable)
import Liveness (analyze, varName, startLine)
import Interference (buildAdjList, colouringSolver, getUniqueVars, Allocations, AdjList)
import AssemblyInstructions (AssemblyInstruction, formatTargetCode, formatInstruction)
import CodeGen (generateTargetCode)

-- GHCi entry point for manual testing without command-line arguments.
run :: Int -> FilePath -> IO ()
run numRegs inputFile = do
    parseResult <- readIntermediateCode inputFile
    case parseResult of
        Left err   -> putStrLn $ "Error: " ++ err
        Right code ->
            case validateLiveOnExit code of
                Left err -> putStrLn $ "Error: " ++ err
                Right () -> runPipeline numRegs code inputFile

-- Command-line entry point
main :: IO ()
main = do
    args <- getArgs
    case args of
        [numStr, filename] -> do
            numRegs <- parseNumRegs numStr
            run numRegs filename
        _ -> exitWithError "Usage: gen <num_regs> <filename>"

-- Validates the register count argument
parseNumRegs :: String -> IO Int
parseNumRegs s
    | not (all isDigit s) || null s =
        exitWithError "Error: Argument one must be an integer."
    | n < 1     = exitWithError "Error: Argument one must be an integer greater than zero."
    | otherwise = return n
  where n = read s

-- Prints an error to stderr and exits
exitWithError :: String -> IO a
exitWithError msg = do
    hPutStrLn stderr msg
    exitFailure

-- Validates that all live-on-exit variables appear in the instruction sequence
validateLiveOnExit :: IntermediateCode -> Either String ()
validateLiveOnExit code =
    let instrs  = getInstructions code
        allVars = nub $ concatMap getVarsFromInstr instrs
        bad     = filter (`notElem` allVars) (getLiveOnExit code)
    in case bad of
        []    -> Right ()
        (v:_) -> Left $ "Variable '" ++ v ++ "' listed as live but does not appear in code"

-- Collects all variable names from a single instruction for validation purposes.
getVarsFromInstr :: ThreeAddressInstruction -> [String]
getVarsFromInstr instr =
    filter isValidVariable $
        [getDst instr, getSrc1 instr]
        ++ maybe [] (:[]) (getSrc2 instr)

-- Finds variables live at line 0 (used before defined in the block)
findLiveOnEntry :: IntermediateCode -> [String]
findLiveOnEntry code =
    let ranges = analyze code
    in nub [ varName r | r <- ranges, startLine r == 0 ]

-- Prints the variable interference table
printInterferenceTable :: AdjList -> IO ()
printInterferenceTable graph = do
    putStrLn "\n--- Variable Interference Table ---"
    mapM_ printEntry (sort graph)
    putStrLn "-----------------------------------"
  where
    printEntry (var, neighbors) =
        putStrLn $ var ++ ": " ++ joinWith ", " (sort neighbors)

-- Prints the register colouring table
printColouringTable :: Allocations -> IO ()
printColouringTable allocs = do
    putStrLn "\n--- Register Colouring Table ---"
    mapM_ printReg (sort regGroups)
    putStrLn "--------------------------------"
  where
    regGroups = foldr groupByReg [] allocs
    groupByReg (var, reg) acc = case lookup reg acc of
        Just vs -> (reg, var : vs) : filter ((/= reg) . fst) acc
        Nothing -> (reg, [var]) : acc
    printReg (reg, vs) =
        putStrLn $ "  R" ++ show reg ++ ": " ++ joinWith ", " (sort vs)

-- Joins a list of strings with a separator, similar to Python's str.join().
joinWith :: String -> [String] -> String
joinWith _ []       = ""
joinWith _ [x]      = x
joinWith sep (x:xs) = x ++ sep ++ joinWith sep xs

-- Strips the file extension and appends '.s' to derive the output filename.
deriveOutputFile :: FilePath -> FilePath
deriveOutputFile path =
    let base = reverse $ drop 1 $ dropWhile (/= '.') $ reverse path
    in if null base then path ++ ".s" else base ++ ".s"

-- Writes assembly to a file
writeAssemblyFile :: FilePath -> [AssemblyInstruction] -> IO ()
writeAssemblyFile filename instrs = do
    writeFile filename (formatTargetCode instrs)
    putStrLn $ "\nAssembly written to: " ++ filename

-- Prints the assembly instructions to stdout
printTargetCode :: [AssemblyInstruction] -> IO ()
printTargetCode instrs = do
    putStrLn "\n--- Assembly Instructions ---"
    mapM_ (putStrLn . formatInstruction) instrs

-- Runs the full compiler pipeline: liveness analysis, interference graph construction,
-- register allocation, code generation, and finally writes the assembly output.
runPipeline :: Int -> IntermediateCode -> FilePath -> IO ()
runPipeline numRegs code inputFile = do
    let ranges = analyze code
    let graph  = buildAdjList ranges
    let vars   = getUniqueVars ranges
    let result = colouringSolver graph vars numRegs []

    case result of
        [] -> putStrLn $ "Register allocation failed: "
                ++ show numRegs ++ " register(s) are not sufficient "
                ++ "to colour the interference graph."
        (allocs:_) -> do
            printInterferenceTable graph
            printColouringTable allocs

            let entry    = findLiveOnEntry code
            let target   = generateTargetCode code allocs entry
            let outFile  = deriveOutputFile inputFile

            printTargetCode target
            writeAssemblyFile outFile target