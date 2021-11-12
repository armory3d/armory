package armory.logicnode;

import kha.FastFloat;
import iron.object.ObjectAnimation;
import iron.object.Object;
import iron.object.Animation;
import iron.object.BoneAnimation;
import iron.math.Mat4;


class AnimActionNode extends LogicNode {

	public var property0: String;
	public var value: String;
	public var actionParam: Animparams;
	var object: Object;
	var animation: Animation;
	var isArmature: Bool;
	var ready = false;

	public function new(tree: LogicTree) {
		super(tree);

	}

	function init(){
		actionParam = new Animparams(inputs[1].get(), 1.0, inputs[2].get());
		object = inputs[0].get();
		assert(Error, object != null, "The object input not be null");
		animation = object.animation;
		if(animation == null) {
			animation = object.getParentArmature(object.name);
			isArmature = true;
		}
		else {
			isArmature = false;
		}
		animation.registerAction(property0, actionParam);

		ready = true;
	}

	override function get(from: Int): Dynamic {

		if(!ready) init();

		if(isArmature){
			return function (animMats: Array<Mat4>){ cast(animation, BoneAnimation).sampleAction(actionParam, animMats);};
		}
		else {
			return function (animMats: Map<String, FastFloat>){ cast(animation, ObjectAnimation).sampleAction(actionParam, animMats);};
		}
	}

}
