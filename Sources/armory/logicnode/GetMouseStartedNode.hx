package armory.logicnode;

import iron.system.Input;

class GetMouseStartedNode extends LogicNode {

	var m = Input.getMouse();
	var buttonStarted: Null<String>;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		buttonStarted = null;

		for (b in Mouse.buttons) {
			if (m.started(b)) {
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
