package armory.logicnode;

import armory.object.Object;

class ResumeActionNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:Object = inputs[1].get();
		
		if (object == null) return;

		// Try first child if we are running from armature
		if (object.animation == null) object = object.children[0];

		object.animation.resume();

		super.run();
	}
}
