package armory.logicnode;

class ArrayAddNode extends LogicNode {

	var ar: Array<Dynamic>;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		ar = inputs[1].get();
		if (ar == null) return;

		// "Modify Original" == `false` -> Copy the input array
		if (!inputs[2].get()) {
			ar = ar.copy();
		}

		if (inputs.length > 4) {
			for (i in 4...inputs.length) {
				var value: Dynamic = inputs[i].get();

				// "Unique Values" options only supports primitive data types
				// for now, a custom indexOf() or contains() method would be
				// required to compare values of other types
				if (!inputs[3].get() || ar.indexOf(value) == -1) {
					ar.push(value);
				}
			}
		}

		runOutput(0);
	}

	override function get(from: Int): Dynamic {
		return ar;
	}
}
