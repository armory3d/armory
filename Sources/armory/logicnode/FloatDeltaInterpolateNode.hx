package armory.logicnode;

import kha.FastFloat;

class FloatDeltaInterpolateNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
		
	}

	override function get(from: Int): FastFloat {
		var fromValue = inputs[0].get();
		var toValue = inputs[1].get();
		var deltaTime = inputs[2].get();
		var rate = inputs[3].get();
		
		var sign = toValue > fromValue ? 1.0 : -1.0;
		var value = fromValue + deltaTime * rate * sign;
		var min = Math.min(fromValue, toValue);
		var max = Math.max(fromValue, toValue);
		return value < min ? min : value > max ? max : value;
	}
}
