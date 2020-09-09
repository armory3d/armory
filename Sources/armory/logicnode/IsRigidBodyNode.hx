package armory.logicnode;

import iron.object.Object;
import armory.trait.physics.RigidBody;

class IsRigidBodyNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: Object = inputs[0].get();

		if (object == null) false;

		#if arm_physics
		var rigidBody = object.getTrait(RigidBody);
		if (rigidBody != null) return true;
		return false;
		#end
	}
}
