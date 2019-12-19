package armory.logicnode;

import iron.object.Object;

class PlayActionNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var action: String = inputs[2].get();
		var blendTime: Float = inputs[3].get();

		if (object == null) return;
		var animation = object.animation;
		if (animation == null) animation = object.getParentArmature(object.name);

		animation.play(action, function() {
			runOutput(1);
		}, blendTime);

		runOutput(0);
	}
}
