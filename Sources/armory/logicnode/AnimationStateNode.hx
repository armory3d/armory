package armory.logicnode;

import iron.object.Object;

class AnimationStateNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var object:Object = inputs[0].get();

		if (object == null) return null;
		var animation = object.animation;
		if (animation == null) animation = object.getParentArmature(object.name);

		if (from == 0) return !animation.paused; // is playing
		else if (from == 1) return animation.action;
		else return animation.currentFrame();
	}
}
