package armory.logicnode;

class ToBoolNode extends LogicNode {

	var value: Bool;
	var b = false;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		b = true;
	}

	override function get(from: Int): Dynamic {
		value = b;
		b = false;
		return value;
	}
}
