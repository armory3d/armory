package armory.logicnode;

import iron.math.Quat;

class QuaternionNode extends LogicNode {

	var value = new Quat();

	public function new(tree:LogicTree, x:Null<Float> = null, y:Null<Float> = null, z:Null<Float> = null, w:Null<Float> = null) {
		super(tree);

		if (x != null) {
			addInput(new FloatNode(tree, x), 0);
			addInput(new FloatNode(tree, y), 0);
			addInput(new FloatNode(tree, z), 0);
			addInput(new FloatNode(tree, w), 0);
		}
	}

	override function get(from:Int):Dynamic {
		value.x = inputs[0].get();
		value.y = inputs[1].get();
		value.z = inputs[2].get();
		value.w = inputs[3].get();
		return value;
	}

	override function set(value:Dynamic) {
		this.value = value;
	}
}
