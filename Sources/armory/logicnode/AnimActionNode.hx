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
	public var sampler: ActionSampler;
	var object: Object;
	#if arm_skin
	var animationBone: BoneAnimation;
	#end
	var animationObject: ObjectAnimation;
	var ready = false;
	var func:Dynamic = null;

	public function new(tree: LogicTree) {
		super(tree);

		tree.notifyOnUpdate(init);
	}

	function init(){
		sampler = new ActionSampler(inputs[1].get(), 1.0, inputs[2].get());
		object = inputs[0].get();
		assert(Error, object != null, "The object input not be null");
		if(object.animation == null) {
			#if arm_skin
			animationBone = object.getParentArmature(object.name);
			animationBone.registerAction(property0, sampler);
			func = sampleBonaAction;
			#end
		}
		else{
			animationObject = cast(object.animation, ObjectAnimation);
			animationObject.registerAction(property0, sampler);
			func = sampleObjectAction;
		}
		
		ready = true;
		tree.removeUpdate(init);
	}

	#if arm_skin
	public function sampleBonaAction(animMats: Array<Mat4>){
		animationBone.sampleAction(sampler, animMats);
	}
	#end

	public function sampleObjectAction(animMats: Map<String, FastFloat>) {
		animationObject.sampleAction(sampler, animMats);
	}

	override function get(from: Int): Dynamic {

		if(!ready) init();

		return func;
	}

}
