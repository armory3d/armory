package armory.logicnode;

import iron.object.Object;

class GetVisibleNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var object:Object = inputs[0].get();

		if (object == null) false;

		return object.visible;
	}
}
