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

		o = RayCaster.closestBoxIntersectObject(objects, inputX, inputY, camera);
		if (o != null)
			v = RayCaster.boxIntersectObject(o, inputX, inputY, camera);

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