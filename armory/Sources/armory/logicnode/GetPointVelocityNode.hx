package armory.logicnode;

import iron.math.Vec4;
import iron.object.Object;
import armory.trait.physics.RigidBody;

class GetPointVelocityNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: Object = inputs[0].get();
		var point: Vec4 = inputs[1].get();

		if (object == null || point == null)
			return null;

		#if arm_physics
		var rb: RigidBody = object.getTrait(RigidBody);

		return rb.getPointVelocity(point.x, point.y, point.z);
		#end

		return null;
	}

}
