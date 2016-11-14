package armory.logicnode;

class ScaleValueNode extends FloatNode {

	public static inline var _factor = 0; // Float
	public static inline var _value = 1; // Float

	public function new() {
		super();
	}

	public override function inputChanged() {
		val = inputs[_value].val * inputs[_factor].val;

		super.inputChanged();
	}

	public static function create(factor:Float, value:Float) {
		var n = new ScaleValueNode();
		n.inputs.push(FloatNode.create(factor));
		n.inputs.push(FloatNode.create(value));
		return n;
	}
}
