package armory.logicnode;

class MapRangeNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): kha.FastFloat {
		var value = inputs[0].get();
		var fromMin = inputs[1].get();
		var fromMax = inputs[2].get();
		var toMin = inputs[3].get();
		var toMax = inputs[4].get();

		if (value == null || fromMin == null || fromMax == null || toMin == null || toMax == null) return null;

		//Implements https://stackoverflow.com/a/5732390
		var slope = (toMax - toMin) / (fromMax - fromMin);
		return toMin + slope * (value - fromMin);
	}
}
