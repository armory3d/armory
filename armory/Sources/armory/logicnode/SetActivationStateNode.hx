package armory.logicnode;

import iron.object.Object;
import armory.trait.physics.RigidBody;

/**
define ISLAND_SLEEPING 2
define WANTS_DEACTIVATION 3
**/

class SetActivationStateNode extends LogicNode {

	public var property0: String;
	public var state: Int;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		if (object == null) return;

#if arm_physics
		var rigidBody = object.getTrait(RigidBody);

		switch (property0) {
		case "inactive":
			state = 0; // Inactive Tag
		case "active":
			state = 1; // Active Tag
		case "always active":
			state = 4 ; // Disable Deactivation
		case "always inactive":
			state = 5; // Disable Simulation
		}
		rigidBody.setActivationState(state);

#end

		runOutput(0);
	}
}
