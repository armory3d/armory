package armory.logicnode;

import iron.object.Object;

class SetActionPausedNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var enabled: Bool = inputs [2].get();

		if (object == null) return;

		var animation = object.animation;

		if (animation == null) animation = object.getParentArmature(object.name);

		enabled ? animation.resume() : animation.pause();

		runOutput(0);
	}
}
