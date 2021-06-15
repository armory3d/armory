package armory.logicnode;

import iron.math.Mat4;
import iron.math.Vec4;
import iron.math.Quat;

class TransformNode extends LogicNode {

	var value: Mat4 = Mat4.identity();
	var q = new Quat();
	var v1 = new Vec4();
	var v2 = new Vec4();

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var loc: Vec4 = inputs[0].get();
		var rot: Quat = new Quat().setFrom(inputs[1].get());
		rot.normalize();
		var scale: Vec4 = inputs[2].get();
		if (loc == null && rot == null && scale == null) return this.value;
		if (loc == null || rot == null || scale == null) return null;
		this.value.compose(loc, rot, scale);
		return this.value;
	}

	override function set(value: Dynamic) {
	        if (inputs.length>0){
			cast(value, Mat4).decompose(v1, q, v2);
			inputs[0].set(v1);
			inputs[1].set(q);
			inputs[2].set(v2);
		}else this.value = value;
	}
}
