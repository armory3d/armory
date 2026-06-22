package armory.logicnode;

import iron.object.Object;

class GetPropertyNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: Object = inputs[0].get();
		var property: String = inputs[1].get();

		if (from == 0) {
			if (object == null || object.properties == null) return null;
			return object.properties.get(property);
		}
		else {
			return property;
		}
	}
}
