package armory.logicnode;

import iron.object.Object;
import armory.trait.physics.RigidBody;

class GetRigidBodyDataNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: Object = inputs[0].get();

		if (object == null) return null;

		#if arm_physics
		var rigidBody = object.getTrait(RigidBody);

		return switch (from) {
			case 0:
			if (rigidBody == null) return false;
			return true;

			//case 1: ; // collision shape
			//case 2: ; // activation state
			case 1: rigidBody.group;
			case 2: rigidBody.mask;
			case 3: rigidBody.animated;
			case 4: rigidBody.staticObj;
			case 5: rigidBody.angularDamping;
			case 6: rigidBody.linearDamping;
			case 7: rigidBody.friction;
			case 8: rigidBody.mass;
		default: null;
		}
		#end
	}
}
