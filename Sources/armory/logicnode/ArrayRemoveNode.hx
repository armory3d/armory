package armory.logicnode;

class ArrayRemoveNode extends LogicNode {

 	var removedValue: Dynamic = null;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var ar: Array<Dynamic> = inputs[1].get();
		if (ar == null) return;

		var i: Int = inputs[2].get();
		if (i < 0) i = ar.length + i;

		removedValue = ar[i];
		ar.splice(i, 1);

		runOutput(0);
	}

	override function get(from: Int): Dynamic {
		return removedValue;
	}
}
