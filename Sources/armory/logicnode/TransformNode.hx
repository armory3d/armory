package armory.logicnode;

import iron.math.Mat4;
import iron.math.Vec4;
import iron.math.Quat;

class TransformNode extends LogicNode {

	var value:Mat4 = Mat4.identity();
	static var q = new Quat();

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {

		var loc:Vec4 = inputs[0].get();
		var rot:Vec4 = inputs[1].get();
		q.fromEuler(rot.x, rot.y, rot.z);
		var scale:Vec4 = inputs[2].get();
		value.compose(loc, q, scale);

		return value;
	}

	override function set(value:Dynamic) {
		this.value = value;
	}
}
