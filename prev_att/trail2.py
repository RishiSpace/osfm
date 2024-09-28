import subprocess

# Function to parse winget search output
def parse_winget_output(command):
    # Ensure the command starts with 'winget search'
    if not command.startswith("winget search"):
        print("The command must start with 'winget search'.")
        return
    
    # Run the winget command and capture the output
    result = subprocess.run(command.split(), capture_output=True, text=True, encoding='utf-8')

    # Split the output into lines
    lines = result.stdout.strip().split('\n')
    
    # Debug: Print the captured lines
    print("Captured lines:")
    for line in lines:
        print(line)
    
    # Find the header line and separator line
    header_index = None
    separator_index = None
    for i, line in enumerate(lines):
        if set(line.strip()) == {'-'} and i > 0 and set(lines[i - 1].strip()) != {'-'}:
            separator_index = i
            header_index = i - 1
            break

    if separator_index is None or header_index is None:
        print("Separator line not found.")
        return
    
    # Extract the header and separator lines
    header_line = lines[header_index]
    separator_line = lines[separator_index]
    
    # Debug: Print the identified header and separator lines
    print(f"Header line: {header_line}")
    print(f"Separator line: {separator_line}")

    # Calculate column positions
    name_pos = header_line.index('Name')
    id_pos = header_line.index('Id')
    version_pos = header_line.index('Version')
    match_pos = header_line.index('Match') if 'Match' in header_line else None
    source_pos = header_line.index('Source') if 'Source' in header_line else None

    # Parse the lines using the positions
    parsed_data = []
    for line in lines[separator_index + 1:]:
        if source_pos:
            name = line[name_pos:id_pos].strip()
            id_ = line[id_pos:version_pos].strip()
            version = line[version_pos:match_pos].strip() if match_pos else line[version_pos:source_pos].strip()
            match = line[match_pos:source_pos].strip() if match_pos else ''
            source = line[source_pos:].strip()
        elif match_pos:
            name = line[name_pos:id_pos].strip()
            id_ = line[id_pos:version_pos].strip()
            version = line[version_pos:match_pos].strip()
            match = line[match_pos:].strip()
            source = ''
        else:
            name = line[name_pos:id_pos].strip()
            id_ = line[id_pos:version_pos].strip()
            version = line[version_pos:].strip()
            match = ''
            source = ''
        parsed_data.append((name, id_, version, match, source))

    # Print the parsed data
    for name, id_, version, match, source in parsed_data:
        print(f"Name: {name}, Id: {id_}, Version: {version}, Match: {match}, Source: {source}")

# Input the command
command_input = input("Enter the program name (e.g 'brave'): ")
command = f"winget search {command_input} --source winget"
print(command)
parse_winget_output(command)
