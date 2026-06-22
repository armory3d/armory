package armory.logicnode;

class GamepadSticksNode extends LogicNode {

	public var property0: String;
	public var property1: String;
	public var property2: String;
	var started = false;
	var previousb = false;

	var gstarted = false;
	var gpreviousb = false;

	public function new(tree: LogicTree) {
		super(tree);

		tree.notifyOnUpdate(update);
	}

	function update() {
		var num: Int = inputs[0].get();
		var gamepad = iron.system.Input.getGamepad(num);
		if (gamepad == null) return;
		var b = false;

		if(property1 == 'LeftStick')
			switch (property2) {
			case 'up':
				b = gamepad.leftStick.y == -1;
			case 'down':
				b = gamepad.leftStick.y == 1;
			case 'left':
				b = gamepad.leftStick.x == -1;
			case 'right':
				b = gamepad.leftStick.x == 1;
			case 'up-left':
				b = gamepad.leftStick.y == -1 && gamepad.leftStick.x == -1;
			case 'up-right':
				b = gamepad.leftStick.y == -1 && gamepad.leftStick.x == 1;
			case 'down-left':
				b = gamepad.leftStick.y == 1 && gamepad.leftStick.x == -1;
			case 'down-right':
				b = gamepad.leftStick.y == 1 && gamepad.leftStick.x == 1;
			}
		else
			switch (property2) {
			case 'up':
				b = gamepad.rightStick.y == -1;
			case 'down':
				b = gamepad.rightStick.y == 1;
			case 'left':
				b = gamepad.rightStick.x == -1;
			case 'right':
				b = gamepad.rightStick.x == 1;
			case 'up-left':
				b = gamepad.rightStick.y == -1 && gamepad.rightStick.x == -1;
			case 'up-right':
				b = gamepad.rightStick.y == -1 && gamepad.rightStick.x == 1;
			case 'down-left':
				b = gamepad.rightStick.y == 1 && gamepad.rightStick.x == -1;
			case 'down-right':
				b = gamepad.rightStick.y == 1 && gamepad.rightStick.x == 1;
			}

		if (b) previousb = b;
		if (b != previousb) started = false;

		if (property0 == 'Started' && b && !started){started = true; runOutput(0);}
		else if (property0 == 'Down' && b){previousb = b; runOutput(0);}
		else if (property0 == 'Released' && b != previousb){previousb = b; runOutput(0);}

	}

	override function get(from: Int): Dynamic {
		var num: Int = inputs[0].get();
		var gamepad = iron.system.Input.getGamepad(num);

		if (gamepad == null) return false;
		var b = false;

		if(property1 == 'LeftStick')
			switch (property2) {
			case 'up':
				b = gamepad.leftStick.y == -1;
			case 'down':
				b = gamepad.leftStick.y == 1;
			case 'left':
				b = gamepad.leftStick.x == -1;
			case 'right':
				b = gamepad.leftStick.x == 1;
			case 'up-left':
				b = gamepad.leftStick.y == -1 && gamepad.leftStick.x == -1;
			case 'up-right':
				b = gamepad.leftStick.y == -1 && gamepad.leftStick.x == 1;
			case 'down-left':
				b = gamepad.leftStick.y == 1 && gamepad.leftStick.x == -1;
			case 'down-right':
				b = gamepad.leftStick.y == 1 && gamepad.leftStick.x == 1;
			}
		else
			switch (property2) {
			case 'up':
				b = gamepad.rightStick.y == -1;
			case 'down':
				b = gamepad.rightStick.y == 1;
			case 'left':
				b = gamepad.rightStick.x == -1;
			case 'right':
				b = gamepad.rightStick.x == 1;
			case 'up-left':
				b = gamepad.rightStick.y == -1 && gamepad.rightStick.x == -1;
			case 'up-right':
				b = gamepad.rightStick.y == -1 && gamepad.rightStick.x == 1;
			case 'down-left':
				b = gamepad.rightStick.y == 1 && gamepad.rightStick.x == -1;
			case 'down-right':
				b = gamepad.rightStick.y == 1 && gamepad.rightStick.x == 1;
			}

		if (b) gpreviousb = b;
		if (b != gpreviousb) gstarted = false;

		if (property0 == 'Started' && b && !gstarted){gstarted = true; return true;}
		else if (property0 == 'Down' && b){gpreviousb = b; return true;}
		else if (property0 == 'Released' && b != gpreviousb){gpreviousb = b; return true;}

		return false;

	}
}
