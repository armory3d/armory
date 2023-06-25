package armory.logicnode;

import iron.math.Quat;
import iron.math.Vec4;
import iron.object.Object;
import iron.object.BoneAnimation;
import iron.math.Mat4;

class BoneFKNode extends LogicNode {

	var notified = false;
	var m: Mat4 = null;
	var w: Mat4 = null;
	var iw = Mat4.identity();

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		#if arm_skin

		var object: Object = inputs[1].get();
		var boneName: String = inputs[2].get();
		var transform: Mat4 = inputs[3].get();

		if (object == null) return;
		var anim = object.animation != null ? cast(object.animation, BoneAnimation) : null;
		if (anim == null) anim = object.getParentArmature(object.name);

		// Get bone in armature
		var bone = anim.getBone(boneName);

		function moveBone() {
			
			var t2 = Mat4.identity();
			var loc= new Vec4();
			var rot = new Quat();
			var scl = new Vec4();

			//Set scale to Armature scale. Bone scaling not yet implemented
			t2.setFrom(transform);
			t2.decompose(loc, rot, scl);
			scl = object.transform.world.getScale();
			t2.compose(loc, rot, scl);

			//Set the bone local transform from world transform
			anim.setBoneMatFromWorldMat(t2, bone);

			//Remove this method from animation loop after FK
			anim.removeUpdate(moveBone);
			notified = false;
		}

		if (!notified) {
			anim.notifyOnUpdate(moveBone);
			notified = true;
		}

		runOutput(0);

		#end
	}
}
