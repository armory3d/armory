package armory.logicnode;

class ArraySpliceNode extends LogicNode {

	var splice: Array<Dynamic>;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var ar: Array<Dynamic> = inputs[1].get();
		if (ar == null) return;

		var i = inputs[2].get();
		var len = inputs[3].get();

		splice = ar.splice(i, len);

		runOutput(0);
	}

	override function get(from: Int): Dynamic {

		return splice;

	}
}
