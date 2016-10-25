package armory.logicnode;

import armory.trait.internal.NodeExecutor;

class GreaterThanNode extends BoolNode {

	public static inline var _value1 = 0; // Float
	public static inline var _value2 = 1; // Float

	public function new() {
		super();
	}

	public override function inputChanged() {
		b = inputs[_value1].f > inputs[_value2].f;
		super.inputChanged();
	}

	public static function create(value1:Float, value2:Float):GreaterThanNode {
		var n = new GreaterThanNode();
		n.inputs.push(FloatNode.create(value1));
		n.inputs.push(FloatNode.create(value2));
		return n;
	}
}
