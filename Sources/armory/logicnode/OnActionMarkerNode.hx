package armory.logicnode;

import iron.object.Object;

class OnActionMarkerNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);

		tree.notifyOnInit(init);
	}

	function init() {
		var object: Object = inputs[0].get();
		var marker: String = inputs[1].get();

		if (object == null) return;
		var animation = object.animation;
		if (animation == null) animation = object.getParentArmature(object.name);

		animation.notifyOnMarker(marker, function() { runOutput(0); });
	}
}
