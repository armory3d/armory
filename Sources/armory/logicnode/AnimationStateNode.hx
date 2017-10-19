package armory.logicnode;

import armory.object.Object;

class AnimationStateNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var object:Object = inputs[0].get();

		if (object == null) return null;

		// Try first child if we are running from armature
		if (object.animation == null) object = object.children[0];

		if (from == 0) return !object.animation.paused; // is playing
		else if (from == 1) return object.animation.action;
		else return object.animation.timeIndex;
	}
}
