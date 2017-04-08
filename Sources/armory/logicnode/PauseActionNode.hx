package armory.logicnode;

import armory.object.Object;

class PauseActionNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:Object = inputs[1].get();
		
		if (object == null) object = tree.object;

		object.animation.player.pause();

		super.run();
	}
}
