package armory.logicnode;

import iron.object.Object;

class OnActionMarkerNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);

		iron.Scene.active.notifyOnInit(init);
	}

	function init() {
		var object:Object = inputs[0].get();
		var marker:String = inputs[1].get();
		
		if (object == null) return;
		// Try first child if we are running from armature
		if (object.animation == null) object = object.children[0];
		
		object.animation.notifyOnMarker(marker, run);
	}
}
