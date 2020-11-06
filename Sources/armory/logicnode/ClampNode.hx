package armory.logicnode;

class ClampNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var value: kha.FastFloat = inputs[0].get();
		var min: kha.FastFloat = inputs[1].get();
		var max: kha.FastFloat = inputs[2].get();

		if (value == null || min == null || max == null) return null;

		value <= min ? return min : value >= max ? return max : return value;
	}
}
