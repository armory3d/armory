package armory.logicnode;

import iron.object.CameraObject;

class GetCameraScaleNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var camera: CameraObject = inputs[0].get();

		if (camera == null) return null;

		return camera.data.raw.ortho[1]*2;
	}
}
