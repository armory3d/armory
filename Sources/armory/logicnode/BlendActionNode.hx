package armory.logicnode;

import iron.object.Animation;
import iron.math.Mat4;
import iron.object.Object;

class BlendActionNode extends LogicNode {

	var object: Object;
	var animation: Animation;
	var tempMats: Array<Mat4>;

	public function new(tree: LogicTree) {
		super(tree);
		tree.notifyOnInit(init);
	}

	public function init(){
		object = inputs[0].get();
		animation = object.animation;
		if (animation == null) animation = object.getParentArmature(object.name);
		tempMats = animation.initMatsEmpty();

	}

	override function get(from: Int): Dynamic {
		return function (animMats: Array<Mat4>){ 
			inputs[1].get()(animMats);
			inputs[2].get()(tempMats);
			animation.blendActionMats(animMats, tempMats, animMats, inputs[3].get(), inputs[4].get());
		};
		
	}
}
