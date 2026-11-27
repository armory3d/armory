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
		// Older node trees may not have the `Exact Mesh` socket yet
		var exactMesh: Bool = inputs.length > 5 && inputs[5] != null && inputs[5].get() == true;

		v = RayCaster.obbIntersectObject(o, inputX, inputY, camera, exactMesh);

		if (v == null) runOutput(2); else runOutput(1);
		
		runOutput(0);
	}
	
	override function get(from: Int): Dynamic {
		return v;
	}
}