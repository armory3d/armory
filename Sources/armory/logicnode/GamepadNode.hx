package armory.logicnode;

class GamepadNode extends LogicNode {

	public var property0:String;
	public var property1:String;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var num:Int = inputs[0].get();
		var gamepad = armory.system.Input.getGamepad(num);
		switch (property0) {
		case "Down":
			return gamepad.down(property1);
		case "Started":
			return gamepad.started(property1) ? 1.0 : 0.0;
		case "Released":
			return gamepad.released(property1) ? 1.0 : 0.0;
		// case "Moved Left":
			// return (gamepad.leftStick.movementX != 0 || gamepad.leftStick.movementY != 0) ? 1.0 : 0.0;
		// case "Moved Right":
			// return (gamepad.rightStick.movementX != 0 || gamepad.rightStick.movementY != 0) ? 1.0 : 0.0;
		}
		return 0.0;
	}
}
