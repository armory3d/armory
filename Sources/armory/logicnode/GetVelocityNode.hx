package armory.logicnode;

import iron.object.Object;
import armory.trait.physics.RigidBody;

class GetVelocityNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var object:Object = inputs[0].get();
		if (object == null) return null;

#if arm_physics
		var rb:RigidBody = object.getTrait(RigidBody);

		if (rb != null) {
			if (from == 0) return rb.getLinearVelocity();
			else if (from == 1) return rb.getAngularVelocity();
			// rb.getLinearFactor(); // TODO
			// rb.getAngularFactor(); // TODO
		}
#end
		return null;
	}
}
