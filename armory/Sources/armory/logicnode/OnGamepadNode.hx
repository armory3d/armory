package armory.logicnode;

class OnGamepadNode extends LogicNode {

	public var property0: String;
	public var property1: String;

	@:deprecated("The 'On Gamepad' node is deprecated and will be removed in future SDK versions. Please use 'Gamepad' instead.")
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
		case "Down":
			b = gamepad.down(property1) > 0.0;
		case "Started":
			b = gamepad.started(property1);
		case "Released":
			b = gamepad.released(property1);
		// case "Moved Left":
			// b = gamepad.leftStick.movementX != 0 || gamepad.leftStick.movementY != 0;
		// case "Moved Right":
			// b = gamepad.rightStick.movementX != 0 || gamepad.rightStick.movementY != 0;
		}
		if (b) runOutput(0);
	}
}
