package armory.logicnode;

import kha.FastFloat;
import iron.object.ObjectAnimation;
import iron.object.Object;
import iron.object.Animation;
#if arm_skin
import iron.object.BoneAnimation;
#end
import iron.math.Mat4;


class AnimActionNode extends LogicNode {

	public var property0: String;
	public var actionParam: Animparams;
	var object: Object;
	#if arm_skin
	var animationBone: BoneAnimation;
	#end
	var animationObject: ObjectAnimation;
	var ready = false;
	var func:Dynamic = null;

	public function new(tree: LogicTree) {
		super(tree);

	}

	function init(){
		actionParam = new Animparams(inputs[1].get(), 1.0, inputs[2].get());
		object = inputs[0].get();
		assert(Error, object != null, "The object input not be null");
		if(object.animation == null) {
			#if arm_skin
			animationBone = object.getParentArmature(object.name);
			animationBone.registerAction(property0, actionParam);
			func = sampleBonaAction;
			#end
		}
		else{
			animationObject = cast(object.animation, ObjectAnimation);
			animationObject.registerAction(property0, actionParam);
			func = sampleObjectAction;
		}
		
		ready = true;
	}

	#if arm_skin
	public function sampleBonaAction(animMats: Array<Mat4>){
		animationBone.sampleAction(actionParam, animMats);
	}
	#end

	public function sampleObjectAction(animMats: Map<String, FastFloat>) {
		animationObject.sampleAction(actionParam, animMats);
	}

	override function get(from: Int): Dynamic {

		if(!ready) init();

		return func;
	}

}
