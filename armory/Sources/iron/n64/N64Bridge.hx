#if arm_target_n64
package iron.n64;

import iron.Scene;
import iron.object.Object;

class N64Bridge {
    public static var input: N64Input = new N64Input();
    public static var transform: N64Transform = new N64Transform();
    public static var scene: N64Scene = new N64Scene();
    public static var object: N64Object = new N64Object();
}

class N64Input {
    public inline function started(button: String): Bool { return false; }
    public inline function down(button: String): Bool { return false; }
    public inline function released(button: String): Bool { return false; }
    public inline function getStickX(): Float { return 0.0; }
    public inline function getStickY(): Float { return 0.0; }
}

class N64Transform {
    public inline function translate(object: Object, x: Float, y: Float, z: Float): Void {}
    public inline function rotate(object: Object, x: Float, y: Float, z: Float): Void {}
    public inline function setPosition(object: Object, x: Float, y: Float, z: Float): Void {}
    public inline function setRotation(object: Object, x: Float, y: Float, z: Float): Void {}
}

class N64Scene {
    public inline function setActive(name: String): Void {}
    public inline function getName(scene: Scene): String { return ""; }
}

class N64Object {
	public inline function getVisible(object: Object): Bool { return false; }
	public inline function setVisible(object: Object, visible: Bool): Void {}
}
#end