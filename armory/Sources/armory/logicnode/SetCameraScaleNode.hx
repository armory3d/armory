package armory.logicnode;

import iron.object.CameraObject;
import kha.arrays.Float32Array;

class SetCameraScaleNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var camera: CameraObject = inputs[1].get();
		var scale: Float = inputs[2].get();

		if (camera == null) return;

		var aspect = camera.data.raw.aspect != null ? camera.data.raw.aspect : iron.App.w() / iron.App.h();
		var ortho = new Float32Array(4);
		ortho[0] = - scale / 2;
		ortho[1] = scale / 2;
		ortho[2] = - scale / (2 * aspect);
		ortho[3] = scale / (2 * aspect);
		camera.data.raw.ortho = ortho;

		camera.buildProjection();

		runOutput(0);
	}
}
