package armory.logicnode;

import kha.FastFloat;

class KeyInterpolateNode extends LogicNode {

	var value: FastFloat = 0.0;

	public function new(tree: LogicTree) {
		super(tree);
		tree.notifyOnInit(init);
		tree.notifyOnUpdate(update);
	}

	function init() {
		value = clamp(inputs[1].get());
	}

	function update() {
		var sign = inputs[0].get() ? 1.0 : -1.0;
		var rate: FastFloat = inputs[2].get();
		value = clamp(value + rate * sign);
	}

	override function get(from: Int): FastFloat {
		return value;
	}

	inline function clamp(value: FastFloat): FastFloat {
		return value < 0.0 ? 0.0 : value > 1.0 ? 1.0 : value;
	}
}
