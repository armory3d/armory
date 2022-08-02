package armory.logicnode;

import armory.system.InputMap;

class OnInputMapNode extends LogicNode {

	var inputMap: Null<InputMap>;

	public function new(tree: LogicTree) {
		super(tree);

		tree.notifyOnUpdate(update);
	}

	function update() {
		var i = inputs[0].get();

		inputMap = InputMap.getInputMap(i);

		if (inputMap != null) {
			if (inputMap.started()) {
				runOutput(0);
			}

			if (inputMap.released()) {
				runOutput(1);
			}
		}
	}

	override function get(from: Int): Dynamic {
		if (from == 2) return inputMap.value();
		else return inputMap.lastKeyPressed;
	}
}
