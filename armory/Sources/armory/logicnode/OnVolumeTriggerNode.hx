package armory.logicnode;

import iron.object.Object;
import iron.math.Vec4;
using armory.object.TransformExtension;

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

		// Use OBB-aware overlap to account for rotation and scale
		var overlap = TransformExtension.overlap_obb(t1, t2);

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
