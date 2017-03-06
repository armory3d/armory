package armory.logicnode;

import armory.math.Vec4;

class VectorNode extends Node {

	var value = new Vec4();

	public function new(trait:armory.Trait, x:Null<Float> = null, y:Null<Float> = null, z:Null<Float> = null) {
		super(trait);

		if (x != null) {
			addInput(new FloatNode(trait, x));
			addInput(new FloatNode(trait, y));
			addInput(new FloatNode(trait, z));
		}
	}

	override function get():Dynamic {
		value.x = inputs[0].get();
		value.y = inputs[1].get();
		value.z = inputs[2].get();
		return value;
	}
}
