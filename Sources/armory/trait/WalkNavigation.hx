package armory.trait;

import kha.Key;
import iron.Trait;
import iron.system.Input;
import iron.system.Time;
import iron.object.CameraObject;
import iron.math.Vec4;
import iron.math.Quat;
import armory.system.Keymap;

@:keep
class WalkNavigation extends Trait {

	static inline var speed = 5.0;

	var camera:CameraObject;

	public function new() {
		super();

		kha.input.Keyboard.get().notify(onKeyDown, onKeyUp);

		notifyOnInit(init);
		notifyOnUpdate(update);
		notifyOnRemove(removed);
	}
	
	function removed() {
		kha.input.Keyboard.get().remove(onKeyDown, onKeyUp);
	}

	function init() {
		camera = cast(object, CameraObject);
	}

	function update() {
		if (Input.occupied) return;

		var d = Time.delta * speed * fast * slow;

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

		if (Input.touch) {
			camera.rotate(Vec4.zAxis(), -Input.deltaX / 200);
			camera.rotate(camera.right(), -Input.deltaY / 200);
		}
	}

	var moveForward = false;
	var moveBackward = false;
	var strafeLeft = false;
	var strafeRight = false;
	var strafeUp = false;
	var strafeDown = false;
	var fast = 1.0;
	var slow = 1.0;
	function onKeyDown(key:Key, char:String) {
		if (char == Keymap.forward || key == Key.UP) moveForward = true;
		else if (char == Keymap.backward || key == Key.DOWN) moveBackward = true;
		else if (char == Keymap.left || key == Key.LEFT) strafeLeft = true;
		else if (char == Keymap.right || key == Key.RIGHT) strafeRight = true;
		else if (char == Keymap.up) strafeUp = true;
		else if (char == Keymap.down) strafeDown = true;
		else if (key == Keymap.fast) fast = 2.0;
		else if (key == Keymap.slow) slow = 0.5;
	}

	function onKeyUp(key:kha.Key, char:String) {
		if (char == Keymap.forward || key == Key.UP) moveForward = false;
		else if (char == Keymap.backward || key == Key.DOWN) moveBackward = false;
		else if (char == Keymap.left || key == Key.LEFT) strafeLeft = false;
		else if (char == Keymap.right || key == Key.RIGHT) strafeRight = false;
		else if (char == Keymap.up) strafeUp = false;
		else if (char == Keymap.down) strafeDown = false;
		else if (key == Keymap.fast) fast = 1.0;
		else if (key == Keymap.slow) slow = 1.0;
	}
}
