package armory.logicnode;

import iron.object.Object;

class RemoveObjectNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		var object:Object = inputs[1].get();
		
		if (object == null) return;

		object.remove();

		runOutput(0);
	}
}
