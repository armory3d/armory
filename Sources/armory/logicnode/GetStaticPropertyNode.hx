package armory.logicnode;

import iron.object.Object;

class GetStaticPropertyNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var className:String = inputs[0].get();
		var property:String = inputs[1].get();

		var cl = Type.resolveClass(className);
		if (cl == null) return null;

		return Reflect.getProperty(cl, property);
	}
}
