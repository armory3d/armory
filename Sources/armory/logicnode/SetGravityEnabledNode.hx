package armory.logicnode;

import iron.object.Object;
#if arm_physics
import armory.trait.physics.RigidBody;
#end

/**
   Enable or disable the gravity for a specific object.
**/
class SetGravityEnabledNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var gravityEnabled: Bool = inputs[2].get();
		if (object == null) return;

		#if arm_physics
		var body = object.getTrait(RigidBody);
		if (body != null) {
			if (gravityEnabled) {
				body.enableGravity();
			}
			else {
				body.disableGravity();
			}
		}
		#end

		runOutput(0);
	}
}
