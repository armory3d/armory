package armory.logicnode;

import iron.math.Vec4;
import iron.math.Vec2;
import iron.App;
import iron.object.CameraObject;

class WorldToScreenSpaceNode extends LogicNode {

	public var property0: String;
	var v = new Vec4();
	var cam: CameraObject;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var v1: Vec4 = inputs[0].get();
		if (v1 == null) return null;

		if(property0 == 'Active Camera') 
			cam = iron.Scene.active.camera;
		else 
			cam = inputs[1].get();
		
		v.setFrom(v1);
		v.applyproj(cam.V);
		v.applyproj(cam.P);
		
		var w = App.w();
		var h = App.h();

		return new Vec2((v.x + 1) * 0.5 * w, (-v.y + 1) * 0.5 * h);
	}
}
