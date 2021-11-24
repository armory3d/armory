package armory.logicnode;

import iron.object.Animation;
import iron.object.Object;

class AnimationStateNode extends LogicNode {

	var object: Object;
	var animation: Animation;
	var action: Animparams;
	public var property0: String;
	public var ready = false;

	public function new(tree: LogicTree) {
		super(tree);
	}

	public function init() {
		object = inputs[0].get();
		assert(Error, object != null, "Object input cannot be null");
		animation = object.animation;
		if (animation == null) animation = object.getParentArmature(object.name);
		assert(Error, animation != null, "Object does not have animations");
		action = animation.activeActions.get(property0);
		if(action == null) return;
		action.notifyOnComplete(function (){runOutput(3);});
		
	}

	override function get(from: Int): Dynamic {
		if(! ready) init();
		if(action == null) return null;
		return switch (from) {
			case 0: action.action;
			case 1: action.offset;
			case 2: action.paused;
			default: null;
		}
	}
}
