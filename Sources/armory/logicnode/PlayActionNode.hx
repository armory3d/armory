package armory.logicnode;

import armory.object.Object;

class PlayActionNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:Object = inputs[1].get();
		var action:String = inputs[2].get();
		
		if (object == null) return;

		// Try first child if we are running from armature
		if (object.animation == null) object = object.children[0];

		object.animation.play(action, function() {
			runOutputs(1);
		});

		runOutputs(0);
	}
}
