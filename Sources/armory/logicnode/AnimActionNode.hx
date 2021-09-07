package armory.logicnode;

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
		animation.registerAction(property0, actionParam);

	}

	override function get(from: Int): Dynamic {
		return function (animMats: Array<Mat4>){ animation.sampleAction(actionParam, animMats);};
		
	}

	/* override function set(value: Dynamic) {
		if (inputs.length > 0) inputs[0].set(value);
		else this.value = value;
	} */
}
