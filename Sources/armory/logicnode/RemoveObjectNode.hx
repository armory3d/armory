package armory.logicnode;

import armory.object.Object;

class RemoveObjectNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:Object = inputs[1].get();
		
		if (object == null) return;

		object.remove();

		super.run();
	}
}
