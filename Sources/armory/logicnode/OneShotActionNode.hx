package armory.logicnode;

import iron.Scene;
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
	var oneShotDone = true;
	var anim: TAnim;
	var totalFrames = 0;
	var frameTime = 1.0 / 60;
	var blendOutFrame = 0;

	public function new(tree: LogicTree) {
		super(tree);

	}

	public function init(){

		object = inputs[2].get();
		assert(Error, object != null, "The object input not be null");
		if(object.animation == null) {
			#if arm_skin
			animationBone = object.getParentArmature(object.name);
			tempMats = animationBone.initMatsEmpty();
			func = blendBones;
			#end
		}
		else{
			animationObject = cast(object.animation, ObjectAnimation);
			tempMats = animationObject.initTransformMap();
			func = blendObject;
		}
		frameTime = Scene.active.raw.frame_time;
		ready = true;
		resetAction();
	}

	public function resetAction() {
		
		if( animationObject == null){
			#if arm_skin
			animationBone.deRegisterAction(property0);
			actionParam = new Animparams(inputs[4].get(), 1.0, false);
			animationBone.registerAction(property0, actionParam);
			totalFrames = animationBone.getTotalFrames(actionParam) - 1;
			#end
		}
		else {
			animationObject.deRegisterAction(property0);
			actionParam = new Animparams(inputs[4].get(), 1.0, false);
			animationObject.registerAction(property0, actionParam);
			totalFrames = animationObject.getTotalFrames(actionParam) - 1;
		}
	}

	public function blendObject(animMats: Map<String, FastFloat>) {

		inputs[3].get()(animMats);
		animationObject.sampleAction(actionParam, tempMats);
		animationObject.blendActionObject(animMats, tempMats, animMats, factor);
	}

	#if arm_skin
	public function blendBones(animMats: Array<Mat4>) {
		var boneLayer = inputs[8].get();
		if(boneLayer < 0){
			boneLayer = null;
			if(factor < 0.05) {

				inputs[3].get()(animMats);
				return;
			}
			if(factor > 0.95) {

				animationBone.sampleAction(actionParam, animMats);
				return;
			}
		}
		inputs[3].get()(animMats);
		animationBone.sampleAction(actionParam, tempMats);
		animationBone.blendAction(animMats, tempMats, animMats, factor, boneLayer);
	
	}
	#end

	override function get(from: Int): Dynamic {
		if(!ready) init();

		return func;
		
	}

	override function run(from:Int) {
		if(!ready) init();
		var restart = inputs[5].get();
		var blendOut = inputs[7].get();
		blendOutFrame = totalFrames - Std.int(blendOut / frameTime);

		if(blendOutFrame < 1) return;

		if(from == 0) {
			if(! restart && ! oneShotDone) {
				return;
			}
			actionParam.restartAction();
			tweenIn();
		}

		if(from == 1){
			stopTween();
		}

		runOutput(0);
	}

	function tweenIn() {
		var blendIn = inputs[6].get();
		if(anim != null){
			Tween.stop(anim);
			
		}
		oneShotDone = false;
		anim = Tween.to({
			target: this,
			props: { factor: 1.0 },
			duration: blendIn,
			ease: Ease.Linear
		});
		tree.removeUpdate(tweenOut);
		tree.notifyOnUpdate(tweenOut);
	}

	function tweenOut() {
		if(actionParam.offset >= totalFrames){
			done();
			return;
		}
		var blendOut = inputs[7].get();
		if(actionParam.offset >= blendOutFrame){
			if(anim != null){
				Tween.stop(anim);
			}
			anim = Tween.to({
				target: this,
				props: { factor: 0.0 },
				duration: blendOut,
				ease: Ease.Linear,
				done: done
			});
			tree.removeUpdate(tweenOut);
		}
	}

	function stopTween() {
		tree.removeUpdate(tweenOut);
		if(anim != null){
			Tween.stop(anim);
		}
		oneShotDone = true;
		actionParam.setFrameOffset(0);
		actionParam.paused = true;
		factor = 0.0;
	}

	function done() {
		stopTween();
		runOutput(1);
	}
}
