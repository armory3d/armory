package armory.logicnode;

import iron.object.CameraObject;

class GetCameraStartEndNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var camera: CameraObject = inputs[0].get();

		if (camera == null) return null;
		
		return from == 0 ? camera.data.raw.near_plane : camera.data.raw.far_plane;
	}
}
