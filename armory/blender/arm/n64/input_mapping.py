# Armory Gamepad button names (from iron.system.Input.Gamepad)
# PlayStation: ["cross", "circle", "square", "triangle", "l1", "r1", "l2", "r2", "share", "options", "l3", "r3", "up", "down", "left", "right", "home", "touchpad"]
# Xbox:        ["a",     "b",      "x",      "y",        "l1", "r1", "l2", "r2", "share", "options", "l3", "r3", "up", "down", "left", "right", "home", "touchpad"]

# N64 button enum names (from input.h, matches libdragon)
# N64_BTN_A, N64_BTN_B, N64_BTN_Z, N64_BTN_START,
# N64_BTN_DUP, N64_BTN_DDOWN, N64_BTN_DLEFT, N64_BTN_DRIGHT,
# N64_BTN_L, N64_BTN_R,
# N64_BTN_CUP, N64_BTN_CDOWN, N64_BTN_CLEFT, N64_BTN_CRIGHT

# Mapping: Armory gamepad button name → N64 button enum
GAMEPAD_TO_N64_MAP = {
    # PlayStation / Xbox → N64
    'cross': 'N64_BTN_A',       'a': 'N64_BTN_A',
    'square': 'N64_BTN_B',      'x': 'N64_BTN_B',
    'r1': 'N64_BTN_CDOWN',
    'r3': 'N64_BTN_CUP',
    'l3': 'N64_BTN_CUP',
    'triangle': 'N64_BTN_CLEFT', 'y': 'N64_BTN_CLEFT',
    'circle': 'N64_BTN_CRIGHT', 'b': 'N64_BTN_CRIGHT',
    'r2': 'N64_BTN_R',
    'l1': 'N64_BTN_Z',
    'l2': 'N64_BTN_L',
    'options': 'N64_BTN_START', 'share': 'N64_BTN_START',
    # D-Pad
    'up': 'N64_BTN_DUP',
    'down': 'N64_BTN_DDOWN',
    'left': 'N64_BTN_DLEFT',
    'right': 'N64_BTN_DRIGHT',
    # Unmapped (no N64 equivalent): home, touchpad
}

# Input state mapping: Armory/Iron method name → N64 C function name
INPUT_STATE_MAP = {
    'started': 'input_started',
    'down': 'input_down',
    'released': 'input_released',
}

# Analog stick mapping: Armory method → N64 C function
STICK_MAP = {
    'getStickX': 'input_stick_x',
    'getStickY': 'input_stick_y',
}

# Scene method mapping: Armory method → N64 C function
SCENE_METHOD_MAP = {
    'setActive': 'scene_switch_to',
}
