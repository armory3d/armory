package armory.object;

import iron.Scene;
import iron.App;
import iron.system.Tween;
import kha.FastFloat;
import iron.math.Mat4;
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
		for (mat in matsFastBlend){
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
	var _isDone: Bool = false;
	var _totalFrames: Int;
	var _blendFactor: Float;
	var _tween: TAnim = null;
	var _blendOutFrame : Int;

	public function new(animation: Animation, oneShotAction: ActionSampler) {

		this.animation = animation;
		this.oneShotAction = oneShotAction;
		if(Std.isOfType(animation, BoneAnimation)) {
			boneAnimation = cast(animation, BoneAnimation);
			tempMats = boneAnimation.initMatsEmpty();
			this.isArmature = true;
		}
		else {
			objectAnimation = cast(animation, ObjectAnimation);
			tempMats =objectAnimation.initTransformMap();
			this.isArmature = false;
		}
		initOneShot();
		
	}

	function initOneShot() {

		_totalFrames = animation.getTotalFrames(oneShotAction) - 1;
		_blendFactor = 0.0;
		var _frameTime = Scene.active.raw.frame_time;
		_blendOutFrame = _totalFrames - Std.int(blendOutTime / _frameTime);
	}

	function tweenIn() {
		
		if(_tween != null){
			Tween.stop(_tween);
			
		}
		_isDone = false;
		_tween = Tween.to({
			target: this,
			props: { _blendFactor: 1.0 },
			duration: blendInTime,
			ease: Ease.Linear
		});

		App.removeUpdate(tweenOut);
		App.notifyOnUpdate(tweenOut);
	}

	function tweenOut() {
		
		if(oneShotAction.offset >= _totalFrames){
			done();
			return;
		}
		
		if(oneShotAction.offset >= _blendOutFrame){
			if(_tween != null){
				Tween.stop(_tween);
			}
			_tween = Tween.to({
				target: this,
				props: { _blendfactor: 0.0 },
				duration: blendOutTime,
				ease: Ease.Linear,
				done: done
			});
			App.removeUpdate(tweenOut);
		}
	}

	function stopTween() {
		App.removeUpdate(tweenOut);
		if(_tween != null){
			Tween.stop(_tween);
		}
		_isDone = true;
		oneShotAction.setFrameOffset(0);
		oneShotAction.paused = true;
		_blendFactor = 0.0;
		
	}

	function done() {
		stopTween();
		if(doneOneShot != null) doneOneShot();
	}

	public function update(mainMats: Dynamic) {
		#if  arm_skin
		if(isArmature){

			boneAnimation.sampleAction(oneShotAction, tempMats);
			boneAnimation.blendAction(mainMats, tempMats, mainMats, _blendFactor, boneLayer);
			return;
		}
		#end
		objectAnimation.sampleAction(oneShotAction, tempMats);
		objectAnimation.blendActionObject(mainMats, tempMats, mainMats, _blendFactor);

	}

	public function startOneShotAction(blendInTime: Float, blendOutTime: Float, restart: Bool, boneLayer: Null<Int>, done: Null<Void -> Void>) {
		
		this.restart = restart;
		this.blendInTime = blendInTime;
		this.blendOutTime = blendOutTime;
		this.boneLayer = boneLayer;

		initOneShot();
		if(_blendOutFrame < 1) return;
		
		if(! restart && ! _isDone) {
			return;
		}
		oneShotAction.restartAction();
		tweenIn();
	}

	public function stopOneShotAction() {
		stopTween();
	}
}
