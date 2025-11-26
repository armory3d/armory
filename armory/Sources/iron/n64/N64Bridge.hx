#if arm_target_n64
package iron.n64;

import iron.Scene;
import iron.object.Object;
import iron.system.Input;

@:keep
class N64Bridge {
	public function new() {}
    public static var input: N64Input = new N64Input();
    public static var transform: N64Transform = new N64Transform();
    public static var scene: N64Scene = new N64Scene();
    public static var object: N64Object = new N64Object();
}

@:keep
class N64Input {
	public function new() {}
    public function started(button: String): Bool { return false; }
    public function down(button: String): Bool { return false; }
    public function released(button: String): Bool { return false; }
    public function getStickX(stick: GamepadStick): Float { return 0.0; }
    public function getStickY(stick: GamepadStick): Float { return 0.0; }
}

@:keep
class N64Transform {
	public function new() {}
    public function translate(object: Object, x: Float, y: Float, z: Float): Void {}
    public function rotate(object: Object, x: Float, y: Float, z: Float): Void {}
    public function setPosition(object: Object, x: Float, y: Float, z: Float): Void {}
    public function setRotation(object: Object, x: Float, y: Float, z: Float): Void {}
}

@:keep
class N64Scene {
	public function new() {}
    public function setActive(name: String): Void {}
    public function getName(scene: Scene): String { return ""; }
}

@:keep
class N64Object {
	public function new() {}
	public function getVisible(object: Object): Bool { return false; }
	public function setVisible(object: Object, visible: Bool): Void {}
}
#end