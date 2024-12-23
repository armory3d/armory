package armory.logicnode;

import iron.math.Vec4;

class SeparateColorNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var vector: Vec4 = inputs[0].get();
		if (vector == null) return 0.0;

		return switch (from) {
			case 0: vector.x;
			case 1: vector.y;
			case 2: vector.z;
			case 3: vector.w;
			default: throw "Unreachable";
		}
	}
}
