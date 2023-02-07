package armory.logicnode;

import iron.object.CameraObject;

class SetCameraAspectNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var camera: CameraObject = inputs[1].get();
		var aspect: Float = inputs[2].get();

		if (camera == null) return;

		camera.data.raw.aspect = aspect;
		camera.buildProjection();

		runOutput(0);
	}
}
