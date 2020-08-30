package armory.logicnode;

import iron.object.Object;
import iron.math.Quat;
import iron.math.Vec4;
import armory.trait.physics.RigidBody;

class SetRotationNode extends LogicNode {

	public var property0: String;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		if (object == null) return;
		var vec: Vec4 = inputs[2].get();
		if (vec == null) return;
		var w: Float = inputs[3].get();

		switch (property0) {
			case "Euler Angles":
				object.transform.rot.fromEuler(vec.x, vec.y, vec.z);
			case "Angle Axies (Degrees)" | "Angle Axies (Radians)":
				var angle: Float = w;
				if (property0 == "Angle Axies (Degrees)") {
					angle = angle * (Math.PI / 180);
				}
				var angleSin = Math.sin(angle / 2);
				vec = vec.normalize();
				var angleCos = Math.cos(angle / 2);
				object.transform.rot = new Quat(vec.x * angleSin, vec.y * angleSin, vec.z * angleSin, angleCos);
			case "Quaternion":
				object.transform.rot = new Quat(vec.x, vec.y, vec.z, w);
				object.transform.rot.normalize();
		}
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
