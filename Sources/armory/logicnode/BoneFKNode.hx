package armory.logicnode;

import iron.math.Quat;
import iron.math.Vec4;
import iron.object.Object;
import iron.object.BoneAnimation;
import iron.math.Mat4;

class BoneFKNode extends LogicNode {

	#if arm_skin
	var object: Object;
	var animMats: Array<Mat4>;
	var animation: BoneAnimation;
	var ready = false;
	#end

	public function new(tree: LogicTree) {
		super(tree);
	}

	#if arm_skin
	public function init(){

		object = inputs[0].get();
		assert(Error, object != null, "The object input not be null");
		animation = object.getBoneAnimation(object.uid);
		assert(Error, animation != null, "The object does not have armatureanimation");
		ready = true;

	}

	override function get(from: Int): Dynamic {

		return function (animMats: Array<Mat4>) {

			if(! ready) init();

			inputs[1].get()(animMats);
			var boneName: String = inputs[2].get();
			var transform = Mat4.identity().setFrom(inputs[3].get());

			// Get bone in armature
			var bone = animation.getBone(boneName);

			//Set the bone local transform from world transform
			animation.setBoneMatFromWorldMat(transform, bone, animMats);
		}

	}
	#end
}
