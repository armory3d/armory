package armory.logicnode;

import iron.math.Vec4;

class DistanceNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var vector1: Vec4 = inputs[0].get();
		var vector2: Vec4 = inputs[1].get();

		if (vector1 == null || vector2 == null) return 0;

		return iron.math.Vec4.distance(vector1, vector2);
	}
}
