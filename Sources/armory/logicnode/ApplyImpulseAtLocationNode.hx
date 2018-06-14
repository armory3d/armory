package armory.logicnode;

import iron.object.Object;
import iron.math.Vec4;
import armory.trait.physics.RigidBody;

class ApplyImpulseAtLocationNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:Object = inputs[1].get();
		var impulse:Vec4 = inputs[2].get();
		var location:Vec4 = inputs[3].get();
		
		if (object == null || impulse == null || location == null) return;

#if arm_physics
		var rb:RigidBody = object.getTrait(RigidBody);
		rb.applyImpulse(impulse, location);
#end

		super.run();
	}
}
