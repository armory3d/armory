package armory.logicnode;

import iron.object.Object;
import iron.math.Mat4;
import iron.math.Quat;
import iron.math.Vec4;
import armory.trait.physics.RigidBody;

class RotateObjectNode extends LogicNode {

	var q = new Quat();

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		var object:Object = inputs[1].get();
		var vec:Vec4 = inputs[2].get();

		if (object == null || vec == null) return;

		q.fromEuler(vec.x, vec.y, vec.z);

		object.transform.rot.mult(q);
		object.transform.buildMatrix();

		#if arm_physics
		var rigidBody = object.getTrait(RigidBody);
		if (rigidBody != null) rigidBody.syncTransform();
		#end

		runOutput(0);
	}
}
