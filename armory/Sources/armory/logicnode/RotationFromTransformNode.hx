package armory.logicnode;

import iron.math.Mat4;
import iron.math.Vec4;

class RotationFromTransformNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var m: Mat4 = inputs[0].get();

		if (m == null) return null;

		var mr: Mat4 = m.clone().toRotation();

		return switch(from){
			case 0: new Vec4(mr._00, mr._10, mr._20, mr._30);
			case 1: new Vec4(mr._01, mr._11, mr._21, mr._31);
			case 2: new Vec4(mr._02, mr._12, mr._22, mr._32);
			default: null;
		}

	}
}
