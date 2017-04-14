package armory.logicnode;

import armory.object.Object;

class GetLocationNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var object:Object = inputs[0].get();

		if (object == null) object = tree.object;

		return object.transform.scale;
	}
}
