package armory.logicnode;

import iron.math.Quat;
import iron.math.Mat4;
import iron.math.Vec4;

class VectorFromTransformNode extends LogicNode {

	public var property0: String;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var m: Mat4 = inputs[0].get();

		if (m == null) return null;

		switch(from) {
		case 0:
			switch (property0) {
			case "Up":
				return m.up();
			case "Right":
				return m.right();
			case "Look":
				return m.look();
			case "Quaternion":
				var q = new Quat();
				q.fromMat(m);
				return q.normalize();
			}
		case 1:
			if (property0 == "Quaternion") {
				var q = new Quat();
				q.fromMat(m);
				q.normalize();
				var v = new Vec4();
				v.x = q.x; v.y = q.y; v.z = q.z;
				v.w = 0;  //prevent vector translation
				return v;
			}
		case 2:
			if (property0 == "Quaternion") {
				var q = new Quat();
				q.fromMat(m);
				q.normalize();
				return q.w;
			}
		}

		return null;
	}
}
