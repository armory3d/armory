package armory.logicnode;

import iron.system.Tween;
import kha.FastFloat;
import iron.object.ObjectAnimation;
import iron.object.Animation;
#if arm_skin
import iron.object.BoneAnimation;
#end
import armory.object.AnimationExtension;
import iron.math.Mat4;
import iron.object.Object;

class SwitchActionMultiNode extends LogicNode {

	static final MIN_INDEX: Int = 6;

	var object: Object;
	#if arm_skin
	var animationBone: BoneAnimation;
	#end
	var animationObject: ObjectAnimation;
	var switchActionOp: SwitchActionOperator;
	var tempMatsObject: Map<String, FastFloat>;
	var tempMatsBone: Array<Mat4>;
	var animMatsObject: Map<String, FastFloat>;
	var animMatsBone: Array<Mat4>;
	var ready = false;
	var result: Dynamic = null;
	var forward = true;
	var switchFrom: Int = 1;
	var switchTo: Int = 2;
	var fromId = 0;
	var toId = 0;

	public function new(tree: LogicTree) {
		super(tree);

	}

	public function init() {
		object = inputs[2].get();
		assert(Error, object != null, "The object input not be null");
		fromId = MIN_INDEX;
		toId = MIN_INDEX + 1;
		if(object.animation == null) {
			#if arm_skin
			animationBone = object.getBoneAnimation(object.uid);
			tempMatsBone = animationBone.initMatsEmpty();
			animMatsBone = animationBone.initMatsEmpty();
			result = resultBone;
			#end
		}
		else {
			animationObject = cast(object.animation, ObjectAnimation);
			tempMatsObject = animationObject.initTransformMap();
			animMatsObject = animationObject.initTransformMap();
			result = resultObject;
		}
		ready = true;
		initSwitchAction();
	}

	public function initSwitchAction(){
		if( animationObject == null){
			#if arm_skin
			switchActionOp = new SwitchActionOperator(animationBone);
			#end
		}
		else {
			switchActionOp = new SwitchActionOperator(animationObject);
		}
	}

	public function resultBone(resultMats: Array<Mat4>){

		inputs[fromId].get()(animMatsBone);
		inputs[toId].get()(tempMatsBone);
		switchActionOp.update(animMatsBone, tempMatsBone, resultMats);
	}

	public function resultObject(resultMats: Map<String, FastFloat>){

		inputs[fromId].get()(animMatsObject);
		inputs[toId].get()(tempMatsObject);
		switchActionOp.update(animMatsObject, tempMatsObject, resultMats);
	}

	override function get(from: Int): Dynamic {
		if(!ready) init();

		return result;
		
	}

	override function run(from:Int) {
		switchTo = inputs[1].get();
		var restart = inputs[3].get();
		var duration: FastFloat = inputs[4].get();
		var boneLayer: Null<Int> = inputs[5].get();

		if(!forward) {
			forward = !forward;
			fromId = MIN_INDEX + switchTo;
			switchActionOp.switchAction(action1, duration, restart, done, boneLayer);
		}
		else {
			forward = !forward;
			toId = MIN_INDEX + switchTo;
			switchActionOp.switchAction(action2, duration, restart, done, boneLayer);
		}
	}

	function done() {
		runOutput(0);
	}
}
