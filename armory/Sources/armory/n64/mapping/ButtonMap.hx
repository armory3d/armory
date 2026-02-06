package armory.n64.mapping;

/**
 * Button Mapping (Armory → N64)
 *
 * Maps common gamepad button names to N64 button identifiers.
 * Supports PlayStation, Xbox, and native N64 naming conventions.
 */
class ButtonMap {
    // Map common button names to N64 button identifiers
    // Matches config.py BUTTON_MAP
    public static var map:Map<String, String> = [
        // PlayStation-style
        "cross" => "a", "square" => "b", "circle" => "cright", "triangle" => "cleft",
        // Xbox-style
        "a" => "a", "b" => "cright", "x" => "b", "y" => "cleft",
        // Shoulders/Triggers
        "r1" => "cdown", "r2" => "r", "r3" => "cup",
        "l1" => "z", "l2" => "l", "l3" => "cup",
        // System
        "start" => "start", "options" => "start", "share" => "start",
        // D-Pad
        "up" => "dup", "down" => "ddown", "left" => "dleft", "right" => "dright",
        "dup" => "dup", "ddown" => "ddown", "dleft" => "dleft", "dright" => "dright",
        // C-Buttons direct
        "cup" => "cup", "cdown" => "cdown", "cleft" => "cleft", "cright" => "cright",
        // N64 native
        "l" => "l", "r" => "r", "z" => "z",
    ];

    // Map normalized button name to N64_BTN_* constant
    public static var n64Const:Map<String, String> = [
        "a" => "N64_BTN_A", "b" => "N64_BTN_B", "z" => "N64_BTN_Z",
        "start" => "N64_BTN_START", "l" => "N64_BTN_L", "r" => "N64_BTN_R",
        "dup" => "N64_BTN_DUP", "ddown" => "N64_BTN_DDOWN", "dleft" => "N64_BTN_DLEFT", "dright" => "N64_BTN_DRIGHT",
        "cup" => "N64_BTN_CUP", "cdown" => "N64_BTN_CDOWN", "cleft" => "N64_BTN_CLEFT", "cright" => "N64_BTN_CRIGHT",
    ];

    public static function normalize(button:String):String {
        var lower = button.toLowerCase();
        return map.exists(lower) ? map.get(lower) : lower;
    }

    public static function toN64Const(button:String):String {
        var normalized = normalize(button);
        return n64Const.exists(normalized) ? n64Const.get(normalized) : "N64_BTN_A";
    }
}
