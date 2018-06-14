package armory.logicnode;

import iron.math.Vec4;

class VectorClampToSizeNode extends LogicNode {

	var v = new Vec4();

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		v = inputs[0].get();
		var fmin:kha.FastFloat = inputs[1].get();
		var fmax:kha.FastFloat = inputs[2].get();

		v.clamp(fmin, fmax);
		
		return v;
	}
}
