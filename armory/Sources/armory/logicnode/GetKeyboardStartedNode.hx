package armory.logicnode;

import iron.system.Input;

class GetKeyboardStartedNode extends LogicNode {

	var kb = Input.getKeyboard();
	var keyStarted: Null<String>;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		keyStarted = null;

		for (k in Keyboard.keys) {
			if (kb.started(k)) {
				keyStarted = k;
				break;
			}
		}

		if (keyStarted != null) {
			runOutput(0);
		}
	}

	override function get(from: Int) {
		return keyStarted;
	}
}
