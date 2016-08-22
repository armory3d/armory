package armory.logicnode;

class SineNode extends FloatNode {

	public static inline var _value = 0; // Float

	public function new() {
		super();
	}

	public override function inputChanged() {
		f = Math.sin(inputs[_value].f);

		super.inputChanged();
	}

	public static function create(value:Float) {
		var n = new SineNode();
		n.inputs.push(FloatNode.create(value));
		return n;
	}
}
