package armory.logicnode;

import armory.object.Object;
import armory.math.Vec4;

class VolumeTriggerNode extends LogicNode {

	public var property0:String;
	var lastOverlap = false;

	var l1 = new Vec4();
	var l2 = new Vec4();

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int) {
		var object:Object = inputs[0].get();
		var volume:Object = inputs[1].get();

		if (object == null) object = tree.object;
		if (volume == null) volume = tree.object;

		var t1 = object.transform;
		var t2 = volume.transform;
		l1.set(t1.absx(), t1.absy(), t1.absz());
		l2.set(t2.absx(), t2.absy(), t2.absz());
		var s1 = t1.size;
		var s2 = t2.size;

		var overlap = l1.x + s1.x / 2 > l2.x - s2.x / 2 && l1.x - s1.x / 2 < l2.x + s2.x / 2 &&
				  	  l1.y + s1.y / 2 > l2.y - s2.y / 2 && l1.y - s1.y / 2 < l2.y + s2.y / 2 &&
				  	  l1.z + s1.z / 2 > l2.z - s2.z / 2 && l1.z - s1.z / 2 < l2.z + s2.z / 2;

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
