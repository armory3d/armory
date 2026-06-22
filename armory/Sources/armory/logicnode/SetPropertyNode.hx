package armory.logicnode;

import iron.object.Object;

class SetPropertyNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var property: String = inputs[2].get();
		var value: Dynamic = inputs[3].get();

		if (object == null) return;
		if (object.properties == null) object.properties = new Map();
		object.properties.set(property, value);

		runOutput(0);
	}
}
