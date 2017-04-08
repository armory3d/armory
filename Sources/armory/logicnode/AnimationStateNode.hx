package armory.logicnode;

import armory.object.Object;

class AnimationStateNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var object:Object = inputs[0].get();

		if (object == null) object = tree.object;

		if (from == 0) return !object.animation.player.paused; // is playing
		else if (from == 1) return object.animation.player.timeIndex;
		else return object.animation.player.current.name;
	}
}
