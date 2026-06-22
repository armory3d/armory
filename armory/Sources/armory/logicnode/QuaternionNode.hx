package armory.logicnode;

import iron.math.Quat;
import iron.math.Vec4;

class QuaternionNode extends LogicNode {

	var value = new Quat();

	public function new(tree: LogicTree, x: Null<Float> = null, y: Null<Float> = null, z: Null<Float> = null, w: Null<Float> = null) {
		super(tree);

		if (x != null) {
			LogicNode.addLink(new FloatNode(tree, x), this, 0, 0);
			LogicNode.addLink(new FloatNode(tree, y), this, 0, 1);
			LogicNode.addLink(new FloatNode(tree, z), this, 0, 2);
			LogicNode.addLink(new FloatNode(tree, w), this, 0, 3);
		}
	}

	override function get(from: Int): Dynamic {
		value.x = inputs[0].get();
		value.y = inputs[1].get();
		value.z = inputs[2].get();
		value.w = inputs[3].get();
		value.normalize();
		switch (from){
		case 0:
			return value;
		case 1:
			var value1 = new Vec4();
			value1.x = value.x;
			value1.y = value.y;
			value1.z = value.z;
			value1.w = 0; // use 0 to avoid this vector being translated.
			return value1;
		case 2:
			return value.w;
		default:
			return null;
		}
	}

	override function set(value: Dynamic) {
		this.value = value;
	}
}
