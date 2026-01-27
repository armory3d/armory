package armory.n64.mapping;

/**
 * Skip Lists
 *
 * Defines which members and classes should be skipped during extraction
 * because they're either handled specially or not available on N64.
 */
class SkipList {
    // Members that are handled specially or provided by the engine
    public static var members:Map<String, Bool> = [
        "object" => true, "transform" => true, "name" => true,
        "gamepad" => true, "keyboard" => true, "mouse" => true,
        "physics" => true, "rb" => true, "rigidBody" => true,
    ];

    // Classes that are not available on N64
    public static var classes:Map<String, Bool> = [
        "PhysicsWorld" => true, "RigidBody" => true,
        "Tween" => true, "Audio" => true, "Network" => true,
        "Graphics" => true,  // kha.graphics2.Graphics - not available on N64
    ];

    public static function shouldSkipMember(name:String):Bool {
        return members.exists(name);
    }

    public static function shouldSkipClass(name:String):Bool {
        return classes.exists(name);
    }
}
