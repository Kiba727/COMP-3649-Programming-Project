class INSTRUCTION:
    def __init__(self, name, arg1, op, arg2, ):
            self.name = name
            self.arg1 = arg1
            self.op = op
            self.arg2 = arg2
          
    def __repr__(self):
        return f"Instruction(Results: {self.name}, Op: {self.arg1}, Args: {self.op}, {self.arg2})"
