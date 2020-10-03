package armory.logicnode;

import iron.object.Object;
import armory.trait.physics.RigidBody;

class GetVelocityNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: Object = inputs[0].get();
		if (object == null) return null;

#if arm_physics
		var rb: RigidBody = object.getTrait(RigidBody);

		return switch (from) {
			case 0: rb.getLinearVelocity();
			case 1: rb.getAngularVelocity();
			default: null;
		}
#end
	return null;
	}
}
