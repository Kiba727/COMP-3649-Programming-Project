-- parser.hs
-- Input file parsing logic.
-- Uses Either String for safe error propagation instead of runtime crashes.
-- Left = error message, Right = successfully parsed value.
module Parser 
    ( readIntermediateCode -- Function client modules needs to read the file
    , isValidVariable      -- Exported because liveness.hs uses it
    ) where

import ThreeAddress 
import Data.Char (isLower, isDigit)

-- Validates variables based on project spec:
-- single lowercase letter (not 't'), or 't' followed by one or more digits.
isValidVariable :: String -> Bool
isValidVariable ""     = False
isValidVariable [c]    = isLower c && c /= 't'
isValidVariable (c:cs) = c == 't' && not (null cs) && all isDigit cs

-- Operands can be valid variables or integer literals (including negative).
-- negative literals like -5 are valid operands, but -a (negative variable) is handled
-- separately as unary negation during instruction parsing.
isValidOperand :: String -> Bool
isValidOperand s = isValidVariable s || case s of
    ('-':rest) -> not (null rest) && all isDigit rest
    str        -> not (null str)  && all isDigit str

-- Routes a single line to the appropriate parser based on token count.
-- Returns Left with a descriptive error message if the line doesn't match any known pattern.
read3AddrInstruction :: String -> Int -> Either String ThreeAddressInstruction
read3AddrInstruction line lineNum =
    case words line of
        [d, "=", src]        -> parseAssignment d src lineNum
        [d, "=", "-", src]   -> parseUnary d src lineNum
        [d, "=", s1, o, s2]  -> parseBinary d s1 o s2 lineNum
        _                    -> Left $ "Error on line " ++ show lineNum
                                    ++ ": Invalid token count"

-- Handles: dst = src (simple assignment) and dst = -src (compact unary negation).
-- Split into multiple pattern clauses to safely handle the '-' prefix without crashing.
parseAssignment :: String -> String -> Int -> Either String ThreeAddressInstruction
parseAssignment d _ lineNum
    | not (isValidVariable d) =
        Left $ "Error on line " ++ show lineNum
            ++ ": Invalid destination '" ++ d ++ "'"
parseAssignment d ('-':rest) lineNum
    | null rest =
        Left $ "Error on line " ++ show lineNum
            ++ ": Invalid operand '-'"
    | isValidOperand rest =
        Right $ makeInstruction d rest (Just "-") Nothing
    | otherwise =
        Left $ "Error on line " ++ show lineNum
            ++ ": Invalid operand '-" ++ rest ++ "'"
parseAssignment d src lineNum
    | not (isValidOperand src) =
        Left $ "Error on line " ++ show lineNum
            ++ ": Invalid operand '" ++ src ++ "'"
    | otherwise =
        Right $ makeInstruction d src Nothing Nothing

-- Handles: dst = - src (unary negation with a space between '-' and the operand).
parseUnary :: String -> String -> Int -> Either String ThreeAddressInstruction
parseUnary d src lineNum
    | not (isValidVariable d) =
        Left $ "Error on line " ++ show lineNum
            ++ ": Invalid destination '" ++ d ++ "'"
    | not (isValidOperand src) =
        Left $ "Error on line " ++ show lineNum
            ++ ": Invalid operand '" ++ src ++ "'"
    | otherwise = Right $ makeInstruction d src (Just "-") Nothing

-- Handles: dst = src1 op src2 (binary operation).
parseBinary :: String -> String -> String -> String -> Int -> Either String ThreeAddressInstruction
parseBinary d s1 o s2 lineNum
    | not (isValidVariable d) =
        Left $ "Error on line " ++ show lineNum
            ++ ": Invalid destination '" ++ d ++ "'"
    | o `notElem` ["+", "-", "*", "/"] =
        Left $ "Error on line " ++ show lineNum
            ++ ": Invalid operator '" ++ o ++ "'"
    | not (isValidOperand s1) || not (isValidOperand s2) =
        Left $ "Error on line " ++ show lineNum
            ++ ": Invalid operand(s)"
    | otherwise = Right $ makeInstruction d s1 (Just o) (Just s2)

-- Parses the final "live:" line.
-- Returns Left if the "live:" prefix is missing entirely.
-- Invalid variable names in the live list are silently ignored rather than erroring.
parseLiveLine :: String -> Int -> Either String [String]
parseLiveLine line lineNum
    | take 5 line /= "live:" =
        Left $ "Error on line " ++ show lineNum ++ ": Missing 'live' prefix"
    | otherwise =
        let remainder = drop 5 line
            vars      = words (filter (/= ',') remainder)
            valid     = filter isValidVariable vars
        in Right valid

-- Reads and parses an entire input file into an IntermediateCode object.
-- Returns Left String on failure, bubbling the error to the caller.
readIntermediateCode :: FilePath -> IO (Either String IntermediateCode)
readIntermediateCode filename = do
    contents <- readFile filename
    let allLines = lines contents
    if null allLines
        then return (Left "Error: Input file is empty")
        else return (parseContents allLines)

-- Splits the file into instruction lines and the live line, then parses each.
-- Blank lines in the body are filtered out before parsing.
parseContents :: [String] -> Either String IntermediateCode
parseContents allLines = 
    let bodyLines = filter (not . null . words) (init allLines)
        liveLine  = last allLines
    in case parseInstructions bodyLines of
        Left errMsg  -> Left errMsg
        Right instrs -> parseLiveAndBuild instrs liveLine (length allLines)

-- Parses all instruction lines, short-circuiting on the first error.
-- sequence collects all Either results and returns the first Left if any failed.
parseInstructions :: [String] -> Either String [ThreeAddressInstruction]
parseInstructions bodyLines =
    let lineNums = [1 .. length bodyLines]
        results  = zipWith read3AddrInstruction bodyLines lineNums
    in sequence results

-- Parses the live line and combines it with the instructions into an IntermediateCode object.
parseLiveAndBuild :: [ThreeAddressInstruction] -> String -> Int -> Either String IntermediateCode
parseLiveAndBuild instrs liveLine lineNum =
    case parseLiveLine liveLine lineNum of
        Left errMsg    -> Left errMsg
        Right liveVars -> Right (makeIntermediateCode instrs liveVars)