import re

filename = 'app/services/process_service.py'

try:
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if '\t' in line:
            print(f"Line {i+1}: Contains TAB character")
        
        # Check for mixed indentation (spaces and tabs at start of line)
        indent = re.match(r'^([ \t]+)', line)
        if indent:
            whitespace = indent.group(1)
            if ' ' in whitespace and '\t' in whitespace:
                print(f"Line {i+1}: Mixed spaces and tabs in indentation")

    print("Check complete.")

except Exception as e:
    print(f"Error: {e}")
