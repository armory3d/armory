package armory.logicnode;

import iron.object.Object;
import iron.math.Vec4;

class VectorToObjectOrientationNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {

		var object: Object = inputs[0].get();
		var vec: Vec4 = inputs[1].get();

		if (object == null || vec == null) return null;

		return vec.applyQuat(object.transform.rot);
	}

}
