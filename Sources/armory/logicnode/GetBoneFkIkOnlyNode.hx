package armory.logicnode;

import iron.object.Object;
import iron.object.BoneAnimation;

class GetBoneFkIkOnlyNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Bool {
		#if arm_skin

		var object: Object = inputs[0].get();
		var boneName: String = inputs[1].get();

		if (object == null) return null;
		var anim = object.animation != null ? cast(object.animation, BoneAnimation) : null;
		if (anim == null) anim = object.getParentArmature(object.name);

		// Get bone in armature
		var bone = anim.getBone(boneName);

        //Get bone transform in world coordinates
        return bone.is_ik_fk_only;
 
        #else
        return null;

		#end
	}
}
