package armory.logicnode;

import armory.object.Object;

class GetVisibleNode extends Node {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var object:Object = inputs[0].get();

		return object.visible;
	}
}
