package armory.logicnode;

import iron.math.Mat4;

class MatrixMathNode extends LogicNode {

	public var property0: String;
	var m = Mat4.identity();

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var m1: Mat4 = inputs[0].get();
		var m2: Mat4 = inputs[1].get();

		if (m1 == null || m2 == null) return null;

		m.setFrom(m1);
		switch (property0) {
		case "Multiply":
			m.multmat(m2);
		}

		return m;
	}
}
