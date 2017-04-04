package armory.logicnode;

import armory.object.Object;

class GetPropertyNode extends Node {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var object:Object = inputs[0].get();
		var property:String = inputs[1].get();

		return Reflect.getProperty(object, property);
	}
}
