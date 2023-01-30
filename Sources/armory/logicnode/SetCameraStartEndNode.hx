package armory.logicnode;

import iron.object.CameraObject;

class SetCameraStartEndNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var camera: CameraObject = inputs[1].get();
		var start: Float = inputs[2].get();
		var end: Float = inputs[3].get();

		if (camera == null) return;

		camera.data.raw.near_plane = start;
		camera.data.raw.far_plane = end;
		
		camera.buildProjection();

		runOutput(0);
	}
}
