package armory.logicnode;

class RandomIntegerNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var min: Int = inputs[0].get();
		var max: Int = inputs[1].get();
		return min + Std.random(max - min);
	}
}
