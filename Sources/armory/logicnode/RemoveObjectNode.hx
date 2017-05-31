package armory.logicnode;

import armory.object.Object;

class RemoveObjectNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:Object = inputs[1].get();

		// Prevent self-destruct
		if (object != null && object != tree.object) object.remove();

		super.run();
	}
}
