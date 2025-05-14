package armory.logicnode;

class ArrayResizeNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var ar: Array<Dynamic> = inputs[1].get();
		if (ar == null) return;

		var len = inputs[2].get();

		ar.resize(len);

		runOutput(0);
	}
}
