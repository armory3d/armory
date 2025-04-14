package armory.logicnode;

import iron.object.Object;
import iron.object.BoneAnimation;
import iron.math.Mat4;

class GetBoneTransformNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Mat4 {
		#if arm_skin

		var object: Object = inputs[0].get();
		var boneName: String = inputs[1].get();

		if (object == null) return null;
		var anim = object.animation != null ? cast(object.animation, BoneAnimation) : null;
		if (anim == null) anim = object.getParentArmature(object.name);

		// Get bone in armature
		var bone = anim.getBone(boneName);

		//return anim.getAbsWorldMat(bone);
		return anim.getAbsMat(bone).clone().multmat(object.transform.world);
		
        #else
        return null;

		#end
	}
}
