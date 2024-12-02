package armory.trait;

import iron.Trait;
import iron.system.Input;
import iron.math.Vec2;

@:access(iron.system.Input)
@:access(iron.system.Gamepad)
class VirtualGamepad extends Trait {

	var gamepad: Gamepad;

	var leftPadX = 0;
	var leftPadY = 0;
	var rightPadX = 0;
	var rightPadY = 0;

	var leftStickX = 0;
	var leftStickXLast = 0;
	var leftStickY = 0;
	var leftStickYLast = 0;
	var rightStickX = 0;
	var rightStickXLast = 0;
	var rightStickY = 0;
	var rightStickYLast = 0;

	var leftLocked = false;
	var rightLocked = false;

	@prop
	public var radius = 100; // Radius
	@prop
	public var offset = 40; // Offset

	public function new() {
		super();

		notifyOnInit(function() {

			gamepad = new Gamepad(0, true);
			Input.gamepads.push(gamepad);

			notifyOnUpdate(update);
			notifyOnRender2D(render2D);
		});
	}

	function update() {
		var r = radius;
		var o = offset;

		leftPadX = r + o;
		rightPadX = iron.App.w() - r - o;
		leftPadY = rightPadY = iron.App.h() - r - o;

		var mouse = Input.getMouse();
		if (mouse.started() && Vec2.distancef(mouse.x, mouse.y, leftPadX, leftPadY) <= r) {
			leftLocked = true;
		}
		else if (mouse.released()) {
			leftLocked = false;
		}

		if (mouse.started() && Vec2.distancef(mouse.x, mouse.y, rightPadX, rightPadY) <= r) {
			rightLocked = true;
		}
		else if (mouse.released()) {
			rightLocked = false;
		}

		if (leftLocked) {
			leftStickX = Std.int(mouse.x - leftPadX);
			leftStickY = Std.int(mouse.y - leftPadY);

			var l = Math.sqrt(leftStickX * leftStickX + leftStickY * leftStickY);
			if (l > r) {
				var x = r * (leftStickX / Math.sqrt(leftStickX * leftStickX + leftStickY * leftStickY));
				var y = r * (leftStickY / Math.sqrt(leftStickX * leftStickX + leftStickY * leftStickY));
				leftStickX = Std.int(x);
				leftStickY = Std.int(y);
			}
		}
		else {
			leftStickX = 0;
			leftStickY = 0;
		}

		if (rightLocked) {
			rightStickX = Std.int(mouse.x - rightPadX);
			rightStickY = Std.int(mouse.y - rightPadY);

			var l = Math.sqrt(rightStickX * rightStickX + rightStickY * rightStickY);
			if (l > r) {
				var x = r * (rightStickX / Math.sqrt(rightStickX * rightStickX + rightStickY * rightStickY));
				var y = r * (rightStickY / Math.sqrt(rightStickX * rightStickX + rightStickY * rightStickY));
				rightStickX = Std.int(x);
				rightStickY = Std.int(y);
			}
		}
		else {
			rightStickX = 0;
			rightStickY = 0;
		}

		if (leftStickX != leftStickXLast) {
			gamepad.axisListener(0, leftStickX / r);
		}
		if (leftStickY != leftStickYLast) {
			gamepad.axisListener(1, leftStickY / r);
		}
		if (rightStickX != rightStickXLast) {
			gamepad.axisListener(2, rightStickX / r);
		}
		if (rightStickY != rightStickYLast) {
			gamepad.axisListener(3, rightStickY / r);
		}

		leftStickXLast = leftStickX;
		leftStickYLast = leftStickY;
		rightStickXLast = rightStickX;
		rightStickYLast = rightStickY;
	}

	function render2D(g: kha.graphics2.Graphics) {
		var r = radius;

		g.color = 0xffaaaaaa;

		zui.GraphicsExtension.fillCircle(g, leftPadX, leftPadY, r);
		zui.GraphicsExtension.fillCircle(g, rightPadX, rightPadY, r);

		var r2 = Std.int(r / 2.2);
		g.color = 0xffffff44;
		zui.GraphicsExtension.fillCircle(g, leftPadX + leftStickX, leftPadY + leftStickY, r2);
		zui.GraphicsExtension.fillCircle(g, rightPadX + rightStickX, rightPadY + rightStickY, r2);

		g.color = 0xffffffff;
	}
}
