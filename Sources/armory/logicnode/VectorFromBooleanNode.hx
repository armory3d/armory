package armory.logicnode;

import iron.math.Vec4;

class VectorFromBooleanNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {

		var boolX = inputs[0].get();
		var boolNegX = inputs[1].get();
		var boolY = inputs[2].get();
		var boolNegY = inputs[3].get();
		var boolZ = inputs[4].get();
		var boolNegZ = inputs[5].get();

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
