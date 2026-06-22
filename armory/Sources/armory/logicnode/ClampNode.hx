package armory.logicnode;

import kha.FastFloat;

class ClampNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): FastFloat {
		var value = inputs[0].get();
		var min = inputs[1].get();
		var max = inputs[2].get();

		return value < min ? min : value > max ? max : value;
	}
}
