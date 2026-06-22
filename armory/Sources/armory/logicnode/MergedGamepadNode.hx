package armory.logicnode;

class MergedGamepadNode extends LogicNode {

	public var property0: String;
	public var property1: String;

	public function new(tree: LogicTree) {
		super(tree);

		tree.notifyOnUpdate(update);
	}

	function update() {
		var num: Int = inputs[0].get();
		var gamepad = iron.system.Input.getGamepad(num);
		if (gamepad == null) return;
		var b = false;
		switch (property0) {
		case "started":
			b = gamepad.started(property1);
		case "down":
			b = gamepad.down(property1) > 0.0;
		case "released":
			b = gamepad.released(property1);
		// case "Moved Left":
			// b = gamepad.leftStick.movementX != 0 || gamepad.leftStick.movementY != 0;
		// case "Moved Right":
			// b = gamepad.rightStick.movementX != 0 || gamepad.rightStick.movementY != 0;
		}
		if (b) runOutput(0);
	}

	override function get(from: Int): Dynamic {
		var num: Int = inputs[0].get();
		var gamepad = iron.system.Input.getGamepad(num);
		switch (property0) {
		case "started":
			return gamepad.started(property1);
		case "down":
			return gamepad.down(property1) > 0.0;
		case "released":
			return gamepad.released(property1);
		// case "Moved Left":
			// return (gamepad.leftStick.movementX != 0 || gamepad.leftStick.movementY != 0) ? 1.0 : 0.0;
		// case "Moved Right":
			// return (gamepad.rightStick.movementX != 0 || gamepad.rightStick.movementY != 0) ? 1.0 : 0.0;
		}
		return 0.0;
	}
}
