package armory.logicnode;

import iron.object.Object;
import iron.math.Quat;
import iron.math.Vec3;
import armory.trait.physics.RigidBody;

class SetRotationNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		var object:Object = inputs[1].get();
		var angle:Float = inputs[2].get() * (Math.PI / 180);
		var vec: Vec3 = inputs[3].get();
		var angleSin = Math.sin(angle / 2);
		vec = vec.normalize();
		vec = new Vec3(vec.x * angleSin, vec.y * angleSin, vec.z * angleSin);
		var angleCos = Math.cos(angle / 2);

		if (object == null || vec == null) return;

		object.transform.rot = new Quat(vec.x, vec.y, vec.z, angleCos);
		object.transform.buildMatrix();

		#if arm_physics
		var rigidBody = object.getTrait(RigidBody);
		if (rigidBody != null) rigidBody.syncTransform();
		#end

		runOutput(0);
	}
}
