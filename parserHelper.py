import sys

def parseLiveLine(line, line_num):
    """
    Parses the "live:" line at the end of the input file.
    
    Args:
        line: string containing live variable list
        line_num: line number for error messages
        
    Returns:
        List of variable names on success, None on error
    """
    line = line.strip()
    
    # Check for "live:" prefix
    if not line.startswith("live:"):
        print(f"Error on line {line_num}: Missing 'live' prefix", file=sys.stderr)
        return None
    
    # Remove "live:" prefix
    remainder = line[5:].strip()
    
    # Handle case where no variables are live on exit
    if not remainder:
        return []
    
    # Split by comma
    var_strings = remainder.split(',')
    variables = []
    
    for var_str in var_strings:
        var = var_str.strip()
        if not var:
            continue  # Skip empty strings from consecutive commas
        if not isValidVariable(var):
            print(f"Error on line {line_num}: Invalid variable name '{var}' in live list", file=sys.stderr)
            return None
        variables.append(var)
    
    return variables


def isValidVariable(name):
    """
    Checks if a name is a valid variable according to the spec.
    
    Valid variable:
      - Single lowercase letter (excluding 't')
      - Letter 't' followed by one or more digits (e.g., t1, t23)
    
    Args:
        name: string to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not name:
        return False
    
    if len(name) == 1:
        # Single lowercase letter excluding 't'
        return name.islower() and name != 't'
    
    # Check for t followed by digits (e.g., t1, t23)
    if name[0] == 't' and len(name) > 1:
        return name[1:].isdigit()
    
    return False


def isValidOperand(operand):
    """
    Checks if an operand is valid variable or integer literal
    
    Args:
        operand: string to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Check if it's a valid variable
    if isValidVariable(operand):
        return True
    
    # Check if it's an integer literal
    try:
        int(operand)
        return True
    except ValueError:
        return False