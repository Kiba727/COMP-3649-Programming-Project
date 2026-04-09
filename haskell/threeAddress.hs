module ThreeAddress where

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

data IntermediateCode = IntermediateCode
    { instruction :: [ThreeAddressInstruction]
    , liveOnExit :: [String]
    }

addInstruction :: IntermediateCode -> ThreeAddressInstruction -> IntermediateCode
addInstruction code instr = code { instruction = instruction code ++ [instr] }

setLiveOnExit :: IntermediateCode -> [String] -> IntermediateCode
setLiveOnExit code liveVars = code { liveOnExit = liveVars }

