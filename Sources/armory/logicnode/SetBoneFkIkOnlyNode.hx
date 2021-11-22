package armory.logicnode;

import iron.math.Quat;
import iron.math.Vec4;
import iron.object.Object;
#if arm_skin
import iron.object.BoneAnimation;
#end

class SetBoneFkIkOnlyNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		#if arm_skin

		var object: Object = inputs[1].get();
		var boneName: String = inputs[2].get();
		var fk_ik_only: Bool = inputs[3].get();

		if (object == null) return;
		var anim = object.animation != null ? cast(object.animation, BoneAnimation) : null;
		if (anim == null) anim = object.getParentArmature(object.name);

		// Get bone in armature
		var bone = anim.getBone(boneName);

        //Set bone animated by FK or IK only
        bone.is_ik_fk_only = fk_ik_only;

		runOutput(0);

		#end
	}
}
