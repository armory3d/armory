package armory.n64.mapping;

/**
 * Type Mapping (Haxe → C)
 *
 * Maps Haxe types to their C equivalents for N64 code generation.
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

        // Scene types
        "SceneId" => "SceneId",
        "SceneFormat" => "SceneId",
        "TSceneFormat" => "SceneId",

        // Vector types
        "Vec2" => "ArmVec2",
        "Vec3" => "ArmVec3",
        "Vec4" => "ArmVec4",

        // UI types
        "Label" => "UILabel*",
        "KouiCanvas" => "void*",  // Canvas is metadata-only, not stored at runtime

        // Audio types
        "Sound" => "const char*",  // Sound asset reference (ROM path)
        "BaseChannelHandle" => "ArmSoundHandle",  // Playback handle
    ];

    public static function getCType(haxeType:String):String {
        return haxeToCType.exists(haxeType) ? haxeToCType.get(haxeType) : "void*";
    }

    public static function isSupported(haxeType:String):Bool {
        return haxeToCType.exists(haxeType);
    }
}
