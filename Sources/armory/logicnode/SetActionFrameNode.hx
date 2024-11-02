package armory.logicnode;

import iron.object.Object;

class SetActionFrameNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var action = inputs[2].get();
		var frame: Int = inputs[3].get();
		

		assert(Error, object != null, "Object input cannot be null");

		var animation = object.animation;

		if(animation == null) animation = object.getBoneAnimation(object.uid);
		if(animation.activeActions == null) return;
		final act = animation.activeActions.get(action);
		if(act == null) return;
		act.setFrameOffset(frame);

		runOutput(0);
	}
}
