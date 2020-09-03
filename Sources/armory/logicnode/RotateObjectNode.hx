package armory.logicnode;

import iron.object.Object;
import iron.math.Quat;
import iron.math.Vec4;
import armory.trait.physics.RigidBody;

class RotateObjectNode extends LogicNode {

	public var property0 = "Euler Angles";
	var q = new Quat();

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var vec: Vec4 = inputs[2].get();
		
		// note: here, the next line is disabled because old versions of the node don't have a third input.
		// when those old versions will be considered remove, feel free to uncomment that, and replace the other `inputs[3].get()` by `w` in this file.
		//var w: Float = inputs[3].get();

		if (object == null || vec == null) return;

		switch (property0) {
			case "Euler Angles":
				q.fromEuler(vec.x, vec.y, vec.z);
			case "Angle Axies (Degrees)" | "Angle Axies (Radians)":
				var angle: Float = inputs[3].get();
				if (property0 == "Angle Axies (Degrees)") {
					angle = angle * (Math.PI / 180);
				}
				var angleSin = Math.sin(angle / 2);
				vec = vec.normalize();
				var angleCos = Math.cos(angle / 2);
				q = new Quat(vec.x * angleSin, vec.y * angleSin, vec.z * angleSin, angleCos);
			case "Quaternion":
				q = new Quat(vec.x, vec.y, vec.z, inputs[3].get());
				q.normalize();
		}

		object.transform.rot.mult(q);
		object.transform.buildMatrix();

		#if arm_physics
		var rigidBody = object.getTrait(RigidBody);
		if (rigidBody != null) rigidBody.syncTransform();
		#end

		runOutput(0);
	}
}
