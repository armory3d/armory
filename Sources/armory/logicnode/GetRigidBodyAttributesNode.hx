package armory.logicnode;

import iron.object.Object;
import armory.trait.physics.RigidBody;

class GetRigidBodyAttributesNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: Object = inputs[0].get();

		if (object == null) false;

		#if arm_physics
		var rigidBody = object.getTrait(RigidBody);

		if (from == 0) return rigidBody.group;
        else if (from == 1) return rigidBody.mask;
		else if (from == 2) return rigidBody.animated;
		else if (from == 3) return rigidBody.staticObj;
		else if (from == 4) return rigidBody.angularDamping;
		else if (from == 5) return rigidBody.linearDamping;
		else if (from == 6) return rigidBody.friction;
		else if (from == 7) return rigidBody.mass;
		#end
		return null;
		
	}
}
