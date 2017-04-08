package armory.logicnode;

import armory.math.Vec4;

class RandomVectorNode extends LogicNode {

	var v = new Vec4();

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var min:Float = inputs[0].get();
		var max:Float = inputs[1].get();
		var x = min + (Math.random() * (max - min));
		var y = min + (Math.random() * (max - min));
		var z = min + (Math.random() * (max - min));
		v.set(x, y, z);
		return v;
	}
}
