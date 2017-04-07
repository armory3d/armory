package armory.logicnode;

import armory.object.Object;

class PlayActionNode extends Node {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:Object = inputs[1].get();
		var action:String = inputs[2].get();
		
		if (object == null) object = tree.object;

		object.animation.player.play(action, function() {
			runOutputs(1);
		});

		runOutputs(0);
	}
}
