package armory.logicnode;

import iron.object.Object;
import armory.trait.physics.RigidBody;

using armory.object.TransformExtension;

class GetVelocityNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: Object = inputs[0].get();
		var localLinear: Bool = inputs.length > 1 ? inputs[1].get() : false;
		var localAngular: Bool = inputs.length > 2 ? inputs[2].get() : false;

		if (object == null) return null;

#if arm_physics
		var rb: RigidBody = object.getTrait(RigidBody);

		if (from == 0) {
		!localLinear ? return rb.getLinearVelocity() : return object.transform.worldVecToOrientation(rb.getLinearVelocity());
		}

		else {
		!localAngular ? return rb.getAngularVelocity() : return object.transform.worldVecToOrientation(rb.getAngularVelocity());
		}
#end

	return null;
	}

}
