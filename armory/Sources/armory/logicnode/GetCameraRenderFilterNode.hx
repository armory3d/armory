package armory.logicnode;

import iron.object.MeshObject;
import iron.object.CameraObject;

class GetCameraRenderFilterNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var mo: MeshObject = cast inputs[0].get();

		if (mo == null) return null;
		
		return mo.cameraList;
	}
}
