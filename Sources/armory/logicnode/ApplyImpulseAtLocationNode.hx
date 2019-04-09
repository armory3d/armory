package armory.logicnode;

import iron.object.Object;
import iron.math.Vec4;
import armory.trait.physics.RigidBody;

class ApplyImpulseAtLocationNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		var object:Object = inputs[1].get();
		var impulse:Vec4 = inputs[2].get();
		var location:Vec4 = inputs[3].get();
		var local:Bool = inputs.length > 3 ? inputs[3].get() : false;
		
		if (object == null || impulse == null || location == null) return;

#if arm_physics
		var rb:RigidBody = object.getTrait(RigidBody);
		if (!local) {
			rb.applyImpulse(impulse, location); }
		else {
			var look = object.transform.world.look().mult(impulse.y);
			var right = object.transform.world.right().mult(impulse.x);
			var up = object.transform.world.up().mult(impulse.z);
			rb.applyImpulse(look, location);
			rb.applyImpulse(right, location);
			rb.applyImpulse(up, location);
		}
#end

		runOutput(0);
	}
}
