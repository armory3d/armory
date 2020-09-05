package armory.logicnode;

import iron.object.Object;
import iron.math.Vec4;
import armory.trait.physics.RigidBody;

class ApplyForceAtLocationNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var force: Vec4 = inputs[2].get();
		var localForce: Bool = inputs[3].get();
        var location: Vec4 = inputs[4].get();
		var localLoc: Bool =  inputs[5].get();

		if (object == null || force == null || location == null) return;

#if arm_physics
		var rb: RigidBody = object.getTrait(RigidBody);

		if (rb == null) return;

		if (localLoc) {
			location.applyQuat(object.transform.rot);
		}
		if(!localForce){
			rb.applyForce(force,location);
		}
		else {
			var look = object.transform.world.look().mult(force.y);
			var right = object.transform.world.right().mult(force.x);
			var up = object.transform.world.up().mult(force.z);
			rb.applyForce(look, location);
			rb.applyForce(right, location);
			rb.applyForce(up, location);
		}
#end

		runOutput(0);
	}
}
