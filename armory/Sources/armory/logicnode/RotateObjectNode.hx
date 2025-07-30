package armory.logicnode;

import iron.object.Object;
import iron.math.Quat;
import armory.trait.physics.RigidBody;

class RotateObjectNode extends LogicNode {

	public var property0 = "Local";

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var q: Quat = inputs[2].get();
		
		if (object == null || q == null) return;

		q.normalize();
		switch (property0){
		case "Local":
		     object.transform.rot.mult(q);
		case "Global": 
		     object.transform.rot.multquats(q, object.transform.rot);
		     // that function call (Quat.multquats) is weird: it both modifies the object, and returns `this`
		}
			
		object.transform.buildMatrix();

		#if arm_physics
		var rigidBody = object.getTrait(RigidBody);
		if (rigidBody != null) rigidBody.syncTransform();
		#end

		runOutput(0);
	}
}
