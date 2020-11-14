package armory.logicnode;

class MapRangeNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var value: kha.FastFloat = inputs[0].get();
		var fromMin: kha.FastFloat = inputs[1].get();
		var fromMax: kha.FastFloat = inputs[2].get();
		var toMin: kha.FastFloat = inputs[3].get();
		var toMax: kha.FastFloat = inputs[4].get();

		if (value == null || fromMin == null || fromMax == null || toMin == null || toMax == null) return null;

		return (value / fromMax - fromMin) * toMax - toMin;
	}
}
