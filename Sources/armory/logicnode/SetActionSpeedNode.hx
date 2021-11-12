package armory.logicnode;

import iron.object.Object;

class SetActionSpeedNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var action = inputs[2].get();
		var speed: Float = inputs[3].get();
		

		assert(Error, object != null, "Object input cannot be null");

		var animation = object.animation;

		if (animation == null) animation = object.getParentArmature(object.name);
		if(animation.activeActions == null) return;
		animation.activeActions.get(action).speed = speed;

		runOutput(0);
	}
}
