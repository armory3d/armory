package armory.logicnode;

import iron.object.CameraObject;

class SetCameraFovNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var camera: CameraObject = inputs[1].get();
		var fov: Float = inputs[2].get();

		if (camera == null) return;

		camera.data.raw.fov = fov;
		camera.buildProjection();

		runOutput(0);
	}
}
