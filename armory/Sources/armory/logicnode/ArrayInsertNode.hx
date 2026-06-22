package armory.logicnode;

class ArrayInsertNode extends LogicNode {

	var ar: Array<Dynamic>;
	
	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		ar = inputs[1].get();
		var index: Int = inputs[2].get();
		var value: Dynamic = inputs[3].get();
		
		if (ar == null || value == null) return;

		ar.insert(index, value);

		runOutput(0);
	}

	override function get(from: Int): Dynamic {
		return ar;
	}
}
