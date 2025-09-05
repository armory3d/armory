package armory.logicnode;

import iron.math.Quat;
import iron.math.Vec4;
import iron.math.Mat4;

class RetainValueNode extends LogicNode {

	var value: Dynamic = null;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var retainValue = inputs[1].get();

		switch(Type.getClassName(Type.getClass(retainValue))){
			case "iron.math.Vec4":
				value = (cast retainValue: Vec4).clone();
			case "iron.math.Mat4":
				value = (cast retainValue: Mat4).clone();
			case "iron.math.Quat":
				var q: Quat = new Quat();
				value = q.setFrom((cast retainValue: Quat));
			default:
				value = retainValue;
		}

		runOutput(0);
	}

	override function get(from:Int):Dynamic {
		return value;
	}
}