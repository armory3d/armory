package armory.logicnode;

import iron.math.Mat4;
import iron.math.Vec4;
import iron.math.Quat;

class TransformNode extends LogicNode {

	var value:Mat4 = Mat4.identity();
	static var q = new Quat();
	static var v1 = new Vec4();
	static var v2 = new Vec4();

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var loc:Vec4 = inputs[0].get();
		var rot:Vec4 = inputs[1].get();
		var scale:Vec4 = inputs[2].get();
		if (loc == null || rot == null || scale == null) return null;
		q.fromEuler(rot.x, rot.y, rot.z);
		value.compose(loc, q, scale);
		return value;
	}

	override function set(value:Dynamic) {
		cast(value, Mat4).decompose(v1, q, v2);
		inputs[0].set(v1);
		inputs[1].set(q.getEuler());
		inputs[2].set(v2);
	}
}
