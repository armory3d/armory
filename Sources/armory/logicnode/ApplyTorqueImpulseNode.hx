package armory.logicnode;

import iron.object.Object;
import iron.math.Vec4;
import armory.trait.physics.RigidBody;

using armory.object.TransformExtension;

class ApplyTorqueImpulseNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var torque: Vec4 = inputs[2].get();
		var local: Bool = inputs.length > 3 ? inputs[3].get() : false;

		if (object == null || torque == null) return;

#if arm_physics
		var rb: RigidBody = object.getTrait(RigidBody);

		!local ? rb.applyTorqueImpulse(torque) : rb.applyTorqueImpulse(object.transform.worldVecToOrientation(torque));
#end

		runOutput(0);
	}

}
