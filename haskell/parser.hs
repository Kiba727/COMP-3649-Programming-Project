module Parser where

import ThreeAddress 
import Data.Char (islower, isDigit)


isValidVariable :: String -> Bool
isValidVariable "" = False
isValidVariable [c] = isLower c && c/= 't'
isValidVariable (c:cs) = c == 't' && all isDigit cs && not (null cs)
isValidVariable _ = False

isValidOperand :: String -> Bool
isValidOperand s = isValidVariable s || all isDigit (filter (/= '-')s)

read3AddrInstruction :: String -> Int -> Maybe ThreeAddressInstruction
read3AddrInstruction line lineNum = 
    case words line of 
        [dst, "=", src] ->
            if isValidVariable dst && isValidOperand src
                then Just (ThreeAddressInstruction dst src Nothing Nothing)
                else Nothing
        [dst, "=", "-", src] ->
            if isValidVariable dst && isValidPerand src
                then Just (ThreeAddressInstruction dst src (Just "-") Nothing)
                else Nothing
        [dst, "=", src1, op, src2] ->
            if isValidVariable dst && isValidOperand src1 && isValidOperand src2 && op 'elem' ["+", "-", "*", "/"]
                then Just (ThreeAddressInstruction dst src1 (Just op) (Just src2))
                else Nothing
        _ -> Nothing


parseLiveLine :: String -> [String]
parseLiveLine line =
    let stripped = drop 5 line
        vars = words (filter (/= ",") stripped)
    in filter isValidVariable vars

readIntermediateCode :: FilePath -> IO (Maybe IntermediateCode)
readIntermediateCode filename = do
    contents <- readFile filenameCDialect
    let allLines = line contents
    if null allLines
        then putStrLn("Error: File does not exist")
        else do
            let bodyLines = init allLines
            let liveLines = last allLines

            let parsedLines = zipWith read3AddrInstruction bodyLines[1..]

            case sequence parsedLines of
                Nothing -> putStrLn("Error: Invalid file format")
                just instrs ->
                    return (Just (IntermediateCode instrs) (parseLiveLine liveLine))
