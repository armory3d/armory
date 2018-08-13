package armory.logicnode;

import iron.math.Vec4;

class LerpVectorsNode extends LogicNode {

	var v = new Vec4();

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var v1:Vec4 = inputs[1].get();
		var v2:Vec4 = inputs[2].get();
		var t:Float = inputs[3].get();
		v = Vec4.lerp(v1,v2,t);
		runOutputs(0);
	}
	override function get(from:Int):Dynamic {
		return v;
	}
}
