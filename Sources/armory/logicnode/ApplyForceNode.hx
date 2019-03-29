package armory.logicnode;

import iron.object.Object;
import iron.math.Vec4;
import armory.trait.physics.RigidBody;

class ApplyForceNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		var object:Object = inputs[1].get();
		var force:Vec4 = inputs[2].get();
		var local:Bool = inputs[3].get();
		var look:Vec4; var right:Vec4; var up:Vec4;
		
		if (object == null || force == null) return;

#if arm_physics
		var rb:RigidBody = object.getTrait(RigidBody);
		if (!local) {
		rb.applyForce(force);
		}
		else {
			look = object.transform.world.look().mult(force.x);
			right = object.transform.world.right().mult(force.y);
			up = object.transform.world.up().mult(force.z);
			rb.applyForce(look); rb.applyImpulse(right); rb.applyImpulse(up);
		}
#end

		runOutput(0);
	}
}
