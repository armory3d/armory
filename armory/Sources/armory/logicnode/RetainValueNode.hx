package armory.logicnode;

class RetainValueNode extends LogicNode {

	var value: Dynamic = null;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		value = inputs[1].get();

		runOutput(0);
	}

	override function get(from:Int):Dynamic {
		return value;
	}
}
