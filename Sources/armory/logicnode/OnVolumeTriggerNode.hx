package armory.logicnode;

import iron.object.Object;
import iron.math.Vec4;

class OnVolumeTriggerNode extends LogicNode {

	public var property0: String;
	var lastOverlap = false;

	var l1 = new Vec4();
	var l2 = new Vec4();

	public function new(tree: LogicTree) {
		super(tree);

		tree.notifyOnUpdate(update);
	}

	function update() {
		var object: Object = inputs[0].get();
		var volume: Object = inputs[1].get();

		if (object == null) return;
		if (volume == null) volume = tree.object;

		var t1 = object.transform;
		var t2 = volume.transform;
		l1.set(t1.worldx(), t1.worldy(), t1.worldz());
		l2.set(t2.worldx(), t2.worldy(), t2.worldz());
		var d1 = t1.dim;
		var d2 = t2.dim;

		var overlap = l1.x + d1.x / 2 > l2.x - d2.x / 2 && l1.x - d1.x / 2 < l2.x + d2.x / 2 &&
				  	  l1.y + d1.y / 2 > l2.y - d2.y / 2 && l1.y - d1.y / 2 < l2.y + d2.y / 2 &&
				  	  l1.z + d1.z / 2 > l2.z - d2.z / 2 && l1.z - d1.z / 2 < l2.z + d2.z / 2;

		var b = false;
		switch (property0) {
		case "begin":
			b = overlap && !lastOverlap;
		case "overlap":
			b = overlap;
		case "end":
			b = !overlap && lastOverlap;
		}

		lastOverlap = overlap;

		if (b) runOutput(0);
	}
}
