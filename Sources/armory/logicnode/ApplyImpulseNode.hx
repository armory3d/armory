package armory.logicnode;

import iron.object.Object;
import iron.math.Vec4;
import armory.trait.physics.RigidBody;

class ApplyImpulseNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		var object:Object = inputs[1].get();
		var impulse:Vec4 = inputs[2].get();
		var local:Bool = inputs[3].get();
		var look:Vec4; var right:Vec4; var up:Vec4;
		
		if (object == null || impulse == null) return;

#if arm_physics
		var rb:RigidBody = object.getTrait(RigidBody);
		if (!local) {
		rb.applyImpulse(impulse);
		}
		else {
			look = object.transform.world.look().mult(impulse.x);
			right = object.transform.world.right().mult(impulse.y);
			up = object.transform.world.up().mult(impulse.z);
			rb.applyImpulse(look); rb.applyImpulse(right); rb.applyImpulse(up);
		}
#end

		runOutput(0);
	}
}
