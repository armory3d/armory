package armory.logicnode;

import iron.object.Object;
import armory.trait.physics.RigidBody;

class GetRigidBodyPropertiesNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: Object = inputs[0].get();

		if (object == null) false;

		#if arm_physics
		var rigidBody = object.getTrait(RigidBody);

		return switch (from) {
			case 0: rigidBody.group;
			case 1: rigidBody.mask;
			case 2: rigidBody.animated;
			case 3: rigidBody.staticObj;
			case 4: rigidBody.angularDamping;
			case 5: rigidBody.linearDamping;
			case 6: rigidBody.friction;
			case 7: rigidBody.mass;
		default: null;
		}
		#end
		return null;
		
	}
}
