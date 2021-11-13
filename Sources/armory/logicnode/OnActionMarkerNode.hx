package armory.logicnode;

import iron.object.Object;

class OnActionMarkerNode extends LogicNode {

	public var property0: String;
	public var property1: String;

	public function new(tree: LogicTree) {
		super(tree);

		tree.notifyOnUpdate(init);
	}

	function init() {
		var object: Object = inputs[0].get();
		var actionID: String = property0;
		var marker: String = property1;

		assert(Error, object != null, "Object input cannot be null");
		var animation = object.animation;
		if (animation == null) animation = object.getParentArmature(object.name);
		var action = animation.activeActions.get(actionID);
		if(action == null) return;
		animation.notifyOnMarker(action, marker, function() { runOutput(0); });
		tree.removeUpdate(init);
	}
}
