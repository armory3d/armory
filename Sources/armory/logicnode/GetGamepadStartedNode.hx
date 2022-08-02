package armory.logicnode;

import iron.system.Input;

class GetGamepadStartedNode extends LogicNode {

	var buttonStarted: Null<String>;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var g = Input.getGamepad(inputs[1].get());

		buttonStarted = null;

		for (b in Gamepad.buttons) {
			if (g.started(b)) {
				buttonStarted = b;
				break;
			}
		}

		if (buttonStarted != null) {
			runOutput(0);
		}
	}

	override function get(from: Int) {
		return buttonStarted;
	}
}
