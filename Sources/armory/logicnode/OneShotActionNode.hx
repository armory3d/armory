package armory.logicnode;

import iron.system.Tween;
import kha.FastFloat;
import iron.object.ObjectAnimation;
import iron.object.Animation;
#if arm_skin
import iron.object.BoneAnimation;
#end
import iron.math.Mat4;
import iron.object.Object;

class OneShotActionNode extends LogicNode {

	public var property0: String;
	public var actionParam: Animparams;
	var object: Object;
	#if arm_skin
	var animationBone: BoneAnimation;
	#end
	var animationObject: ObjectAnimation;
	var tempMats: Dynamic;
	var ready = false;
	var func: Dynamic = null;
	var factor = 0.0;
	var tweenDone = true;
	var anim: TAnim;
	var totalFrames = 0;

	public function new(tree: LogicTree) {
		super(tree);

		tree.notifyOnUpdate(tweenOut);

	}

	public function init(){
		actionParam = new Animparams(inputs[1].get(), 1.0, inputs[2].get());
		actionParam.paused = true;
		object = inputs[0].get();
		assert(Error, object != null, "The object input not be null");
		if(object.animation == null) {
			#if arm_skin
			animationBone = object.getParentArmature(object.name);
			animationBone.registerAction(property0, actionParam);
			tempMats = animationBone.initMatsEmpty();
			func = blendBones;
			#end
		}
		else{
			animationObject = cast(object.animation, ObjectAnimation);
			animationObject.registerAction(property0, actionParam);
			func = blendObject;
		}
		ready = true;
	}

	public function registerAction() {
		
		if(!ready) init();

		if( animationObject == null){
			animationBone.deRegisterAction(property0);
			actionParam = new Animparams(inputs[1].get(), 1.0, inputs[2].get());
			actionParam.paused = true;
			animationBone.registerAction(property0, actionParam);
			totalFrames = animationBone.totalFrames(actionParam);
		}
		else {
			animationObject.deRegisterAction(property0);
			actionParam = new Animparams(inputs[1].get(), 1.0, inputs[2].get());
			actionParam.paused = true;
			animationObject.registerAction(property0, actionParam);
			totalFrames = animationObject.totalFrames(actionParam);
		}
	}

	public function blendObject(animMats: Map<String, FastFloat>) {
		inputs[3].get()(animMats);
		animationObject.sampleAction(actionParam, tempMats)
		animationObject.blendActionObject(animMats, tempMats, animMats, factor);

	}

	#if arm_skin
	public function blendBones(animMats: Array<Mat4>) {
		var boneLayer = inputs[7].get();
		if(boneLayer < 0){
			boneLayer = null;
			if(factor < 0.05) {

				inputs[3].get()(animMats);
				return;
			}
			if(factor > 0.95) {

				animationBone.sampleAction(actionParam, tempMats)
				return;
			}
		}
		
		inputs[3].get()(animMats);
		animationBone.sampleAction(actionParam, tempMats)
		animationBone.blendAction(animMats, tempMats, animMats, factor, boneLayer);
	
	}
	#end

	override function get(from: Int): Dynamic {
		if(!ready) init();

		return func;
		
	}

	override function run(from:Int) {

		registerAction();

		var restart = inputs[5].get();
		var blendIn = inputs[6].get();
		var blendOut = inputs[7].get();

		if(from == 0) {

			if(anim != null){
				if(! restart && ! tweenDone) {

					return;
				}
				Tween.stop(anim);
			}
			tweenDone = false;
			anim = Tween.to({
				target: this,
				props: { factor: 1.0 },
				duration: blendIn,
				ease: Ease.Linear,
				done: done
			});
		}

		if(from == 1){

			if(anim != null){
				Tween.stop(anim);
			}
			factor = 0.0;
		}
	}

	public function tweenOut() {
		
	}

	function done() {
		tweenDone = true;
		runOutput(0);
	}
}
