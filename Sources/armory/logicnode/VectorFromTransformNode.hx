package armory.logicnode;

import armory.math.Mat4;

class VectorFromTransformNode extends LogicNode {

	public var property0:String;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var m:Mat4 = inputs[0].get();

		switch (property0) {
		case "Up":
			return m.up();
		case "Right":
			return m.right();
		case "Look":
			return m.look();
		case "Quaternion":
			return m.getQuat();
		}

		return null;
	}
}
