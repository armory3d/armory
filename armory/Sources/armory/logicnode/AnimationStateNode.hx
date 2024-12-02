package armory.logicnode;

import iron.object.Object;

class AnimationStateNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: Object = inputs[0].get();

		if (object == null) return null;

		var animation = object.animation;

		if (animation == null) animation = object.getParentArmature(object.name);

		return switch (from) {
			case 0: animation.action;
			case 1: animation.currentFrame();
			case 2: animation.paused;
			default: null;
		}
	}
}
