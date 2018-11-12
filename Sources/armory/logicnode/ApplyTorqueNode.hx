package armory.logicnode;

import iron.object.Object;
import iron.math.Vec4;
import armory.trait.physics.RigidBody;

class ApplyTorqueNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		var object:Object = inputs[1].get();
		var torque:Vec4 = inputs[2].get();
		
		if (object == null || torque == null) return;

#if arm_physics
		var rb:RigidBody = object.getTrait(RigidBody);
		rb.applyTorque(torque);
#end

		runOutput(0);
	}
}
