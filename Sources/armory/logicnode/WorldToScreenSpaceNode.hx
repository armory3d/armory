package armory.logicnode;

import iron.math.Vec4;

class WorldToScreenSpaceNode extends LogicNode {

	public var property0:String;
	var v = new Vec4();

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var v1:Vec4 = inputs[0].get();
		if (v1 == null) return null;

		var cam = iron.Scene.active.camera;
		v.setFrom(v1);
		v.applyproj(cam.V);
		v.applyproj(cam.P);

		return v;
	}
}
