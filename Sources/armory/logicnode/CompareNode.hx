package armory.logicnode;

import iron.math.Vec4;

class CompareNode extends LogicNode {

	public var property0:String;
	public var property1:Float;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Bool {

		var v1:Dynamic = inputs[0].get();
		var v2:Dynamic = inputs[1].get();
		var cond = false;

		switch (property0) {
		case "Equal":
			cond = Std.is(v1, Vec4) ? v1.equals(v2) : v1 == v2;
		case "Almost Equal":
			cond = Std.is(v1, Vec4) ? v1.almostEquals(v2, property1) : Math.abs(v1 - v2) < property1;
		case "Greater":
			cond = v1 > v2;
		case "Greater Equal":
			cond = v1 >= v2;
		case "Less":
			cond = v1 < v2;
		case "Less Equal":
			cond = v1 <= v2;
		case "Or":
			for (input in inputs) {
				if (input.get()) {
					cond = true;
					break;
				}
			}
		case "And":
			cond = true;
			for (input in inputs) {
				if (!input.get()) {
					cond = false;
					break;
				}
			}
		}

		return cond;
	}
}
