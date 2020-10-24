package armory.logicnode;

import iron.object.Object;
import iron.math.Vec4;

class VectorToObjectSpaceNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {

		var object: Object = inputs[0].get();
		var vecIn: Vec4 = inputs[1].get();

		if (object == null || vecIn == null) return null;

		var vecOut = new Vec4();

		var right = object.transform.world.right().mult(vecIn.x);
		var look = object.transform.world.look().mult(vecIn.y);
		var up = object.transform.world.up().mult(vecIn.z);

		vecOut.add(right).add(look).add(up);

		return vecOut;
	}
}
