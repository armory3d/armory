package armory.logicnode;

import iron.object.Object;
import iron.math.Mat4;
import iron.math.Vec4;
import armory.trait.physics.RigidBody;

class TranslateObjectNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		var object:Object = inputs[1].get();
		var vec:Vec4 = inputs[2].get();
		var local:Bool = inputs.length > 3 ? inputs[3].get() : false;

		if (object == null || vec == null) return;

		if(!local) {
			object.transform.loc.add(vec);
			object.transform.buildMatrix();
		}
		else {
			var look = object.transform.world.look().mult(vec.y);
			var right = object.transform.world.right().mult(vec.x);
			var up = object.transform.world.up().mult(vec.z);
			object.transform.loc.add(look);
			object.transform.loc.add(right);
			object.transform.loc.add(up);
			object.transform.buildMatrix();
		}
		
		#if arm_physics
		var rigidBody = object.getTrait(RigidBody);
		if (rigidBody != null) rigidBody.syncTransform();
		#end

		runOutput(0);
	}
}
