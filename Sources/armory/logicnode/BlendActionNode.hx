package armory.logicnode;

import kha.FastFloat;
import iron.object.ObjectAnimation;
import iron.object.Animation;
#if arm_skin
import iron.object.BoneAnimation;
#end
import iron.math.Mat4;
import iron.object.Object;

class BlendActionNode extends LogicNode {

	var object: Object;
	#if arm_skin
	var animationBone: BoneAnimation;
	#end
	var animationObject: ObjectAnimation;
	var tempMats: Dynamic;
	var ready = false;
	var func: Dynamic = null;

	public function new(tree: LogicTree) {
		super(tree);
	}

	public function init(){
		object = inputs[0].get();
		assert(Error, object != null, "The object input not be null");
		if(object.animation == null) {
			#if arm_skin
			animationBone = object.getParentArmature(object.name);
			tempMats = animationBone.initMatsEmpty();
			func = blendBones;
			#end
		}
		else {
			animationObject = cast(object.animation, ObjectAnimation);
			tempMats = animationObject.initTransformMap();
			func = blendObject;
		}
		ready = true;
	}

	public function blendObject(animMats: Map<String, FastFloat>) {
		inputs[1].get()(animMats);
		inputs[2].get()(tempMats);
		animationObject.blendActionObject(animMats, tempMats, animMats, inputs[3].get());

	}

	#if arm_skin
	public function blendBones(animMats: Array<Mat4>) {
		var boneLayer = inputs[4].get();
		var factor = inputs[3].get();
		if(boneLayer < 0){
			boneLayer = null;
			if(factor < 0.05) {

				inputs[1].get()(animMats);
				return;
			}
			if(factor > 0.95) {

				inputs[2].get()(animMats);
				return;
			}
		}
		
		inputs[1].get()(animMats);
		inputs[2].get()(tempMats);
		animationBone.blendAction(animMats, tempMats, animMats, factor, boneLayer);
	
	}
	#end

	override function get(from: Int): Dynamic {
		if(!ready) init();

		return func;
		
	}
}
