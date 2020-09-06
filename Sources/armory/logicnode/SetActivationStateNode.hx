package armory.logicnode;

import iron.object.Object;
import armory.trait.physics.RigidBody;

/**
define ACTIVE_TAG 1
define ISLAND_SLEEPING 2
define WANTS_DEACTIVATION 3
define DISABLE_DEACTIVATION 4
define DISABLE_SIMULATION 5
**/

class SetActivationStateNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		if (object == null) return;

		var state: Int = inputs[2].get();
		if (state < 0 || state > 5) return;

		#if arm_physics
		var rigidBody = object.getTrait(RigidBody);
		if (rigidBody != null) rigidBody.setActivationState(state);
		#end

		runOutput(0);
	}
}
