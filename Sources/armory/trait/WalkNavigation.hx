package armory.trait;

import iron.Trait;
import iron.system.Input;
import iron.system.Time;
import iron.object.CameraObject;
import iron.math.Vec4;

@:keep
class WalkNavigation extends Trait {

	static inline var speed = 5.0;
	var dir = new Vec4();
	var xvec = new Vec4();
	var yvec = new Vec4();
	var ease = 1.0;

	var camera:CameraObject;

	var keyboard:Keyboard;
	var gamepad:Gamepad;
	var mouse:Mouse;

	public function new() {
		super();

		notifyOnInit(init);
		notifyOnUpdate(update);
	}

	function init() {
		keyboard = Input.getKeyboard();
		gamepad = Input.getGamepad();
		mouse = Input.getMouse();

		camera = cast(object, CameraObject);
	}

	function update() {
		if (Input.occupied) return;

		var moveForward = keyboard.down("w") || keyboard.down("up");
		var moveBackward = keyboard.down("s") || keyboard.down("down");
		var strafeLeft = keyboard.down("a") || keyboard.down("left");
		var strafeRight = keyboard.down("d") || keyboard.down("right");
		var strafeUp = keyboard.down("e");
		var strafeDown = keyboard.down("q");
		var fast = keyboard.down("shift") ? 2.0 : (keyboard.down("alt") ? 0.5 : 1.0);

		if (gamepad != null) {
			dir.set(0, 0, 0);

			if (Math.abs(gamepad.leftStick.y) > 0.05) {
				yvec.setFrom(camera.look());
				yvec.mult(gamepad.leftStick.y);
				dir.add(yvec);
			}
			if (Math.abs(gamepad.leftStick.x) > 0.05) {
				xvec.setFrom(camera.right());
				xvec.mult(gamepad.leftStick.x);
				dir.add(xvec);
			}
			if (gamepad.down("r1") > 0.0) dir.addf(0, 0, 1);
			if (gamepad.down("l1") > 0.0) dir.addf(0, 0, -1);

			var d = Time.delta * speed * fast;
			camera.move(dir, d);

			if (Math.abs(gamepad.rightStick.x) > 0.1) {
				camera.rotate(Vec4.zAxis(), -gamepad.rightStick.x / 15.0);
			}
			if (Math.abs(gamepad.rightStick.y) > 0.1) {
				camera.rotate(camera.right(), gamepad.rightStick.y / 15.0);
			}
		}
		
		if (moveForward || moveBackward || strafeRight || strafeLeft || strafeUp || strafeDown) {
			ease = 1.0;
			dir.set(0, 0, 0);
			if (moveForward) dir.addf(camera.look().x, camera.look().y, camera.look().z);
			if (moveBackward) dir.addf(-camera.look().x, -camera.look().y, -camera.look().z);
			if (strafeRight) dir.addf(camera.right().x, camera.right().y, camera.right().z);
			if (strafeLeft) dir.addf(-camera.right().x, -camera.right().y, -camera.right().z);
			if (strafeUp) dir.addf(0, 0, 1);
			if (strafeDown) dir.addf(0, 0, -1);
		}
		else {
			ease -= Time.delta * 15.0 * ease;
		}

		var d = Time.delta * speed * fast * ease;
		if (d > 0.0) camera.move(dir, d);

		if (mouse.down()) {
			camera.rotate(Vec4.zAxis(), -mouse.movementX / 200);
			camera.rotate(camera.right(), -mouse.movementY / 200);
		}
	}
}
