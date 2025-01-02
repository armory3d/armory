package armory.logicnode;

import armory.system.InputMap;

class GetInputMapKeyNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var inputMap = inputs[0].get();
		var key = inputs[1].get();

		var k = InputMap.getInputMapKey(inputMap, key);

		if (k != null) {
			if (from == 0) return k.scale;
			else if (from == 1) return k.deadzone;
		}

		return null;
	}
}
