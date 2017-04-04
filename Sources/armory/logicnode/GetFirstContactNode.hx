package armory.logicnode;

import armory.object.Object;
import armory.trait.internal.RigidBody;

class GetFirstContactNode extends Node {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var object:Object = inputs[0].get();

#if arm_physics
		var physics = armory.trait.internal.PhysicsWorld.active;
		var rbs = physics.getContacts(object.getTrait(RigidBody));
		if (rbs != null) return rbs[0].object;
#end
		return null;
	}
}
