def parse_trait(filepath):
    """
    Parse a Haxe trait file and extract notifyOn* blocks.
    Returns a dictionary with the trait structure.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    trait = {
        'name': '',
        'vars': {},          # Variable declarations
        'on_add': [],        # notifyOnAdd block lines
        'on_init': [],       # notifyOnInit block lines
        'on_update': [],     # notifyOnUpdate block lines
        'on_remove': [],     # notifyOnRemove block lines
    }

    # State machine
    state = 'IDLE'
    current_block = None
    brace_depth = 0
    block_lines = []

    for line in lines:
        stripped = line.strip()

        # Extract class name
        if state == 'IDLE' and stripped.startswith('class ') and ' extends ' in stripped:
            # "class Level extends iron.Trait {"
            parts = stripped.split()
            trait['name'] = parts[1]

        # Detect notifyOn* block start
        if state == 'IDLE':
            if 'notifyOnAdd(' in stripped:
                state = 'IN_BLOCK'
                current_block = 'on_add'
                brace_depth = stripped.count('{') - stripped.count('}')
                block_lines = []
                continue
            elif 'notifyOnInit(' in stripped:
                state = 'IN_BLOCK'
                current_block = 'on_init'
                brace_depth = stripped.count('{') - stripped.count('}')
                block_lines = []
                continue
            elif 'notifyOnUpdate(' in stripped:
                state = 'IN_BLOCK'
                current_block = 'on_update'
                brace_depth = stripped.count('{') - stripped.count('}')
                block_lines = []
                continue
            elif 'notifyOnRemove(' in stripped:
                state = 'IN_BLOCK'
                current_block = 'on_remove'
                brace_depth = stripped.count('{') - stripped.count('}')
                block_lines = []
                continue

        # Inside a notifyOn* block - track braces
        if state == 'IN_BLOCK':
            brace_depth += stripped.count('{') - stripped.count('}')

            # Store the line (excluding the closing brace line)
            if brace_depth > 0:
                block_lines.append(stripped)

            # Block ended - brace depth back to 0
            if brace_depth <= 0:
                trait[current_block] = block_lines
                state = 'IDLE'
                current_block = None
                block_lines = []

    return trait


def print_trait(trait):
    """Debug helper to print parsed trait structure."""
    print(f"\n=== Trait: {trait['name']} ===")
    for block_name in ['on_add', 'on_init', 'on_update', 'on_remove']:
        if trait[block_name]:
            print(f"\n{block_name}:")
            for line in trait[block_name]:
                print(f"  {line}")
    print("")
