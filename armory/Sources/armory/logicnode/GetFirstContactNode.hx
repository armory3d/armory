package armory.logicnode;

import iron.object.Object;
import armory.trait.physics.RigidBody;

class GetFirstContactNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: Object = inputs[0].get();
		if (object == null) return null;

#if arm_physics
		var physics = armory.trait.physics.PhysicsWorld.active;
		var rbs = physics.getContacts(object.getTrait(RigidBody));

		if (rbs != null && rbs.length > 0) return rbs[0].object;
#end

		return null;
	}
}
