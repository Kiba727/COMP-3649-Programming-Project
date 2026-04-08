data ThreeAddressInstruction = ThreeAddressInstruction
    { dst :: String
    , src1 :: String
    , op :: Maybe String
    , src2 :: Maybe String
    }


isBinary :: ThreeAddressInstruction -> Bool
isBinary instr = case op instr of
    Just _ -> case src2 instr of
        Just _ -> True
        Nothing -> False
    Nothing -> False

isUnaryNegation :: ThreeAddressInstruction -> Bool
isUnaryNegation instr = case op instr of 
    Just "-" -> case src2 instr of
        Nothing -> True
        _       -> False
    _ -> False

isAssignment :: ThreeAddressInstruction -> Bool
isAssignment instr = case op instr of
    Nothing -> case src2 instr of
        Nothing -> True
        _       -> False
    _ -> False



getUsedVariables :: ThreeAddressInstruction -> [String]
getUsedVariables instr = case is

data IntermediateCode = IntermediateCode
    { instruction :: [ThreeAddressInstruction]
    , liveOnExit :: [String]
    }