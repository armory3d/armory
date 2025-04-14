package armory.logicnode;

import iron.object.CameraObject;
import kha.arrays.Float32Array;

class SetCameraTypeNode extends LogicNode {

	public var property0: String;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var camera: CameraObject = inputs[1].get();
		var prop: Float = inputs[2].get();

		if (camera == null) return;

		if (property0 == 'Perspective'){
			camera.data.raw.ortho = null;
			camera.data.raw.fov = prop;
			camera.data.raw.near_plane = inputs[3].get();
			camera.data.raw.far_plane = inputs[4].get();
		}
		else {
			var aspect = camera.data.raw.aspect != null ? camera.data.raw.aspect : iron.App.w() / iron.App.h();
			camera.data.raw.fov = null;
			var ortho = new Float32Array(4);
			ortho[0] = - prop / 2;
			ortho[1] = prop / 2;
			ortho[2] = - prop / (2 * aspect);
			ortho[3] = prop / (2 * aspect);
			camera.data.raw.ortho = ortho;
			camera.data.raw.near_plane = - camera.data.raw.far_plane;
		}

		camera.buildProjection();

		runOutput(0);
	}
}