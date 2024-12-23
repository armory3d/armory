package armory.logicnode;

import iron.math.Vec4;

class SeparateVectorNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var vector: Vec4 = inputs[0].get();
		if (vector == null) return 0.0;

		if (from == 0) return vector.x;
		else if (from == 1) return vector.y;
		else return vector.z;
	}
}
