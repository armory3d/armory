package armory.logicnode;

import iron.math.Vec4;
import iron.math.Quat;

class LookAtNode extends LogicNode {

	public var property0: String;
	var v1 = new Vec4();
	var v2 = new Vec4();
	var q = new Quat();

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var vfrom: Vec4 = inputs[0].get();
		var vto: Vec4 = inputs[1].get();

		if (vfrom == null || vto == null) return null;

		switch (property0) {
			case "X":
				v1.set(1, 0, 0);
			case "-X":
				v1.set(-1, 0, 0);
			case "Y":
				v1.set(0, 1, 0);
			case "-Y":
				v1.set(0, -1, 0);
			case "Z":
				v1.set(0, 0, 1);
			case "-Z":
				v1.set(0, 0, -1);
		}
		v2.setFrom(vto).sub(vfrom).normalize();

		q.fromTo(v1, v2);
		return q;
	}
}
