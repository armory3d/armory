package armory.logicnode;

import iron.object.Object;
import iron.object.BoneAnimation;
import iron.math.Vec4;

class BoneIKNode extends LogicNode {

	var goal:Vec4;
	var notified = false;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:Object = inputs[1].get();
		var boneName:String = inputs[2].get();
		goal = inputs[3].get();
		
		if (object == null || goal == null) return;
		var anim = object.animation != null ? cast(object.animation, BoneAnimation) : null;
		if (anim == null) anim = object.getParentArmature(object.name);

		var bone = anim.getBone(boneName);
		
		function solveBone() {
			anim.solveIK(bone, goal);

			// anim.removeUpdate(solveBone);
			// notified = false;
		}

		if (!notified) {
			anim.notifyOnUpdate(solveBone);
			notified = true;
		}

		runOutputs(0);
	}
}
