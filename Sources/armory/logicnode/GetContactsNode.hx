package armory.logicnode;

import armory.object.Object;
import armory.trait.internal.RigidBody;

class GetContactsNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var object:Object = inputs[0].get();

#if arm_physics
		var physics = armory.trait.internal.PhysicsWorld.active;
		var rbs = physics.getContacts(object.getTrait(RigidBody));
		var obs = [];
		if (rbs != null) for (rb in rbs) obs.push(rb.object);
		return obs;
#end
		return null;
	}
}
