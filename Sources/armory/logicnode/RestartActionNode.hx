package armory.logicnode;

import iron.object.Object;

class RestartActionNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var action = inputs[2].get();		

		if (object == null) return;

		var animation = object.animation;

		if (animation == null) animation = object.getParentArmature(object.name);

		animation.activeActions.get(action).restartAction();

		runOutput(0);
	}
}
