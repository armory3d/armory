package armory.logicnode;

import iron.math.Vec4;
import iron.math.Mat4;

class ScreenToWorldSpaceNode extends LogicNode {

	public var property0:String;
	var v = new Vec4();
	var m = Mat4.identity();

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var v1:Vec4 = inputs[0].get();

		if (v1 == null) return null;

		var cam = iron.Scene.active.camera;
		v.setFrom(v1);
		m.getInverse(cam.P);
		v.applyproj(m);
		m.getInverse(cam.V);
		v.applyproj(m);

		return v;
	}
}
