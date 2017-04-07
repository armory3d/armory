package armory.logicnode;

import armory.math.Vec4;

class SeparateColorNode extends Node {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var vector:Vec4 = inputs[0].get();

		if (from == 0) vector.x;
		else if (from == 1) vector.y;
		else vector.z;
	}
}
