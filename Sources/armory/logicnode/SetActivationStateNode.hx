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
		
		if (rigidBody == null) return;

		switch (property0) {
		case "Inactive":
			state = 0; // Inactive Tag
		case "Active":
			state = 1; // Active Tag
		case "Always Active":
			state = 4 ; // Disable Deactivation
		case "Always Inactive":
			state = 5; // Disable Simulation
		}
		rigidBody.setActivationState(state);

		#end

		runOutput(0);
	}
}
