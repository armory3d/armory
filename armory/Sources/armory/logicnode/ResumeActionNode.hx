package armory.logicnode;

import iron.object.Object;

class ResumeActionNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();

		if (object == null) return;
		var animation = object.animation;
		if (animation == null) animation = object.getParentArmature(object.name);

		animation.resume();

		runOutput(0);
	}
}
