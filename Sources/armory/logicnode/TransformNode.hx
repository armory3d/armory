package armory.logicnode;

import iron.math.Mat4;
import iron.math.Vec4;
import iron.math.Quat;
import iron.object.Transform;

class TransformNode extends Node {

	var value:Mat4 = Mat4.identity();
	static var q:Quat = new Quat();

	public function new(trait:armory.Trait) {
		super(trait);
	}

	override function get():Dynamic {

		var loc = inputs[0].get();
		var rot = inputs[1].get();
		q.fromEuler(rot.x, rot.y, rot.z);
		var scale = inputs[2].get();
		value.compose(loc, q, scale);
		return value;
	}
}
