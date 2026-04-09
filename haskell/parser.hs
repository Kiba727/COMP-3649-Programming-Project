module Parser where

import ThreeAddress 
import Data.Char (isLower, isDigit)

-- Validates variables based on project specs: single char (not 't') or t + digits
isValidVariable :: String -> Bool
isValidVariable "" = False
isValidVariable [c] = isLower c && c /= 't'
isValidVariable (c:cs) = c == 't' && all isDigit cs && not (null cs)

-- Operands can be valid variables or integer literals (handling negative signs)
isValidOperand :: String -> Bool
isValidOperand s = isValidVariable s || case s of
    ('-':rest) -> not (null rest) && all isDigit rest
    str        -> not (null str) && all isDigit str

read3AddrInstruction :: String -> Int -> ThreeAddressInstruction
read3AddrInstruction line lineNum = 
    case words line of 
        [dst, "=", src] ->
            if isValidVariable dst && isValidOperand src
                then ThreeAddressInstruction dst src Nothing Nothing
                else error $ "Error on line " ++ show lineNum ++ ": Invalid assignment syntax."
        
        [dst, "=", "-", src] ->
            if isValidVariable dst && isValidOperand src
                then ThreeAddressInstruction dst src (Just "-") Nothing
                else error $ "Error on line " ++ show lineNum ++ ": Invalid unary negation syntax."
        
        [dst, "=", src1, op, src2] ->
            if not (op `elem` ["+", "-", "*", "/"])
                then error $ "Error on line " ++ show lineNum ++ ": Invalid operator '" ++ op ++ "'"
            else if isValidVariable dst && isValidOperand src1 && isValidOperand src2 
                then ThreeAddressInstruction dst src1 (Just op) (Just src2)
                else error $ "Error on line " ++ show lineNum ++ ": Invalid operands or destination."
        
        _ -> error $ "Error on line " ++ show lineNum ++ ": Unrecognized instruction format."

-- Extracts variables from the 'live:' line using standard string processing
parseLiveLine :: String -> [String]
parseLiveLine line =
    let stripped = drop 5 line
        vars = words (filter (/= ',') stripped)
    in filter isValidVariable vars

-- Uses readFile for lazy processing of the input file
readIntermediateCode :: FilePath -> IO (Maybe IntermediateCode)
readIntermediateCode filename = do
    contents <- readFile filename
    let allLines = lines contents
    if null allLines
        then do
            putStrLn "Error: File is empty or does not exist"
            return Nothing
        else do
            let liveLine = last allLines
            let bodyLines = filter (\l -> not (null (words l))) (init allLines)
            
            -- This now returns a clean [ThreeAddressInstruction]
            let instrs = zipWith read3AddrInstruction bodyLines [1..]
            
            let liveVars = parseLiveLine liveLine
            
            -- Build and return the final object directly
            return (Just (IntermediateCode instrs liveVars))