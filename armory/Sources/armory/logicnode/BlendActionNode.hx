package armory.logicnode;

import iron.object.Object;

class BlendActionNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var action1: String = inputs[2].get();
		var action2: String = inputs[3].get();
		var blendFactor: Float = inputs[4].get();

		if (object == null || action1 == "" || action2 == "") return;
		var animation = object.animation;
		if (animation == null) animation = object.getParentArmature(object.name);

		animation.blend(action1, action2, blendFactor);

		runOutput(0);
	}
}
