package armory.logicnode;

import iron.object.Object;
import iron.math.Vec4;
import armory.trait.physics.RigidBody;

using armory.object.TransformExtension;

class ApplyForceNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var force: Vec4 = inputs[2].get();
		var local: Bool = inputs.length > 3 ? inputs[3].get() : false;

		if (object == null || force == null) return;

#if arm_physics
		var rb: RigidBody = object.getTrait(RigidBody);

		!local ? rb.applyForce(force) : rb.applyForce(object.transform.worldVecToOrientation(force));
#end

		runOutput(0);
	}

}
