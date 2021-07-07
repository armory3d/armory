package armory.logicnode;

import armory.system.InputMap;

class RemoveInputMapKeyNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var inputMap = inputs[1].get();
		var key = inputs[2].get();

		var k = InputMap.getInputMapKey(inputMap, key);

		if (k != null) {
			if (InputMap.getInputMap(inputMap).removeKey(k)) {
				runOutput(0);
			}
		}
	}
}
