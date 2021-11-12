package armory.logicnode;

import kha.FastFloat;
import iron.object.ObjectAnimation;
import iron.object.Animation;
import iron.object.BoneAnimation;
import iron.math.Mat4;
import iron.object.Object;

class BlendActionNode extends LogicNode {

	var object: Object;
	var animation: Animation;
	var tempMats: Dynamic;
	var isArmature: Bool;
	var ready = false;

	public function new(tree: LogicTree) {
		super(tree);
	}

	public function init(){
		object = inputs[0].get();
		assert(Error, object != null, "The object input not be null");
		animation = object.animation;
		if(animation == null) {
			animation = object.getParentArmature(object.name);
			tempMats = cast(animation, BoneAnimation).initMatsEmpty();
			isArmature = true;
		}
		else {
			tempMats = cast(animation, ObjectAnimation).initTransformMap();
			isArmature = false;
		}
		ready = true;
	}

	override function get(from: Int): Dynamic {

		if(!ready) init();

		if(isArmature){
			return function (animMats: Array<Mat4>){ 
				inputs[1].get()(animMats);
				inputs[2].get()(tempMats);
				cast(animation, BoneAnimation).blendAction(animMats, tempMats, animMats, inputs[3].get(), inputs[4].get());
			};
		}
		else {
			return function (animMats: Map<String, FastFloat>){ 
				inputs[1].get()(animMats);
				inputs[2].get()(tempMats);
				cast(animation, ObjectAnimation).blendActionObject(animMats, tempMats, animMats, inputs[3].get());
			};
		}
		return null;
		
	}
}
