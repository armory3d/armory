package armory.logicnode;

import kha.FastFloat;
import iron.math.Quat;
import iron.math.Vec4;

class SeparateRotationNode extends LogicNode {

	public var property0 = "EulerAngles";	// EulerAngles, AxisAngle, or Quat
	public var property1 = "Rad";  // Rad or Deg
	public var property2 = "XYZ";

	static inline var toDEG:FastFloat = 57.29577951308232;  // 180/pi

	var input_cache = new Quat();
	var euler_cache = new Vec4();
	var aa_axis_cache = new Vec4();
	var aa_angle_cache: Float = 0;


	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var q: Quat = inputs[0].get();
		if (q == null) return null;
                q.normalize();

		switch (property0) {
		case "EulerAngles":
		        if (q!=this.input_cache)
				euler_cache = q.toEulerOrdered(property2);
			if (from>0)
				return null;
			
			switch (property1){
			case "Rad": return euler_cache;
			case "Deg": return new Vec4(euler_cache.x*toDEG, euler_cache.y*toDEG, euler_cache.z*toDEG);
			}
			
		case "AxisAngle":
			if (q!=this.input_cache)
				aa_angle_cache = q.toAxisAngle(aa_axis_cache);
			switch (from){
			case 0: return aa_axis_cache;
			case 1: switch(property1){
				case "Rad": return aa_angle_cache;
				case "Deg": return toDEG*aa_angle_cache;
			        }
			}
		case "Quaternion":
			switch(from){
			case 0: return new Vec4(q.x,q.y,q.z);
			case 1: return q.w;
			}
		}
		return null;
	}
}
