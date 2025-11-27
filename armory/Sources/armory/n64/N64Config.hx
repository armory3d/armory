package armory.n64;

#if macro
/**
 * N64 Configuration - Internal Dictionaries
 *
 * All mappings are embedded directly in the macro for speed and simplicity.
 * No external file loading needed at compile time.
 */
class N64Config {
    // =========================================
    // Button Mappings: Armory/Iron -> N64
    // =========================================
    static var _buttonMap:Map<String, String> = [
        // PlayStation-style
        "cross" => "N64_BTN_A",
        "square" => "N64_BTN_B",
        "circle" => "N64_BTN_CRIGHT",
        "triangle" => "N64_BTN_CLEFT",
        // Xbox-style
        "a" => "N64_BTN_A",
        "b" => "N64_BTN_CRIGHT",
        "x" => "N64_BTN_B",
        "y" => "N64_BTN_CLEFT",
        // Shoulders/Triggers
        "r1" => "N64_BTN_CDOWN",
        "r2" => "N64_BTN_R",
        "r3" => "N64_BTN_CUP",
        "l1" => "N64_BTN_Z",
        "l2" => "N64_BTN_L",
        "l3" => "N64_BTN_CUP",
        "l" => "N64_BTN_L",
        "r" => "N64_BTN_R",
        "zl" => "N64_BTN_Z",
        "zr" => "N64_BTN_Z",
        // System
        "start" => "N64_BTN_START",
        "options" => "N64_BTN_START",
        "share" => "N64_BTN_START",
        // D-Pad
        "up" => "N64_BTN_DUP",
        "down" => "N64_BTN_DDOWN",
        "left" => "N64_BTN_DLEFT",
        "right" => "N64_BTN_DRIGHT"
    ];

    // =========================================
    // Input State Mappings: Method -> N64 Function
    // =========================================
    static var _inputStateMap:Map<String, String> = [
        "down" => "input_down",
        "started" => "input_started",
        "released" => "input_released"
    ];

    // =========================================
    // Stick Mappings: Method -> N64 Function
    // =========================================
    static var _stickMap:Map<String, String> = [
        "getStickX" => "input_stick_x",
        "getStickY" => "input_stick_y"
    ];

    // =========================================
    // Type Mappings: Haxe -> C
    // =========================================
    static var _typeMap:Map<String, String> = [
        "Float" => "float",
        "float" => "float",
        "double" => "float",
        "Int" => "int32_t",
        "int" => "int32_t",
        "Bool" => "bool",
        "bool" => "bool",
        "String" => "const char*",
        "Vec4" => "Vec3",
        "iron.math.Vec4" => "Vec3",
        "SceneId" => "SceneId"
    ];

    // =========================================
    // Skip Filters
    // =========================================
    static var _skipMembers:Map<String, Bool> = [
        "object" => true,
        "transform" => true,
        "gamepad" => true,
        "keyboard" => true,
        "mouse" => true,
        "name" => true
    ];

    // =========================================
    // Public API
    // =========================================

    /**
     * Map a Haxe button name to N64 constant
     */
    public static function mapButton(button:String):String {
        var mapped = _buttonMap.get(button.toLowerCase());
        return mapped != null ? mapped : "N64_BTN_A";
    }

    /**
     * Map input state (down, started, released) to N64 function
     */
    public static function mapInputState(state:String):String {
        var mapped = _inputStateMap.get(state);
        return mapped != null ? mapped : "input_down";
    }

    /**
     * Map stick method to N64 function
     */
    public static function mapStick(method:String):String {
        var mapped = _stickMap.get(method);
        return mapped != null ? mapped : "input_stick_x";
    }

    /**
     * Map Haxe type to C type
     */
    public static function mapType(haxeType:String):String {
        var mapped = _typeMap.get(haxeType);
        return mapped != null ? mapped : "float";
    }

    /**
     * Check if type is supported for N64
     */
    public static function isSupportedType(typeName:String):Bool {
        return _typeMap.exists(typeName);
    }

    /**
     * Check if member should be skipped (API objects like gamepad, transform)
     */
    public static function shouldSkipMember(name:String):Bool {
        return _skipMembers.exists(name);
    }
}
#end
