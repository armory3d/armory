package armory.logicnode;

import iron.object.Object;
import iron.math.Vec4;
import armory.trait.physics.RigidBody;

class RotateObjectAroundAxisNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var axis: Vec4 = inputs[2].get();
		var angle: Float = inputs[3].get();

		if (object == null || axis == null) return;

		// the rotate function already calls buildMatrix
		object.transform.rotate(axis.normalize(), angle);

		#if arm_physics
		var rigidBody = object.getTrait(RigidBody);
		if (rigidBody != null) rigidBody.syncTransform();
		#end

		runOutput(0);
	}
}
