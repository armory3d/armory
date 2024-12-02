package armory.logicnode;

import iron.math.Quat;
import iron.math.Vec4;
import iron.math.Mat4;
import kha.FastFloat;

class QuaternionMathNode extends LogicNode {

	public var property0: String; // Operation
	public var property1: Bool;   // Separator Out
	var res_q = new Quat();
	var res_v = new Vec4();
	var res_f: FastFloat = 0.0;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		switch (property0) {
			// 1 argument: Module, Normalize
			case "Module": {
				var q: Quat = inputs[0].get();
				if (q == null) return null;
				res_q.setFrom(q);
				res_f = res_q.module();
			}
			case "Normalize": {
				var q: Quat = inputs[0].get();
				if (q == null) return null;
				res_q.setFrom(q);
				res_q = res_q.normalize();
			}
			// Many arguments: Add, Subtract, DotProduct, Multiply			
			case "Add": {
				res_v = inputs[0].get();
				res_f = inputs[1].get();
				if (res_v == null || res_f == null) return null;
				
				res_q.set(res_v.x, res_v.y, res_v.z, res_f);
				var i = 1;
				while (2*i+1 < inputs.length) {
					res_v = inputs[2*i].get();
					res_f = inputs[2*i+1].get();
					if (res_v == null || res_f == null) return null;
					res_q.x += res_v.x;
					res_q.y += res_v.y;
					res_q.z += res_v.z;
					res_q.w += res_f;
					i++;
				}
			}
			case "Subtract": {
				res_v = inputs[0].get();
				res_f = inputs[1].get();
				if (res_v == null || res_f == null) return null;
				
				res_q.set(res_v.x, res_v.y, res_v.z, res_f);
				var i = 1;
				while (2*i+1 < inputs.length) {
					res_v = inputs[2*i].get();
					res_f = inputs[2*i+1].get();
					if (res_v == null || res_f == null) return null;
					res_q.x -= res_v.x;
					res_q.y -= res_v.y;
					res_q.z -= res_v.z;
					res_q.w -= res_f;
					i++;
				}
			}
			case "Multiply": {
				res_v = inputs[0].get();
				res_f = inputs[1].get();
				if (res_v == null || res_f == null) return null;
				
				res_q.set(res_v.x, res_v.y, res_v.z, res_f);
				var i = 1;
				while (2*i+1 < inputs.length) {
					res_v = inputs[2*i].get();
					res_f = inputs[2*i+1].get();
					if (res_v == null || res_f == null) return null;
					var temp_q = new Quat(res_v.x, res_v.y, res_v.z, res_f);
					res_q.mult(temp_q);
					i++;
				}
			}
			case "MultiplyFloats": {
				res_v = inputs[0].get();
				res_f = inputs[1].get();
				if (res_v == null || res_f == null) return null;
				
				res_q.set(res_v.x, res_v.y, res_v.z, res_f);
				var f: Float = 1.0;
				var i = 2;
				while (i < inputs.length) {
					f *= inputs[i].get();
					if (f == null) return null;
					i++;
				}
				res_q.scale(f);
			}
			case "DotProduct": {  // what this does with more than 2 terms is not *remotely* intuitive. Heck, you could consider it a footgun!

				res_v = inputs[0].get();
				var temp_f = inputs[1].get();
				if (res_v == null || temp_f == null) return null;
				
				res_q.set(res_v.x, res_v.y, res_v.z, temp_f);
				var i = 1;
				while (2*i+1 < inputs.length) {
					res_v = inputs[2*i].get();
					temp_f = inputs[2*i+1].get();
					if (res_v == null || temp_f == null) return null;
					var temp_q = new Quat(res_v.x, res_v.y, res_v.z, temp_f);
					res_f = res_q.dot(temp_q);
					res_q.set(res_f, res_f, res_f, res_f);
					i++;
				}
			}
		}
		switch (from) {
			case 0: {
				return res_q;
			}
			case 1: 
				if (property0 == "DotProduct" || property0 == "Module") {
					return res_f;
				} else {
					return null;
				}
			default: {
				return null;
			}
		}
	}
}