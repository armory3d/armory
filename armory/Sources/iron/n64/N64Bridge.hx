#if arm_target_n64
package iron.n64;

class N64Bridge {
    public static var input: N64Input = new N64Input();
    public static var transform: N64Transform = new N64Transform();
    public static var scene: N64Scene = new N64Scene();
}

class N64Input {
    public inline function started(key: String): Bool { return false; }
    public inline function down(key: String): Bool { return false; }
    public inline function released(key: String): Bool { return false; }
    public inline function getStickX(): Float { return 0.0; }
    public inline function getStickY(): Float { return 0.0; }
}

class N64Transform {
    public inline function translate(object: iron.object.Object, x: Float, y: Float, z: Float): Void {}
    public inline function rotate(object: iron.object.Object, x: Float, y: Float, z: Float): Void {}
    public inline function setPosition(object: iron.object.Object, x: Float, y: Float, z: Float): Void {}
    public inline function setRotation(object: iron.object.Object, x: Float, y: Float, z: Float): Void {}
}

class N64Scene {
    public inline function switchTo(name: String): Void {}
    public inline function getCurrentName(): String { return ""; }
}
#end