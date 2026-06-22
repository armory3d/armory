
package armory.logicnode;

import iron.object.Object;
import iron.math.Quat;
import armory.trait.physics.RigidBody;

class SetRotationNode extends LogicNode {

	public var property0: String; // UNUSED

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		if (object == null) return;
		var _q: Quat = inputs[2].get();
		if (_q == null) return;

		final q = new Quat(_q.x, _q.y, _q.z, _q.w).normalize();
		object.transform.rot.setFrom(q);
		object.transform.buildMatrix();

		#if arm_physics
		var rigidBody = object.getTrait(RigidBody);
		if (rigidBody != null) {
			rigidBody.syncTransform();
		}
		#end
		runOutput(0);
	}
}
