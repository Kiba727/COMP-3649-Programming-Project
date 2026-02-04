class ThreeAddress:
    def __init__(self, name, arg1, op, arg2, ):
            self.name = name
            self.arg1 = arg1
            self.op = op
            self.arg2 = arg2
          
    def __repr__(self):
        return f"Instruction(Results: {self.name}, Op: {self.arg1}, Args: {self.op}, {self.arg2})"

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
        instruction = ThreeAddress(input_sections[0], input_sections[2], input_sections[3], input_sections[4])
        print(f"Read instruction: {instruction}")
    
    if len(input_sections) == 4:
        instruction = ThreeAddress(input_sections[0], input_sections[2], input_sections[3], input_sections[4])
        print("4")