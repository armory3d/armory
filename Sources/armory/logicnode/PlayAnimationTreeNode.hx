package armory.logicnode;

import iron.object.Object;
import iron.Scene;

class PlayAnimationTreeNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var action: Dynamic = inputs[2].get();

		if (object == null) return;
		var animation = object.getParentArmature(object.name);

		animation.animationLoop(function f(mats) {
			action(mats);
			
		});

		runOutput(0);
	}
}
