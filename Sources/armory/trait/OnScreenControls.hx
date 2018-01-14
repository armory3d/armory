package armory.trait;

import iron.Trait;
import iron.system.Input;
import iron.math.Vec2;

class OnScreenControls extends Trait {

	var leftPadX = 0;
	var leftPadY = 0;
	var rightPadX = 0;
	var rightPadY = 0;

	var leftStickX = 0;
	var leftStickY = 0;
	var rightStickX = 0;
	var rightStickY = 0;

	var leftLocked = false;
	var rightLocked = false;

	var r = 100; // Radius
	var o = 40; // Offset

	public function new() {
		super();

		notifyOnInit(function() {
			
			leftPadX = r + o;
			rightPadX = iron.App.w() - r - o;
			leftPadY = rightPadY = iron.App.h() - r - o;

			notifyOnUpdate(update);
			notifyOnRender2D(render2D);
		});
	}

	function update() {
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

			leftStickX = Std.int(iron.math.Math.clamp(leftStickX, -r, r));
			leftStickY = Std.int(iron.math.Math.clamp(leftStickY, -r, r));
		}

		if (rightLocked) {
			rightStickX = Std.int(mouse.x - rightPadX);
			rightStickY = Std.int(mouse.y - rightPadY);

			rightStickX = Std.int(iron.math.Math.clamp(rightStickX, -r, r));
			rightStickY = Std.int(iron.math.Math.clamp(rightStickY, -r, r));
		}
	}

	function render2D(g:kha.graphics2.Graphics) {
		g.color = 0xffffffff;
		g.fillRect(leftPadX - r, leftPadY - r, r * 2, r * 2);
		g.fillRect(rightPadX - r, rightPadY - r, r * 2, r * 2);

		var r2 = Std.int(r / 2.5);
		g.color = 0xff000000;
		g.fillRect(leftPadX - r2 + leftStickX, leftPadY - r2 + leftStickY, r2 * 2, r2 * 2);
		g.fillRect(rightPadX - r2 + rightStickX, rightPadY - r2 +rightStickY, r2 * 2, r2 * 2);

		g.color = 0xffffffff;
	}
}
