package armory.logicnode;

import iron.math.Vec4;
import armory.math.Helper;

class VectorClampToSizeNode extends LogicNode {

	/** Clamping mode ("length" or "components"). **/
	public var property0: String;

	var v: Vec4;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		v = (inputs[0].get(): Vec4).clone();
		var fmin: kha.FastFloat = inputs[1].get();
		var fmax: kha.FastFloat = inputs[2].get();

		if (property0 == "length") {
			v.clamp(fmin, fmax);
		}
		else if (property0 == "components") {
			v.x = Helper.clamp(v.x, fmin, fmax);
			v.y = Helper.clamp(v.y, fmin, fmax);
			v.z = Helper.clamp(v.z, fmin, fmax);
		}

		return v;
	}
}
