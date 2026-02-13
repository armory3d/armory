package armory.n64.mapping;

/**
 * Type Mapping (Haxe → C)
 *
 * Maps Haxe types to their C equivalents for N64 code generation.
 * Supports basic types and parameterized containers (Map, Array).
 */
class TypeMap {
    public static var haxeToCType:Map<String, String> = [
        // Primitives
        "Float" => "float",
        "float" => "float",
        "Int" => "int32_t",
        "int" => "int32_t",
        "Bool" => "bool",
        "bool" => "bool",
        "String" => "const char*",

        // Kha types
        "FastFloat" => "float",
        "Color" => "color_t",  // libdragon RGBA32 format
        "kha.Color" => "color_t",

        // Scene types
        "SceneId" => "SceneId",
        "SceneFormat" => "SceneId",
        "TSceneFormat" => "SceneId",

        // Object types
        "Object" => "ArmObject*",
        "iron.object.Object" => "ArmObject*",

        // Vector types
        "Vec2" => "ArmVec2",
        "Vec3" => "ArmVec3",
        "Vec4" => "ArmVec4",

        // Trait types - stored as pointers to trait data structs
        "RigidBody" => "void*",
        "armory.trait.physics.RigidBody" => "void*",

        // UI types
        "Label" => "UILabel*",
        "KouiCanvas" => "void*",  // Canvas is metadata-only, not stored at runtime
        "AnchorPane" => "UIGroup*",
        "RowLayout" => "UIGroup*",
        "ColLayout" => "UIGroup*",
        "GridLayout" => "UIGroup*",

        // Audio types
        "Sound" => "const char*",  // Sound asset reference (ROM path)
        "BaseChannelHandle" => "ArmSoundHandle",  // Playback handle

        // Tween types
        "Tween" => "ArmTween*",  // Tween instance (pointer to pool entry)

        // Function/callback types - all callbacks receive (void* obj, void* data) for trait access
        "Void->Void" => "ArmCallback",  // Typedef for void (*)(void*, void*)
        "Float->Void" => "ArmFloatObjCallback",  // Typedef for void (*)(float, void*, void*)
    ];

    public static function getCType(haxeType:String):String {
        if (haxeType == null) return "void*";

        // First check simple types
        if (haxeToCType.exists(haxeType)) {
            return haxeToCType.get(haxeType);
        }

        // Check for parameterized types
        var parsed = parseParameterizedType(haxeType);
        if (parsed != null) {
            return getCTypeForParameterized(parsed.base, parsed.params);
        }

        return "void*";
    }

    public static function isSupported(haxeType:String):Bool {
        if (haxeType == null) return false;
        if (haxeToCType.exists(haxeType)) return true;

        var parsed = parseParameterizedType(haxeType);
        if (parsed != null) {
            return parsed.base == "Map" || parsed.base == "Array";
        }
        return false;
    }

    /**
     * Parse a parameterized type like "Map<String, Array<BaseChannelHandle>>"
     * Returns { base: "Map", params: ["String", "Array<BaseChannelHandle>"] }
     */
    public static function parseParameterizedType(typeStr:String):{base:String, params:Array<String>} {
        if (typeStr == null) return null;
        var ltPos = typeStr.indexOf("<");
        if (ltPos == -1) return null;

        var base = typeStr.substring(0, ltPos);
        var paramsStr = typeStr.substring(ltPos + 1, typeStr.length - 1);

        // Parse params, handling nested generics
        var params:Array<String> = [];
        var depth = 0;
        var start = 0;
        for (i in 0...paramsStr.length) {
            var c = paramsStr.charAt(i);
            if (c == "<") depth++;
            else if (c == ">") depth--;
            else if (c == "," && depth == 0) {
                params.push(StringTools.trim(paramsStr.substring(start, i)));
                start = i + 1;
            }
        }
        params.push(StringTools.trim(paramsStr.substring(start)));

        return { base: base, params: params };
    }

    /**
     * Get C type for parameterized Haxe type.
     */
    static function getCTypeForParameterized(base:String, params:Array<String>):String {
        switch (base) {
            case "Array":
                if (params.length == 1) {
                    var elemType = params[0];
                    // Special case: Array<BaseChannelHandle> -> ArmSoundHandleArray
                    if (elemType == "BaseChannelHandle") {
                        return "ArmSoundHandleArray";
                    }
                    // Only generate typed arrays for known supported element types
                    // Others fall back to void* since we can't declare them
                    switch (elemType) {
                        case "Int": return "ArmIntArray";
                        case "Float": return "ArmFloatArray";
                        case "String": return "ArmStringArray";
                        case "Bool": return "ArmBoolArray";
                        default: return "void*";  // Unsupported array element type
                    }
                }

            case "Map":
                if (params.length == 2) {
                    var keyType = params[0];
                    var valueType = params[1];

                    // Only support String keys for now
                    if (keyType == "String") {
                        // Map<String, Array<BaseChannelHandle>> -> ArmSoundChannelMap
                        var valueParsed = parseParameterizedType(valueType);
                        if (valueParsed != null && valueParsed.base == "Array") {
                            if (valueParsed.params[0] == "BaseChannelHandle") {
                                return "ArmSoundChannelMap";
                            }
                        }
                        // Generic string map
                        return "ArmStringMap";
                    }
                }
        }

        return "void*";
    }

    /**
     * Check if a type is a Map type.
     */
    public static function isMapType(haxeType:String):Bool {
        if (haxeType == null) return false;
        var parsed = parseParameterizedType(haxeType);
        return parsed != null && parsed.base == "Map";
    }

    /**
     * Check if a type is an Array type.
     */
    public static function isArrayType(haxeType:String):Bool {
        if (haxeType == null) return false;
        var parsed = parseParameterizedType(haxeType);
        return parsed != null && parsed.base == "Array";
    }

    /**
     * Get the element type for an Array type.
     */
    public static function getArrayElementType(haxeType:String):String {
        if (haxeType == null) return null;
        var parsed = parseParameterizedType(haxeType);
        if (parsed != null && parsed.base == "Array" && parsed.params.length >= 1) {
            return parsed.params[0];
        }
        return null;
    }

    /**
     * Get key and value types for a Map type.
     */
    public static function getMapTypes(haxeType:String):{key:String, value:String} {
        if (haxeType == null) return null;
        var parsed = parseParameterizedType(haxeType);
        if (parsed != null && parsed.base == "Map" && parsed.params.length >= 2) {
            return { key: parsed.params[0], value: parsed.params[1] };
        }
        return null;
    }
}
