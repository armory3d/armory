package armory.logicnode;

import kha.arrays.Float32Array;
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

	public function new(tree: LogicTree) {
		super(tree);
		tree.notifyOnInit(init);

	}

	function init(){
		actionParam = new Animparams(inputs[1].get(), 1.0, inputs[2].get());
		object = inputs[0].get();
		if (object == null) return;
		animation = object.animation;
		if (animation == null) animation = object.getParentArmature(object.name);
		else animation = cast(animation, ObjectAnimation);
		animation.registerAction(property0, actionParam);

	}

	override function get(from: Int): Dynamic {
		if(Std.isOfType(animation, BoneAnimation)){
			var animationB = cast(animation, BoneAnimation);
			return function (animMats: Array<Mat4>){ animationB.sampleAction(actionParam, animMats);};
		}
		else{
			trace("object mode get");
			var animationO = cast(animation, ObjectAnimation);
			return function (animT: Float32Array) { 
				trace("in sample func");
				animationO.sampleAction(actionParam, animT);
			};
		}
		return null;
	}

	/* override function set(value: Dynamic) {
		if (inputs.length > 0) inputs[0].set(value);
		else this.value = value;
	} */
}
