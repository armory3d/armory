package armory.logicnode;

import iron.math.Vec4;
import iron.math.RayCaster;
import iron.object.Object;
import iron.object.CameraObject;

class RaycastClosestObjectNode extends LogicNode {

	var o: Object;
	var v = new Vec4();

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var objects: Array<Object> = inputs[1].get();
		var inputX: Float = inputs[2].get();
		var inputY: Float = inputs[3].get();
		var camera: CameraObject = inputs[4].get();
		// Older node trees may not have the `Exact Mesh` socket yet
		var exactMesh: Bool = inputs.length > 5 && inputs[5] != null && inputs[5].get() == true;

		o = RayCaster.closestObbIntersectObject(objects, inputX, inputY, camera, exactMesh);
		v = o != null ? RayCaster.lastHit : null;

		if (o == null) runOutput(2); else runOutput(1);
		
		runOutput(0);
	}
	
	override function get(from: Int): Dynamic {
		switch (from) {
			case 3: return o;
			case 4: if(o == null) return null; else return v;
		}
		return null;
	}
}