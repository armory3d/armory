package armory.logicnode;

import iron.math.Vec4;

class RandomColorNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		
		var r = Math.random();
		var g = Math.random();
		var b = Math.random();
		// var a = Math.random();
		var v = new Vec4(r, g, b);
		return v;
	}
}
