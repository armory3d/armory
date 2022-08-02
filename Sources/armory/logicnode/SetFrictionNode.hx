package armory.logicnode;

import iron.object.Object;
import armory.trait.physics.RigidBody;

class SetFrictionNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();

		if (object == null) return;

		var friction = inputs[2].get();

#if arm_physics
		var rigidBody = object.getTrait(RigidBody);

		rigidBody.setFriction(friction);
#end

		runOutput(0);
	}
}
