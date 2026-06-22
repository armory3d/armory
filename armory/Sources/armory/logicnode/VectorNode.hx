package armory.logicnode;

import iron.math.Vec4;

class VectorNode extends LogicNode {

	var value = new Vec4();

	public function new(tree: LogicTree, x: Null<Float> = null, y: Null<Float> = null, z: Null<Float> = null) {
		super(tree);

		if (x != null) {
			LogicNode.addLink(new FloatNode(tree, x), this, 0, 0);
			LogicNode.addLink(new FloatNode(tree, y), this, 0, 1);
			LogicNode.addLink(new FloatNode(tree, z), this, 0, 2);
		}
	}

	override function get(from: Int): Dynamic {
		value = new Vec4();
		value.x = inputs[0].get();
		value.y = inputs[1].get();
		value.z = inputs[2].get();
		return value;
	}

	override function set(value: Dynamic) {
		inputs[0].set(value.x);
		inputs[1].set(value.y);
		inputs[2].set(value.z);
	}
}
