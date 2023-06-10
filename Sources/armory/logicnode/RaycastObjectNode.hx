package armory.logicnode;

import iron.math.Vec4;
import iron.math.RayCaster;
import iron.object.Object;
import iron.object.CameraObject;

class RaycastObjectNode extends LogicNode {

	var v = new Vec4();

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var o: Object = inputs[1].get();
		var inputX: Float = inputs[2].get();
		var inputY: Float = inputs[3].get();
		var camera: CameraObject = inputs[4].get();

		v = RayCaster.boxIntersectObject(o, inputX, inputY, camera);

		if (v == null) runOutput(2); else runOutput(1);
		
		runOutput(0);
	}
	
	override function get(from: Int): Dynamic {
		return v;
	}
}