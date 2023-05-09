package armory.logicnode;

import iron.object.Object;

class GetNameNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: Object = inputs[0].get();

		if (object == null) return "";

		return object.name;
	}
}
