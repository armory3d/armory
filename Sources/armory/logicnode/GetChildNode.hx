package armory.logicnode;

import armory.object.Object;

class GetChildNode extends Node {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var object:Object = inputs[0].get();
		var childName:String = inputs[1].get();

		if (object == null) object = tree.object;

		return object.getChild(childName);
	}
}
