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
			// 1 argument: Module, Normalize, GetEuler
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
			case "GetEuler":  {
				var q: Quat = inputs[0].get();
				if (q == null) return null;
				res_q.setFrom(q);
				res_v = res_q.getEuler();
			}
			// 2 arguments: FromTo, FromMat, FromRotationMat, ToAxisAngle
			case "FromTo": {
				var v1: Vec4 = inputs[0].get();
				var v2: Vec4 = inputs[1].get();
				if ((v1 == null) || (v2 == null)) return null;
				res_q.fromTo(v1, v2);
			}
			case "FromMat": {
				var q: Quat = inputs[0].get();
				var m: Mat4 = inputs[1].get();
				if ((q == null) || (m == null)) return null;
				res_q.setFrom(q);
				res_q = res_q.fromMat(m);
			}
			case "FromRotationMat": {
				var q: Quat = inputs[0].get();
				var m: Mat4 = inputs[1].get();
				if ((q == null) || (m == null)) return null;
				res_q.setFrom(q);
				res_q = res_q.fromRotationMat(m);
			}
			case "ToAxisAngle": {
				var q: Quat = inputs[0].get();
				var v: Vec4 = inputs[1].get();
				if ((q == null) || (v == null)) return null;
				res_q.setFrom(q);
				res_f = res_q.toAxisAngle(v);
			}
			// # 3 arguments: Lerp, Slerp, FromAxisAngle, FromEuler
			case "Lerp": {
				var from: Quat = inputs[0].get();
				var to: Quat = inputs[1].get();
				var f: Float = inputs[2].get();
				if ((from == null) || (to == null)) return null;
				res_q = res_q.lerp(from, to, f);
			}
			case "Slerp": {
				var from: Quat = inputs[0].get();
				var to: Quat = inputs[1].get();
				var f: Float = inputs[2].get();
				if ((from == null) || (to == null)) return null;
				res_q = res_q.slerp(from, to, f);
			}
			case "FromAxisAngle": {
				var q: Quat = inputs[0].get();
				var axis: Vec4 = inputs[1].get();
				var angle: Float = inputs[2].get();
				if ((q == null) || (axis == null)) return null;
				res_q.setFrom(q);
				res_q = res_q.fromAxisAngle(axis, angle);
			}
			case "FromEuler": {
				var x: Float = inputs[0].get();
				var y: Float = inputs[1].get();
				var z: Float = inputs[2].get();
				res_q = res_q.fromEuler(x, y, z);
			}
			// Many arguments: Add, Subtract, DotProduct, Multiply			
			case "Add": {
				var q: Quat = inputs[0].get();
				if (q == null) return null;
				res_q.setFrom(q);
				var q2 = new Quat();
				var i = 1;
				while (i < inputs.length) {
					q2 = inputs[i].get();
					if (q2 == null) return null;
					res_q.add(q2);
					i++;
				}
			}
			case "Subtract": {
				var q: Quat = inputs[0].get();
				if (q == null) return null;
				res_q.setFrom(q);
				var q2 = new Quat();
				var i = 1;
				while (i < inputs.length) {
					q2 = inputs[i].get();
					if (q2 == null) return null;
					res_q.sub(q2);
					i++;
				}
			}
			case "Multiply": {
				var q: Quat = inputs[0].get();
				if (q == null) return null;
				res_q.setFrom(q);
				var q2 = new Quat();
				var i = 1;
				while (i < inputs.length) {
					q2 = inputs[i].get();
					if (q2 == null) return null;
					res_q.mult(q2);
					i++;
				}
			}
			case "MultiplyFloats": {
				var q: Quat = inputs[0].get();
				if (q == null) return null;
				res_q.setFrom(q);
				var f: Float = 1.0;
				var i = 1;
				while (i < inputs.length) {
					f = inputs[i].get();
					res_q.scale(f);
					i++;
				}
			}
			case "DotProduct": {
				var q: Quat = inputs[0].get();
				if (q == null) return null;
				res_q.setFrom(q);
				var q2 = new Quat();
				var i = 1;
				while (i < inputs.length) {
					q2 = inputs[i].get();
					if (q2 == null) return null;
					res_f = res_q.dot(q2);
					res_q.set(res_f, res_f, res_f, res_f);
					i++;
				}
			}
		}
		// Return and check separator
		switch (from) {
			case 0: {
				if (property0 == 'GetEuler')
					return res_v;
				else
					return res_q;
			}
			case 1: 
				if (property1) {
					return res_q.x;
				} else {
					return res_f;
				}
			case 2: 
				if (property1) return res_q.y;
			case 3: 
				if (property1) return res_q.z;
			case 4: 
				if (property1) return res_q.w;
			case 5: 
				if (property1) return res_f;
		}
		return null;
	}
}