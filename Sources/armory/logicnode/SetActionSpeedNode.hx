package armory.logicnode;

import iron.object.Object;

class SetActionSpeedNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:Object = inputs[1].get();
		var speed:Float = inputs[2].get();
		
		if (object == null) return;

		// Try first child if we are running from armature
		if (object.animation == null) object = object.children[0];

		object.animation.speed = speed;

		super.run();
	}
}
