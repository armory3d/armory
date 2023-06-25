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
		var localLinear: Bool = inputs[1].get();
		var localAngular: Bool = inputs[2].get();

		if (object == null) return null;

#if arm_physics
		var rb: RigidBody = object.getTrait(RigidBody);

		if (from == 0) {
		!localLinear ? return rb.getLinearVelocity() : return object.transform.getWorldVectorAlongLocalAxis(rb.getLinearVelocity());
		}

		else {
		!localAngular ? return rb.getAngularVelocity() : return object.transform.getWorldVectorAlongLocalAxis(rb.getAngularVelocity());
		}
#end

	return null;
	}

}
