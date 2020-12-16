package armory.logicnode;

import iron.math.Vec4;
import iron.object.Object;

using armory.object.TransformExtension;

class WorldVectorToLocalSpaceNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Vec4 {
		var object: Object = inputs[0].get();
		var worldVec: Vec4 = inputs[1].get();

		if (object == null || worldVec == null) return null;

		var localVec: Vec4 = new Vec4();

		localVec.x = worldVec.dot(object.transform.right());
		localVec.y = worldVec.dot(object.transform.look());
		localVec.z = worldVec.dot(object.transform.up());

		return localVec;
	}
}
