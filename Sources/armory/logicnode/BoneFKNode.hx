package armory.logicnode;

import iron.object.Object;
import iron.object.BoneAnimation;
import iron.math.Mat4;

class BoneFKNode extends LogicNode {

	var notified = false;
	var m:Mat4 = null;
	var w:Mat4 = null;
	var iw = Mat4.identity();

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		#if arm_skin

		var object:Object = inputs[1].get();
		var boneName:String = inputs[2].get();
		var transform:Mat4 = inputs[3].get();
		
		if (object == null) return;
		var anim = object.animation != null ? cast(object.animation, BoneAnimation) : null;
		if (anim == null) anim = object.getParentArmature(object.name);

		// Manipulating bone in world space
		var bone = anim.getBone(boneName);
		m = anim.getBoneMat(bone);
		w = anim.getAbsMat(bone);
		
		function moveBone() {
			m.setFrom(w);
			m.multmat(transform);
			iw.getInverse(w);
			m.multmat(iw);

			// anim.removeUpdate(moveBone);
			// notified = false;
		}

		if (!notified) {
			anim.notifyOnUpdate(moveBone);
			notified = true;
		}

		runOutput(0);

		#end
	}
}
