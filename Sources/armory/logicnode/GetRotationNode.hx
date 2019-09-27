package armory.logicnode;

import iron.object.Object;
import iron.math.Quat;
import iron.math.Vec3;

class GetRotationNode extends LogicNode {
	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		switch (from) {
			case 0:
				// euler angles
				var object:Object = inputs[0].get();
				if (object == null)
					return null;
				return object.transform.rot.getEuler();
			case 1:
				// angle radians
				var object:Object = inputs[0].get();
				if (object == null)
					return null;
				var rot = object.transform.rot;
				var angle = 2 * Math.acos(rot.w);
				return angle;
			case 2:
				// angle degrees
				var object:Object = inputs[0].get();
				if (object == null)
					return null;
				var rot = object.transform.rot;
				var angle = 2 * Math.acos(rot.w);
				return angle * (180 / Math.PI);
			case 3:
				// vector
				var object:Object = inputs[0].get();
				if (object == null)
					return null;
				var rot = object.transform.rot;
				var sqrtW = Math.sqrt(1 - (rot.w * rot.w));
				if (sqrtW == 0)
					return new Vec3(0, 0, 1);
				return new Vec3(rot.x / sqrtW, rot.y / sqrtW, rot.z / sqrtW);
			case 4:
				return new Vec3(rot.x, rot.y, rot.z); 
			case 5:
				return rot.w;
		}
		return null;
	}
}
