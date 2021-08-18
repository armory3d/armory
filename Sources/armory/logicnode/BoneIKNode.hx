package armory.logicnode;

import iron.object.Object;
import iron.object.BoneAnimation;
import iron.math.Vec4;

class BoneIKNode extends LogicNode {

	var goal: Vec4;
	var pole: Vec4;
	var poleEnabled: Bool;
	var chainLength: Int;
	var maxIterartions: Int;
	var precision: Float;
	var rollAngle: Float;

	var notified = false;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		#if arm_skin

		var object: Object = inputs[1].get();
		var boneName: String = inputs[2].get();
		goal = inputs[3].get();
		poleEnabled = inputs[4].get();
		pole = inputs[5].get();
		chainLength = inputs[6].get();
		maxIterartions = inputs[7].get();
		precision = inputs[8].get();
		rollAngle = inputs[9].get();

		if (object == null || goal == null) return;
		var anim = object.animation != null ? cast(object.animation, BoneAnimation) : null;
		if (anim == null) anim = object.getParentArmature(object.name);

		var bone = anim.getBone(boneName);

		if(! poleEnabled) pole = null;

		function solveBone() {
			//Solve IK
			anim.solveIK(bone, goal, precision, maxIterartions, chainLength, pole, rollAngle);

			//Remove this method from animation loop after IK
			anim.removeUpdate(solveBone);
			notified = false;
		}

		if (!notified) {
			anim.notifyOnUpdate(solveBone);
			notified = true;
		}

		runOutput(0);

		#end
	}
}
