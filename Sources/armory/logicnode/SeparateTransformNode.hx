package armory.logicnode;

import iron.math.Mat4;
import iron.math.Vec4;
import iron.math.Quat;

class SeparateTransformNode extends Node {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var matrix:Mat4 = inputs[0].get();

		var loc = new Vec4();
		var rot = new Quat();
		var scale = new Vec4();
		matrix.decompose(loc, rot, scale);

		if (from == 0) return loc;
		else if (from == 1) return rot.getEuler();
		else return scale;
	}
}
