package armory.logicnode;

import iron.object.Object;
import armory.trait.physics.RigidBody;

class HasContactArrayNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object1: Object = inputs[0].get();
		var objects: Array<Object> = inputs[1].get();
		if (object1 == null || objects == null) return false;

#if arm_physics
		var physics = armory.trait.physics.PhysicsWorld.active;
		var rb1 = object1.getTrait(RigidBody);
		var rbs = physics.getContacts(rb1);
		
		if (rb1 != null && rbs != null) {
			for (object2 in objects) {
				var rb2 = object2.getTrait(RigidBody);
				for (rb in rbs) {
					if (rb == rb2) {
						return true;
					}
				}
			}
		}
#end
		return false;
	}
}
