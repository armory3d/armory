package armory.logicnode;

class GetHaxePropertyNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: Dynamic = inputs[0].get();
		var property: String = inputs[1].get();

		if (object == null) return null;

		return Reflect.getProperty(object, property);
	}
}
