package armory.logicnode;

import iron.Scene;
import iron.system.Tween;
import kha.FastFloat;
import iron.object.ObjectAnimation;
import iron.object.Animation;
import armory.object.AnimationExtension;
#if arm_skin
import iron.object.BoneAnimation;
#end
import iron.math.Mat4;
import iron.object.Object;

class OneShotActionNode extends LogicNode {

	public var property0: String;
	public var sampler: ActionSampler;
	var object: Object;
	#if arm_skin
	var animationBone: BoneAnimation;
	#end
	var animationObject: ObjectAnimation;
	var tempMatsObject: Map<String, FastFloat>;
	var tempMatsBone: Array<Mat4>;
	var ready = false;
	var result: Dynamic;

	var oneShotOp: OneShotOperator;

	public function new(tree: LogicTree) {
		super(tree);

	}

	public function init(){

		object = inputs[2].get();
		assert(Error, object != null, "The object input not be null");
		if(object.animation == null) {
			#if arm_skin
			animationBone = object.getBoneAnimation(object.uid);
			tempMatsBone = animationBone.initMatsEmpty();
			#end
		}
		else{
			animationObject = cast(object.animation, ObjectAnimation);
			tempMatsObject = animationObject.initTransformMap();
		}
		ready = true;
		initOneShot();
	}

	public function initOneShot() {
		
		if(animationObject == null){
			#if arm_skin
			animationBone.deRegisterAction(property0);
			sampler = new ActionSampler(inputs[4].get(), 1.0, false, true);
			animationBone.registerAction(property0, sampler);
			oneShotOp = new OneShotOperator(animationBone, sampler);
			result = resultBone;
			#end
		}
		else {
			animationObject.deRegisterAction(property0);
			sampler = new ActionSampler(inputs[4].get(), 1.0, false, true);
			animationObject.registerAction(property0, sampler);
			oneShotOp = new OneShotOperator(animationObject, sampler);
			result = resultObject;
		}
	}

	public function resultBone(resultMats: Array<Mat4>) {

		inputs[3].get()(tempMatsBone);
		oneShotOp.update(tempMatsBone, resultMats);
	}

	public function resultObject(resultMats: Map<String, FastFloat>) {

		inputs[3].get()(tempMatsObject);
		oneShotOp.update(tempMatsObject, resultMats);
	}

	override function get(from: Int): Dynamic {
		if(!ready) init();
		return result;
	}

	override function run(from:Int) {
		if(ready) {
			initOneShot();
		}
		else {
			init();
		}
		var restart = inputs[5].get();
		var blendOut = inputs[7].get();
		var blendIn = inputs[6].get();
		var boneLayer: Null<Int> = inputs[8].get();

		if(from == 0) {
			oneShotOp.startOneShotAction(blendIn, blendOut, restart, done, boneLayer);
		}

		if(from == 1){
			oneShotOp.stopOneShotAction();
		}

		runOutput(0);
	}

	function done() {
		runOutput(1);
	}
}
