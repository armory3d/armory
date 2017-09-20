package armory.logicnode;

import armory.object.Object;
import armory.math.Vec4;
import armory.trait.internal.RigidBody;

class ApplyImpulseNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:Object = inputs[1].get();
		var impulse:Vec4 = inputs[2].get();
		
		if (object == null) return;

#if arm_physics
		var rb:RigidBody = object.getTrait(RigidBody);
		rb.applyImpulse(impulse);
#end

		super.run();
	}
}
