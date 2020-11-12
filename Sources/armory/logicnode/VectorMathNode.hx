package armory.logicnode;

import iron.math.Vec4;

class VectorMathNode extends LogicNode {

	public var property0: String; // Operation
	public var property1: Bool;   // Separator Out
	var res_v = new Vec4();
	var res_f = 0.0;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var p1: Vec4 = inputs[0].get();
		if (p1 == null) return null;
		res_v.setFrom(p1);
		switch (property0) {
			// 1 arguments: Normalize, Length 
			case "Normalize":
				res_v.normalize();
			case "Length":
				res_f = res_v.length();
			// 2 arguments: Distance, Reflect
			case "Distance": {
				var p2: Vec4 = inputs[1].get();
				if (p2 == null) return null;
				res_f = res_v.distanceTo(p2);
			}
			case "Reflect": {
				var p2: Vec4 = inputs[1].get();
				if (p2 == null) return null;
				res_v.reflect(p2); 
			}
			// Many arguments: Add, Subtract, Average, Dot Product, Cross Product, Multiply
			case "Add": {
				var p2 = new Vec4();
				var i = 1;
				while (i < inputs.length) {
					p2 = inputs[i].get();
					if (p2 == null) return null;
					res_v.add(p2);
					i++;
				}
			}
			case "Subtract": {
				var p2 = new Vec4();
				var i = 1;
				while (i < inputs.length) {
					p2 = inputs[i].get();
					if (p2 == null) return null;
					res_v.sub(p2);
					i++;
				}
			}
			case "Average": {
				var p2 = new Vec4();
				var i = 1;
				while (i < inputs.length) {
					p2 = inputs[i].get();
					if (p2 == null) return null;
					res_v.add(p2);
					res_v.mult(0.5);
					i++;
				}
			}
			case "Dot Product": {
				var p2 = new Vec4();
				var i = 1;
				while (i < inputs.length) {
					p2 = inputs[i].get();
					if (p2 == null) return null;
					res_f = res_v.dot(p2);
					res_v.set(res_f, res_f, res_f);
					i++;
				}
			}
			case "Cross Product": {
				var p2 = new Vec4();
				var i = 1;
				while (i < inputs.length) {
					p2 = inputs[i].get();
					if (p2 == null) return null;
					res_v.cross(p2);
					i++;
				}
			}
			case "Multiply": {
				var p2 = new Vec4();
				var i = 1;
				while (i < inputs.length) {
					p2 = inputs[i].get();
					if (p2 == null) return null;
					res_v.x *= p2.x;
					res_v.y *= p2.y;
					res_v.z *= p2.z;
					i++;
				}
			}
			case "MultiplyFloats": {
				var p2_f = 1.0;
				var i = 1;
				while (i < inputs.length) {
					p2_f = inputs[i].get();
					res_v.mult(p2_f);
					i++;
				}
			}
		}
		// Return and check separator
		switch (from) {
			case 0: return res_v;
			case 1: 
				if (property1) {
					return res_v.x;
				} else {
					return res_f;
				}
			case 2: 
				if (property1) {
					return res_v.y;
				} else {
					return res_f;
				}
			case 3: 
				if (property1) {
					return res_v.z;
				} else {
					return res_f;
				}
			case 4: 
				if (property1) return res_f;
		}
		return null;
	}
}