package armory.object;

import iron.Scene;
import iron.data.SceneFormat;
import iron.App;
import iron.system.Tween;
import kha.FastFloat;
import iron.math.Mat4;
import iron.math.Vec4;
import iron.math.Vec3;
import iron.math.Vec2;
import haxe.ds.Vector;
import iron.object.Animation;
import iron.object.BoneAnimation;
import iron.object.ObjectAnimation;

class AnimationExtension {

	public static function solveIKBlend(boneAnimation: BoneAnimation, actionMats: Array<Mat4>, effector: TObj, goal: Vec4, precision = 0.01, maxIterations = 100, chainLenght = 100, pole: Vec4 = null, rollAngle = 0.0, influence = 0.0, layerMask: Null<Int> = null, threshold: FastFloat = 0.1) {
		
		var matsBlend = boneAnimation.initMatsEmpty();

		var i = 0;
		for (mat in matsBlend){
			mat.setFrom(actionMats[i]);
			i++;
		}

		boneAnimation.solveIK(effector, goal, precision, maxIterations, chainLenght, pole, rollAngle, actionMats);
		boneAnimation.blendAction(matsBlend, actionMats, actionMats, influence, layerMask, threshold);
	}

	public static function solveTwoBoneIKBlend(boneAnimation: BoneAnimation, actionMats: Array<Mat4>, effector: TObj, goal: Vec4, pole: Vec4 = null, rollAngle = 0.0, influence = 0.0, layerMask: Null<Int> = null, threshold: FastFloat = 0.1) {
		
		var matsBlend = boneAnimation.initMatsEmpty();

		var i = 0;
		for (mat in matsBlend){
			mat.setFrom(actionMats[i]);
			i++;
		}

		boneAnimation.solveTwoBoneIK(effector, goal, pole, rollAngle, actionMats);
		boneAnimation.blendAction(matsBlend, actionMats, actionMats, influence, layerMask, threshold);
	}

	public static function getBlend2DWeights(actionCoords: Array<Vec2>, sampleCoords: Vec2): Vec3 {
		var weights = new Vector<Float>(3);
		var tempWeights = new Vector<Float>(2);

		// Gradient Band Interpolation
		for (i in 0...3){

			var v1 = new Vec2().setFrom(sampleCoords).sub(actionCoords[i]);
			var k = 0;
			for (j in 0...3){
				if (i == j) continue;
				var v2 = new Vec2().setFrom(actionCoords[j]).sub(actionCoords[i]);
				var len = new Vec2().setFrom(v2).dot(v2);
				var w = 1.0 - ((new Vec2().setFrom(v1).dot(v2)) / len);

				w = w < 0 ? 0 : w > 1.0 ? 1.0 : w;
				tempWeights.set(k, w);
				k++;		
			}

			weights.set(i, Math.min(tempWeights.get(0), tempWeights.get(1)));
		}

		var res = new Vec3(weights.get(0), weights.get(1), weights.get(2));

		res.mult(1.0 / (res.x + res.y + res.z));

		return res;
	}

}

class OneShotOperator {

	var boneAnimation: BoneAnimation;
	var objectAnimation: ObjectAnimation;
	var isArmature: Bool;
	var oneShotAction: ActionSampler;
	var restart: Bool;
	var blendInTime: Float;
	var blendOutTime: Float;
	var frameTime: Float;
	var boneLayer: Null<Int>;
	var doneOneShot: Null<Void -> Void> = null;
	var tempMats: Dynamic;
	// Internal
	var isDone: Bool = true;
	var totalFrames: Int;
	var blendFactor: Float;
	var tween: TAnim = null;
	var blendOutFrame : Int;

	public function new(animation: Animation, oneShotAction: ActionSampler) {

		var animation = animation;
		this.oneShotAction = oneShotAction;
		if(Std.isOfType(animation, BoneAnimation)) {
			boneAnimation = cast animation;
			tempMats = boneAnimation.initMatsEmpty();
			this.isArmature = true;
		}
		else {
			objectAnimation = cast animation;
			tempMats = objectAnimation.initTransformMap();
			this.isArmature = false;
		}
		initOneShot();
		
	}

	function initOneShot() {
		if(isArmature) {
			totalFrames = boneAnimation.getTotalFrames(oneShotAction) - 1;
		}
		else {
			totalFrames = objectAnimation.getTotalFrames(oneShotAction) - 1;
		}
		blendFactor = 0.0;
		blendOutFrame = getBlendOutFrame(blendOutTime);
	}

	function tweenIn() {
		if(tween != null){
			Tween.stop(tween);
			
		}
		isDone = false;
		tween = Tween.to({
			target: this,
			props: { blendFactor: 1.0 },
			duration: blendInTime,
			ease: Ease.Linear
		});

		App.removeUpdate(tweenOut);
		App.notifyOnUpdate(tweenOut);
	}

	function tweenOut() {
		if(oneShotAction.offset >= totalFrames){
			done();
			return;
		}
		
		if(oneShotAction.offset >= blendOutFrame){
			if(tween != null){
				Tween.stop(tween);
			}
			tween = Tween.to({
				target: this,
				props: { blendFactor: 0.0 },
				duration: blendOutTime,
				ease: Ease.Linear,
				done: done
			});
			App.removeUpdate(tweenOut);
		}
	}

	function stopTween() {
		App.removeUpdate(tweenOut);
		if(tween != null){
			Tween.stop(tween);
		}
		isDone = true;
		oneShotAction.setFrameOffset(0);
		oneShotAction.paused = true;
		blendFactor = 0.0;
		
	}

	function done() {
		stopTween();
		if(doneOneShot != null) doneOneShot();
	}

	inline function getBlendOutFrame(blendOutTime: Float): Int {
		var frameTime = Scene.active.raw.frame_time;
		return totalFrames - Std.int(blendOutTime / frameTime);
	}

	public function update(mainMats: Dynamic) {
		#if  arm_skin
		if(isArmature){

			boneAnimation.sampleAction(oneShotAction, tempMats);
			boneAnimation.blendAction(mainMats, tempMats, mainMats, blendFactor, boneLayer);
			return;
		}
		#end
		objectAnimation.sampleAction(oneShotAction, tempMats);
		objectAnimation.blendActionObject(mainMats, tempMats, mainMats, blendFactor);

	}

	public function startOneShotAction(blendInTime: Float, blendOutTime: Float, restart: Bool = false, done: Null<Void -> Void> = null, boneLayer: Null<Int> = null) {
		if(getBlendOutFrame(blendOutTime) < 1) return;
		
		if(! restart && ! isDone) {
			return;
		}
		
		this.restart = restart;
		this.blendInTime = blendInTime;
		this.blendOutTime = blendOutTime;
		this.boneLayer = boneLayer;
		initOneShot();
		oneShotAction.restartAction();
		tweenIn();
	}

	public function stopOneShotAction() {
		stopTween();
	}
}

class SwitchActionOperator {

	var boneAnimation: BoneAnimation;
	var objectAnimation: ObjectAnimation;
	var isArmature: Bool;
	var restart: Bool;
	var blendTime: Float;
	var frameTime: Float;
	var boneLayer: Null<Int>;
	var done: Null<Void -> Void> = null;
	// Internal
	var isDone: Bool = true;
	var totalFrames: Int;
	var blendFactor: Float;
	var tween: TAnim = null;
	var blendOutFrame : Int;
	
	public function new(animation: Animation) {
		
		if(Std.isOfType(animation, BoneAnimation)) {
			boneAnimation = cast animation;
			this.isArmature = true;
		}
		else {
			objectAnimation = cast animation;
			this.isArmature = false;
		}
	}

	public function update(action1: Dynamic, action2: Dynamic, result: Dynamic) {
		#if  arm_skin
		if(isArmature){

			boneAnimation.blendAction(action1, action2, result, blendFactor, boneLayer);
			return;
		}
		#end
		objectAnimation.blendActionObject(action1, action2, result, blendFactor);

	}

	public function switchAction(toAction: SelectAction, duration: Float, restrat: Bool = false, done: Null<Void -> Void> = null, boneLayer: Null<Int> = null) {

		this.done = done;
		this.boneLayer = boneLayer;

		switch(toAction){
			case action1:
				if(tween != null){
					if(! restart && ! isDone) {
	
						return;
					}
					Tween.stop(tween);
				}
				isDone = false;
				tween = Tween.to({
					target: this,
					props: { blendFactor: 0.0 },
					duration: blendFactor * duration,
					ease: Ease.Linear,
					done: doneSwitch
				});
			
			case action2:
				if(tween != null){
					if(! restart && ! isDone) {
	
						return;
					}
					Tween.stop(tween);
				}
				isDone = false;
				tween = Tween.to({
					target: this,
					props: { blendFactor: 1.0 },
					duration: (1.0 - blendFactor) * duration,
					ease: Ease.Linear,
					done: doneSwitch
				});
		}
	}

	function doneSwitch() {
		isDone = true;
		if(done != null) done();
	}
}

@:enum abstract SelectAction(Int) from Int to Int {
	var action1 = 0;
	var action2 = 1;
}
