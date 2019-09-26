package armory.logicnode;

import iron.object.Object;
import iron.math.Quat;
import iron.math.Vec3;

class GetRotationNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		if (from == 0) {
			var object:Object = inputs[0].get();
			if (object == null) return null;
			return object.transform.rot.getEuler();
		}
		if (from == 1) {
			//angle
			var object:Object = inputs[0].get();
			if (object == null) return null;
			var rot = object.transform.rot;
			var angle = 2 * Math.acos(rot.w);
			return angle * (180 / Math.PI); 
		} else if (from == 2) {
			//vector
			var object:Object = inputs[0].get();
			if (object == null) return null;
			var rot = object.transform.rot;
			var sqrtW = Math.sqrt(1 - (rot.w * rot.w));
			if (sqrtW == 0)
				return new Vec3(0, 0, 1);
			return new Vec3(rot.x / sqrtW, rot.y / sqrtW, rot.z / sqrtW);
		}
		return null;
	}
}
