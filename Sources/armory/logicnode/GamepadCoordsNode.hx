package armory.logicnode;

import iron.math.Vec4;

class GamepadCoordsNode extends LogicNode {

	var coords = new Vec4();

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var num: Int = inputs[0].get();
		var gamepad = iron.system.Input.getGamepad(num);
		if (from == 0) {
			coords.x = gamepad.leftStick.x;
			coords.y = gamepad.leftStick.y;
			return coords;
		}
		else if (from == 1) {
			coords.x = gamepad.rightStick.x;
			coords.y = gamepad.rightStick.y;
			return coords;
		}
		else if (from == 2) {
			coords.x = gamepad.leftStick.movementX;
			coords.y = gamepad.leftStick.movementY;
			return coords;
		}
		else if (from == 3) {
			coords.x = gamepad.rightStick.movementX;
			coords.y = gamepad.rightStick.movementY;
			return coords;
		}
		else if (from == 4) {
			return gamepad.down("l2");
		}
		else if (from == 5) {
			return gamepad.down("r2");
		}
		return null;
	}
}
