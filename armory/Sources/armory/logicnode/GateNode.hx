package armory.logicnode;

import iron.math.Vec4;

class GateNode extends LogicNode {

	public var property0: String;
	public var property1: Float;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var v1: Dynamic = inputs[1].get();
		var v2: Dynamic = inputs[2].get();
		var cond = false;

		switch (property0) {
		case "Equal":
			cond = Std.isOfType(v1, Vec4) ? (v1: Vec4).equals(v2) : v1 == v2;
		case "Not Equal":
			cond = Std.isOfType(v1, Vec4) ? !(v1: Vec4).equals(v2) : v1 != v2;
		case "Almost Equal":
			cond = Std.isOfType(v1, Vec4) ? (v1: Vec4).almostEquals(v2, property1) : Math.abs(v1 - v2) < property1;
		case "Greater":
			cond = v1 > v2;
		case "Greater Equal":
			cond = v1 >= v2;
		case "Less":
			cond = v1 < v2;
		case "Less Equal":
			cond = v1 <= v2;
		case "Between":
			var v3: Dynamic = inputs[3].get();
			cond = Std.isOfType(v1, Vec4) ? v2.x <= v1.x && v2.y <= v1.y && v2.z <= v1.z && v1.x <= v3.x && v1.y <= v3.y && v1.z <= v3.z : v2 <= v1 && v1 <= v3;
		case "Or":
			for (i in 1...inputs.length) {
				if (inputs[i].get()) {
					cond = true;
					break;
				}
			}
		case "And":
			cond = true;
			for (i in 1...inputs.length) {
				if (!inputs[i].get()) {
					cond = false;
					break;
				}
			}
		}

		cond ? runOutput(0) : runOutput(1);
	}
}
