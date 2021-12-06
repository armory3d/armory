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

class SwitchActionNode extends LogicNode {

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
		else {
			animationObject = cast(object.animation, ObjectAnimation);
			tempMats = animationObject.initTransformMap();
			func = blendObject;
		}
		ready = true;
	}

	public function blendObject(animMats: Map<String, FastFloat>) {
		inputs[3].get()(animMats);
		inputs[4].get()(tempMats);
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

				inputs[4].get()(animMats);
				return;
			}
		}
		
		inputs[3].get()(animMats);
		inputs[4].get()(tempMats);
		animationBone.blendAction(animMats, tempMats, animMats, factor, boneLayer);
	
	}
	#end

	override function get(from: Int): Dynamic {
		if(!ready) init();

		return func;
		
	}

	override function run(from:Int) {
		var restart = inputs[5].get();
		var duration = inputs[6].get();

		if(from == 0){

			if(anim != null){
				if(! restart && ! tweenDone) {

					return;
				}
				Tween.stop(anim);
			}
			tweenDone = false;
			anim = Tween.to({
				target: this,
				props: { factor: 0.0 },
				duration: factor * duration,
				ease: Ease.Linear,
				done: done
			});
		}
		if(from == 1){
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
				duration: (1.0 - factor) * duration,
				ease: Ease.Linear,
				done: done
			});
		}
	}

	function done() {
		tweenDone = true;
		runOutput(0);
	}
}
