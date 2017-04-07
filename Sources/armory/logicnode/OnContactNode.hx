package armory.logicnode;

import armory.object.Object;
import armory.trait.internal.RigidBody;

class OnContactNode extends Node {

	public var property0:String;
	var lastContact = false;

	public function new(tree:LogicTree) {
		super(tree);

		tree.notifyOnUpdate(update);
	}

	function update() {
		var object1:Object = inputs[0].get();
		var object2:Object = inputs[1].get();

		if (object1 == null) object1 = tree.object;
		if (object2 == null) object2 = tree.object;

		var contact = false;

#if arm_physics
		var physics = armory.trait.internal.PhysicsWorld.active;
		var rb2 = object2.getTrait(RigidBody);
		var rbs = physics.getContacts(object1.getTrait(RigidBody));
		if (rbs != null) {
			for (rb in rbs) {
				if (rb == rb2) {
					contact = true;
					break;
				}
			}
		}
#end

		var b = false;
		switch (property0) {
		case "Begin":
			b = contact && !lastContact;
		case "End":
			b = !contact && lastContact;
		case "Overlap":
			b = contact;
		}

		lastContact = contact;

		if (b) run();
	}
}
