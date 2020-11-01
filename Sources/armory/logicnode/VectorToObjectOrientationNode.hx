package armory.logicnode;

import iron.object.Object;
import iron.math.Vec4;

using armory.object.TransformExtension;

class VectorToObjectOrientationNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {

		var object: Object = inputs[0].get();
		var vec: Vec4 = inputs[1].get();

		if (object == null || vec == null) return null;

		return object.transform.worldVecToOrientation(vec);
	}

}
