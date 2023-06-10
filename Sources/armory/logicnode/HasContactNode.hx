package armory.logicnode;

import iron.object.Object;
import armory.trait.physics.RigidBody;

class HasContactNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object1: Object = inputs[0].get();
		var object2: Object = inputs[1].get();

		if (object1 == null || object2 == null) return false;

#if arm_physics
		var physics = armory.trait.physics.PhysicsWorld.active;
		var rb2 = object2.getTrait(RigidBody);
		var rbs = physics.getContacts(object1.getTrait(RigidBody));
		if (rbs != null) for (rb in rbs) if (rb == rb2) return true;
#end
		return false;
	}
}
