package armory.trait;

import iron.Trait;
import iron.system.Input;
import iron.system.Time;
import iron.object.CameraObject;
import iron.math.Vec4;

@:keep
class WalkNavigation extends Trait {

	static inline var speed = 5.0;

	var camera:CameraObject;

	public function new() {
		super();

		notifyOnInit(init);
		notifyOnUpdate(update);
	}

	function init() {
		camera = cast(object, CameraObject);
	}

	function update() {
		if (Input.occupied) return;

		var keyboard = Input.getKeyboard();
		var moveForward = keyboard.down("w") || keyboard.down("up");
		var moveBackward = keyboard.down("s") || keyboard.down("down");
		var strafeLeft = keyboard.down("a") || keyboard.down("left");
		var strafeRight = keyboard.down("d") || keyboard.down("right");
		var strafeUp = keyboard.down("e");
		var strafeDown = keyboard.down("q");
		var fast = keyboard.down("shift") ? 2.0 : (keyboard.down("alt") ? 0.5 : 1.0);

		var d = Time.delta * speed * fast;

		if (moveForward) {
			camera.move(camera.look(), d);
		}
		else if (moveBackward) {
			camera.move(camera.look(), -d);
		}
		if (strafeRight) {
			camera.move(camera.right(), d);
		}
		else if (strafeLeft) {
			camera.move(camera.right(), -d);
		}
		if (strafeUp) {
			var dir = new Vec4(0, 0, 1);
			camera.move(dir, d);
		}
		else if (strafeDown) {
			var dir = new Vec4(0, 0, 1);
			camera.move(dir, -d);
		}

		var mouse = Input.getMouse();
		if (mouse.down()) {
			camera.rotate(Vec4.zAxis(), -mouse.movementX / 200);
			camera.rotate(camera.right(), -mouse.movementY / 200);
		}
	}
}
