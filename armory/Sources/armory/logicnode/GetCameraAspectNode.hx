package armory.logicnode;

import iron.object.CameraObject;

class GetCameraAspectNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var camera: CameraObject = inputs[0].get();

		if (camera == null) return null;

		return camera.data.raw.aspect != null ? camera.data.raw.aspect : iron.App.w() / iron.App.h();
	}
}
