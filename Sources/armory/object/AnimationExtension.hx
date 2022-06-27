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
import iron.object.Object;
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

	static inline function sortWeights(vecs: Array<Vec2>, sampleVec: Vec2): Map<Int, Vec2> {
		var weightIndex: Array<WeightIndex> = [];
		var i = 0;
		for (vec in vecs){
			weightIndex.push({weight: Vec2.distance(vec, sampleVec), index: i} );
			i++;
		}

		weightIndex.sort(sortCompare);

		var weightsSorted = new Map<Int, Vec2>();
		for (i in 0...3) {
			var index = weightIndex[i].index;
			weightsSorted.set(index, vecs[index]);
		}

		return weightsSorted;
	}

	static inline function sortCompare(a: WeightIndex, b: WeightIndex): Int {
		return Reflect.compare(a.weight, b.weight);
	}

	public static function getBlend2DWeights(actionCoords: Array<Vec2>, sampleCoords: Vec2): Map<Int, Float> {
		
		var weightsMap = sortWeights(actionCoords, sampleCoords);
		
		var weights = new Vector<Float>(3);
		var tempWeights = new Vector<Float>(2);

		// Gradient Band Interpolation
		var keys1 = weightsMap.keys();
		var i = 0;
		for (key1 in keys1){
			var v1 = new Vec2().setFrom(sampleCoords).sub(weightsMap[key1]);
			var k = 0;
			var keys2 = weightsMap.keys();
			for (key2 in keys2){
				if (key1 == key2) continue;
				var v2 = new Vec2().setFrom(weightsMap[key2]).sub(weightsMap[key1]);
				var len = new Vec2().setFrom(v2).dot(v2);
				var w = 1.0 - ((new Vec2().setFrom(v1).dot(v2)) / len);

				w = w < 0 ? 0 : w > 1.0 ? 1.0 : w;
				tempWeights.set(k, w);
				k++;
			}
			weights.set(i, Math.min(tempWeights.get(0), tempWeights.get(1)));
			i++;
		}

		var res = new Vec3(weights.get(0), weights.get(1), weights.get(2));
		res.mult(1.0 / (res.x + res.y + res.z));
		
		var resultMap = new Map<Int, Float>();
		var keys = weightsMap.keys();
		resultMap.set(keys.next(), res.x );
		resultMap.set(keys.next(), res.y );
		resultMap.set(keys.next(), res.z );

		return resultMap;
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
	var tempMatsBone: Array<Mat4>;
	var tempMatsObject: Map<String, FastFloat>;
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
			tempMatsBone = boneAnimation.initMatsEmpty();
			this.isArmature = true;
		}
		else {
			objectAnimation = cast animation;
			tempMatsObject = objectAnimation.initTransformMap();
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

	public overload extern inline function update(mainMats: Array<Mat4>, resultMats: Array<Mat4>) {
	#if arm_skin
		boneAnimation.sampleAction(oneShotAction, tempMatsBone);
		boneAnimation.blendAction(mainMats, tempMatsBone, resultMats, blendFactor, boneLayer);
	#end
	}

	public overload extern inline function update(mainMats: Map<String, FastFloat>, resultMats: Map<String, FastFloat>) {

		objectAnimation.sampleAction(oneShotAction, tempMatsObject);
		objectAnimation.blendActionObject(mainMats, tempMatsObject, resultMats, blendFactor);
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
		this.doneOneShot = done;
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
	var blendFactor: Float = 0;
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

	public overload extern inline function update(action1: Array<Mat4>, action2: Array<Mat4>, resultMats: Array<Mat4>) {
		#if arm_skin
		boneAnimation.blendAction(action1, action2, resultMats, blendFactor, boneLayer);
		#end
	}
	
	public overload extern inline function update(action1: Map<String, FastFloat>, action2: Map<String, FastFloat>, resultMats: Map<String, FastFloat>) {
	
		objectAnimation.blendActionObject(action1, action2, resultMats, blendFactor);
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

class simpleBiPedalIK {

	var armatureObject: Object;
	var boneAnimation: BoneAnimation;
	var animMats: Array<Mat4>; //1
	var leftBone: TObj; //2
	var rightBone: TObj; //3
	var leftHitPoint: Null<Float>; //4
	var rightHitPoint: Null<Float>; //5
	var hipHeight: Float; //6
	var footOffset: Null<Float>; //7
	var footOffsetThreshold: Float; //8
	var interpSpeed: Float; //9
	var layerMask: Null<Int>; //10
	var leftPole: Vec4 = null; 
	var rightPole: Vec4 = null;
	var oldInfluence: Null<Float> = null;
	var influenceMatch: Bool = false;

	public function new(armatureObject: Object, boneAnimation: BoneAnimation, leftBoneName: Sting, rightBoneName: String) {
		this.armatureObject = armatureObject;
		this.boneAnimation = boneAnimation;
		this.leftBone = boneAnimation.getBone(leftBoneName);
		this.rightBone = boneAnimation.getBone(rightBoneName);
		
	}

	inline function deltaInterpolate(from: Float, to: Float, interpSpeed: Float): Float {

		var sign = to > from ? 1.0 : -1.0;
		var value = from + interpSpeed * sign;
		var min = Math.min(to, from);
		var max = Math.max(to, from);
		return value < min ? min : value > max ? max : value;
	}

	inline function setWorldLocation(currentPos: Vec4) {
		var loc = new Vec4().setFrom(currentPos);
		// Remove parent location influence
		loc.sub(object.parent.transform.world.getLoc());
		// Convert vec to parent local space
		var dotX = loc.dot(object.parent.transform.right());
		var dotY = loc.dot(object.parent.transform.look());
		var dotZ = loc.dot(object.parent.transform.up());
		var vec = new Vec4(dotX, dotY, dotZ);
		object.transform.loc.setFrom(vec);
		object.transform.buildMatrix();
	}

}

@:enum abstract SelectAction(Int) from Int to Int {
	var action1 = 0;
	var action2 = 1;
}

typedef WeightIndex = {
	var weight: FastFloat;
	var index: Int;
}
