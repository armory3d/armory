package armory.logicnode;

import iron.math.Vec4;

class CombineColorNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var r = inputs[0].get();
		var g = inputs[1].get();
		var b = inputs[2].get();
		var a = inputs[3].get();

		return new Vec4(
			r == null ? 0.0 : r,
			g == null ? 0.0 : g,
			b == null ? 0.0 : b,
			a == null ? 0.0 : a
		);
	}
}
