package armory.logicnode;

import iron.object.CameraObject;

class SetCameraNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var camera: CameraObject = inputs[1].get();
		if (camera == null) return;
		camera.buildProjection();

		iron.Scene.active.camera = camera;

		runOutput(0);
	}
}
