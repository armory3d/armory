package armory.logicnode;

import iron.object.Object;
import armory.trait.physics.RigidBody;

class OnContactNode extends LogicNode {

	public var property0: String;
	var lastContact = false;

	public function new(tree: LogicTree) {
		super(tree);

		tree.notifyOnUpdate(update);
	}

	function update() {
		var object1: Object = inputs[0].get();
		var object2: Object = inputs[1].get();

		if (object1 == null) object1 = tree.object;
		if (object2 == null) object2 = tree.object;

		var contact = false;

#if arm_physics
		var physics = armory.trait.physics.PhysicsWorld.active;
		var rb1 = object1.getTrait(RigidBody);
		if (rb1 != null) {
			var rbs = physics.getContacts(rb1);
			if (rbs != null) {
				var rb2 = object2.getTrait(RigidBody);
				for (rb in rbs) {
					if (rb == rb2) {
						contact = true;
						break;
					}
				}
			}
		}
#end

		var b = false;
		switch (property0) {
		case "begin":
			b = contact && !lastContact;
		case "overlap":
			b = contact;
		case "end":
			b = !contact && lastContact;
		}

		lastContact = contact;

		if (b) runOutput(0);
	}
}
