package armory.logicnode;

import iron.math.Vec4;

class VectorFromBooleanNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {

		var boolX: Bool = inputs[0].get();
		var boolNegX: Bool = inputs[1].get();
		var boolY: Bool = inputs[2].get();
		var boolNegY: Bool = inputs[3].get();
		var boolZ: Bool = inputs[4].get();
		var boolNegZ: Bool = inputs[5].get();

		var vector = new Vec4();

		if (boolX == true) vector.x += 1;

		if (boolNegX == true) vector.x += -1;

		if (boolY == true) vector.y += 1;

		if (boolNegY == true) vector.y += -1;

		if (boolZ == true) vector.z += 1;

		if (boolNegZ == true) vector.z += -1;

		return vector.normalize();
	}
}
