package armory.logicnode;

import armory.object.AnimationExtension;
import iron.object.Object;
import iron.object.BoneAnimation;
import iron.math.Vec4;
import iron.math.Mat4;

class BoneIKNode extends LogicNode {

	public var property0: String; //2 Bone or FABRIK
	#if arm_skin
	var object: Object;
	var boneName: String;
	var animMats: Array<Mat4>;
	var goal: Vec4;
	var pole: Vec4;
	var poleEnabled: Bool;
	var rollAngle: Float;
	var influence: Float;
	var layerMask: Null<Int>;
	var chainLength: Int;
	var maxIterartions: Int;
	var precision: Float;
	var animation: BoneAnimation;
	var ready = false;
	#end
	
	public function new(tree: LogicTree) {
		super(tree);
	}

	#if arm_skin

	public function init(){

		object = inputs[0].get();
		assert(Error, object != null, "The object input not be null");
		animation = object.getBoneAnimation(object.uid);
		assert(Error, animation != null, "The object does not have armatureanimation");
		ready = true;

	}

	override function get(from: Int): Dynamic {

		return function (animMats: Array<Mat4>) {

			if(! ready) init();

			inputs[1].get()(animMats);
			boneName = inputs[2].get();
			goal = inputs[3].get();
			poleEnabled = inputs[4].get();
			pole = inputs[5].get();
			rollAngle = inputs[6].get();
			influence = inputs[7].get();
			layerMask = inputs[8].get();

			var bone = animation.getBone(boneName);

			if(! poleEnabled) pole = null;

			switch (property0) {
				case "2 Bone":
					AnimationExtension.solveTwoBoneIKBlend(animation, animMats, bone, goal, pole, 
												  rollAngle, influence, layerMask);
				case "FABRIK":
					chainLength = inputs[9].get();
					maxIterartions = inputs[10].get();
					precision = inputs[11].get();
					AnimationExtension.solveIKBlend(animation, animMats, bone, goal, precision, maxIterartions, 
							               chainLength, pole, rollAngle, influence, layerMask);
					
			}
		}
	}
	#end
}
