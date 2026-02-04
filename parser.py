import threeAddress

def readIntermediateCode(): 
    input_file = "input.txt"
    instructions = []
    try:
        with open(input_file, 'r') as file:
              for line in file:
                
                instruction = read3AddrInstruction(line)

                if instruction:
                    instructions.append(instruction)

        return instructions

    except FileNotFoundError:
        print(f"Error: The file {input_file} was not found.")

def read3AddrInstruction(line):
    line = line.strip()

    input_sections = line.split()

    if len(input_sections) == 5:
        instruction = threeAddress.INSTRUCTION(input_sections[0], input_sections[2], input_sections[3], input_sections[4])
    
    elif len(input_sections) == 4:
        instruction = threeAddress.INSTRUCTION(input_sections, input_sections[2], input_sections[3], None)
    
    else:
        print("Bad input. Does not match expected format.")
        print("Format: Name, operand 1, operator, operand 2(optional)")