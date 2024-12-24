package armory.trait;

import iron.Trait;
import iron.system.Input;
import iron.system.Time;
import iron.object.CameraObject;
import iron.math.Vec4;

class WalkNavigation extends Trait {

	public static var enabled = true;
	var speed = 5.0;
	var dir = new Vec4();
	var xvec = new Vec4();
	var yvec = new Vec4();
	var ease = 1.0;

	var camera: CameraObject;

	var keyboard: Keyboard;
	var gamepad: Gamepad;
	var mouse: Mouse;

	public function new() {
		super();
		notifyOnInit(init);
	}

	#if arm_debug @:keep #end
	function init() {
		keyboard = Input.getKeyboard();
		gamepad = Input.getGamepad();
		mouse = Input.getMouse();

		try {
			camera = cast(object, CameraObject);
		}
		catch (msg: String) {
			trace("Error occurred: " + msg + "\nWalkNavigation trait should be used with a camera object.");
		}

		if (camera != null){
			notifyOnUpdate(update);
		}
	}

	function update() {
		if (!enabled || Input.occupied) return;

		var moveForward = keyboard.down(keyUp) || keyboard.down("up");
		var moveBackward = keyboard.down(keyDown) || keyboard.down("down");
		var strafeLeft = keyboard.down(keyLeft) || keyboard.down("left");
		var strafeRight = keyboard.down(keyRight) || keyboard.down("right");
		var strafeUp = keyboard.down(keyStrafeUp);
		var strafeDown = keyboard.down(keyStrafeDown);
		var fast = keyboard.down("shift") ? 2.0 : (keyboard.down("alt") ? 0.5 : 1.0);

		if (gamepad != null) {
			var leftStickY = Math.abs(gamepad.leftStick.y) > 0.05;
			var leftStickX = Math.abs(gamepad.leftStick.x) > 0.05;
			var r1 = gamepad.down("r1") > 0.0;
			var l1 = gamepad.down("l1") > 0.0;
			var rightStickX = Math.abs(gamepad.rightStick.x) > 0.1;
			var rightStickY = Math.abs(gamepad.rightStick.y) > 0.1;

			if (leftStickY || leftStickX || r1 || l1 || rightStickX || rightStickY) {
				dir.set(0, 0, 0);

				if (leftStickY) {
					yvec.setFrom(camera.look());
					yvec.mult(gamepad.leftStick.y);
					dir.add(yvec);
				}
				if (leftStickX) {
					xvec.setFrom(camera.right());
					xvec.mult(gamepad.leftStick.x);
					dir.add(xvec);
				}
				if (r1) dir.addf(0, 0, 1);
				if (l1) dir.addf(0, 0, -1);

				var d = Time.delta * speed * fast;
				camera.transform.move(dir, d);

				if (rightStickX) {
					camera.transform.rotate(Vec4.zAxis(), -gamepad.rightStick.x / 15.0);
				}
				if (rightStickY) {
					camera.transform.rotate(camera.right(), gamepad.rightStick.y / 15.0);
				}
			}
		}

		if (moveForward || moveBackward || strafeRight || strafeLeft || strafeUp || strafeDown) {
			ease += Time.delta * 15;
			if (ease > 1.0) ease = 1.0;
			dir.set(0, 0, 0);
			if (moveForward) dir.addf(camera.look().x, camera.look().y, camera.look().z);
			if (moveBackward) dir.addf(-camera.look().x, -camera.look().y, -camera.look().z);
			if (strafeRight) dir.addf(camera.right().x, camera.right().y, camera.right().z);
			if (strafeLeft) dir.addf(-camera.right().x, -camera.right().y, -camera.right().z);
			#if arm_yaxisup
			if (strafeUp) dir.addf(0, 1, 0);
			if (strafeDown) dir.addf(0, -1, 0);
			#else
			if (strafeUp) dir.addf(0, 0, 1);
			if (strafeDown) dir.addf(0, 0, -1);
			#end
		}
		else {
			ease -= Time.delta * 20.0 * ease;
			if (ease < 0.0) ease = 0.0;
		}

		if (mouse.wheelDelta < 0) {
			speed *= 1.1;
		} else if (mouse.wheelDelta > 0) {
			speed *= 0.9;
			if (speed < 0.5) speed = 0.5;
		}

		var d = Time.delta * speed * fast * ease;
		if (d > 0.0) camera.transform.move(dir, d);

		if (mouse.down()) {
			#if arm_yaxisup
			camera.transform.rotate(Vec4.yAxis(), -mouse.movementX / 200);
			#else
			camera.transform.rotate(Vec4.zAxis(), -mouse.movementX / 200);
			#end
			camera.transform.rotate(camera.right(), -mouse.movementY / 200);
		}
	}

	#if arm_azerty
	static inline var keyUp = "z";
	static inline var keyDown = "s";
	static inline var keyLeft = "q";
	static inline var keyRight = "d";
	static inline var keyStrafeUp = "e";
	static inline var keyStrafeDown = "a";
	#else
	static inline var keyUp = "w";
	static inline var keyDown = "s";
	static inline var keyLeft = "a";
	static inline var keyRight = "d";
	static inline var keyStrafeUp = "e";
	static inline var keyStrafeDown = "q";
	#end
}
