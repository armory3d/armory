package armory.logicnode;

import iron.object.Object;
import iron.math.Vec4;

class VolumeTriggerNode extends LogicNode {

	public var property0:String;
	var lastOverlap = false;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int) {
		var object:Object = inputs[0].get();
		var volume:Object = inputs[1].get();

		if (object == null) return false;
		if (volume == null) volume = tree.object;

		var t1 = object.transform;
		var t2 = volume.transform;
		var overlap = t1.overlap(t2);

		var b = false;
		switch (property0) {
		case "Enter":
			b = overlap && !lastOverlap;
		case "Leave":
			b = !overlap && lastOverlap;
		case "Overlap":
			b = overlap;
		}

		lastOverlap = overlap;
		return b;
	}
}
