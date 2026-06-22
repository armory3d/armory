package armory.logicnode;

import iron.object.MeshObject;
import iron.object.CameraObject;

class SetCameraRenderFilterNode extends LogicNode {

	public var property0: String;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var mo: MeshObject = cast inputs[1].get();
		var camera: CameraObject = inputs[2].get();
		
		assert(Error, Std.isOfType(camera, CameraObject), "Camera must be a camera object!");
		
		if (camera == null || mo == null) return;
		
		if (property0 == 'Add'){
			if (mo.cameraList == null || mo.cameraList.indexOf(camera.name) == -1){
				if (mo.cameraList == null) mo.cameraList = [];
				mo.cameraList.push(camera.name);
			}
		}
		else{
			if (mo.cameraList != null){
				mo.cameraList.remove(camera.name);
				if (mo.cameraList.length == 0)
					mo.cameraList = null;
			}
		}

		runOutput(0);
	}
}
