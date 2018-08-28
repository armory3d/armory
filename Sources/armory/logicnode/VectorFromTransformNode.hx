package armory.logicnode;

import iron.math.Quat;
import iron.math.Mat4;

class VectorFromTransformNode extends LogicNode {

	public var property0:String;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var m:Mat4 = inputs[0].get();

		if (m == null) return null;

		switch (property0) {
		case "Up":
			return m.up();
		case "Right":
			return m.right();
		case "Look":
			return m.look();
		case "Quaternion":
			var q = new Quat();
			return q.fromMat(m);
		}

		return null;
	}
}
