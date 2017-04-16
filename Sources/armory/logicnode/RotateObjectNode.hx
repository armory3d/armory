package armory.logicnode;

import armory.object.Object;
import armory.math.Mat4;
import armory.math.Quat;
import armory.math.Vec4;
#if arm_physics
import armory.trait.internal.RigidBody;
#end

class RotateObjectNode extends LogicNode {

	var q = new Quat();

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:Object = inputs[1].get();
		var vec:Vec4 = inputs[2].get();

		if (object == null) object = tree.object;

		q.fromEuler(vec.x, vec.y, vec.z);

		object.transform.rot.mult(q);
		object.transform.buildMatrix();

		#if arm_physics
		var rigidBody = object.getTrait(RigidBody);
		if (rigidBody != null) {
			rigidBody.syncTransform();
			rigidBody.activate();
		}
		#end

		super.run();
	}
}
