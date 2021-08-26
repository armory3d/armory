package armory.logicnode;

import iron.math.Quat;
import iron.math.Vec4;
import iron.math.Mat4;
import kha.FastFloat;

class RotationMathNode extends LogicNode {

	public var property0: String; // Operation
	var res_q = new Quat();
	var res_v = new Vec4();
	var res_f: FastFloat = 0.0;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		//var q: Quat = inputs[0].get();
		//if (q==null) return null;
		
		//var res_q: Quat = new Quat();
		switch (property0) {
			// 1 argument: Normalize, Inverse
			case "Normalize": {
			        var q: Quat = inputs[0].get();
				if (q==null) return null;
				res_q.setFrom(q);
				res_q = res_q.normalize();
			}
			case "Inverse": {
			var q: Quat = inputs[0].get();
				if (q==null) return null;
			        var modl = q.x*q.x + q.y*q.y + q.z*q.z + q.w*q.w;
				modl = -1/modl;
				res_q.w = -q.w*modl;
				res_q.x = q.x*modl;
				res_q.y = q.y*modl;
				res_q.z = q.z*modl;
			}			
			// 2 arguments: Compose, Amplify, FromTo, FromRotationMat,
			case "FromTo": {
				var v1: Vec4 = inputs[0].get();
				var v2: Vec4 = inputs[1].get();
				if ((v1 == null) || (v2 == null)) return null;
				res_q.fromTo(v1, v2);
			}
			case "Compose": {
				var v1: Quat = inputs[0].get();
				var v2: Quat = inputs[1].get();
				if ((v1 == null) || (v2 == null)) return null;
				res_q.multquats(v1,v2);
			}
			case "Amplify": {
				var v1: Quat = inputs[0].get();
				var v2: Float = inputs[1].get();
				if ((v1 == null) || (v2 == null)) return null;
				res_q.setFrom(v1);
				var fac2 = Math.sqrt(1- res_q.w*res_q.w);
				if (fac2 > 0.001) {
				    var fac1 = v2*Math.acos(res_q.w);
				    res_q.w = Math.cos(fac1);
				    fac1 = Math.sin(fac1)/fac2;
				    res_q.x *= fac1;
				    res_q.y *= fac1;
				    res_q.z *= fac1;
				}
			}
			//case "FromRotationMat": {
			//	var m: Mat4 = inputs[1].get();
			//	if (m == null) return null;

			//	res_q = res_q.fromMat(m);
			//}
			// # 3 arguments: Lerp, Slerp, FromAxisAngle, FromEuler
			case "Lerp": {
				//var from = q;
				var from: Quat = inputs[0].get();
				var to: Quat = inputs[1].get();
				var f: Float = inputs[2].get();
				if ((from == null) || (f == null) || (to == null)) return null;
				res_q = res_q.lerp(from, to, f);
			}
			case "Slerp": {
				//var from = q;
				var from:Quat = inputs[0].get();
				var to: Quat = inputs[1].get();
				var f: Float = inputs[2].get();
				if ((from == null) || (f == null) || (to == null)) return null;
				res_q = res_q.slerp(from, to, f);
			}
		}
		return res_q;
	}
}