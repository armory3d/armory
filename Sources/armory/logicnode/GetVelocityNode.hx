package armory.logicnode;

import iron.object.Object;
import iron.math.Vec3;
#if arm_physics
import armory.trait.physics.RigidBody;
#end

class GetVelocityNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var object:Object = inputs[0].get();
		
		if (object == null) return null;

#if arm_physics
		var rb:RigidBody = object.getTrait(RigidBody);

		// rb.activate();
		if (rb != null) {
        	var btvec;

			if (from == 0) {
				btvec = rb.getLinearVelocity();
				return new Vec3(btvec.x(), btvec.y(), btvec.z());
			}
			// return rb.getLinearFactor(); //TODO
			else if (from == 1) {
				btvec = rb.getAngularVelocity();
				return new Vec3(btvec.x(), btvec.y(), btvec.z());
			}
			else {
				return new Vec3(0,0,0);
			}
			// rb.getAngularFactor(); //TODO
		}
#end
	return null;
	}
}
