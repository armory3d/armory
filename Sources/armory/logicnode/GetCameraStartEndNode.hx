package armory.logicnode;

import iron.object.CameraObject;

class SetCameraStartEndNode extends LogicNode {

	public var property0: String;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var camera: CameraObject = inputs[1].get();
		
		if (camera == null) return;
		
		if (property0 == 'Start'){
			var start: Float = inputs[2].get();
			camera.data.raw.near_plane = start;
		}
		else if (property0 == 'End' ){
			var end: Float = inputs[2].get();
			camera.data.raw.far_plane = end;
		}
		else {
		
		var start: Float = inputs[2].get();
		camera.data.raw.near_plane = start;
		var end: Float = inputs[3].get();
		camera.data.raw.far_plane = end;
		
		}
				
		camera.buildProjection();

		runOutput(0);
	}
}
