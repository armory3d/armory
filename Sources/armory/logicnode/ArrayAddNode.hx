package armory.logicnode;

class ArrayAddNode extends LogicNode {

	var ar: Array<Dynamic>;
	var array: Array<Dynamic>;

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

		array = ar.map(item -> Std.string(item));

		if (inputs.length > 4) {
			for (i in 4...inputs.length) {
				var value: Dynamic = inputs[i].get();

				// "Unique Values" options only supports primitive data types
				// for now, a custom indexOf() or contains() method would be
				// required to compare values of other types

				//meanwhile an efficient comparison method is defined, it can be compared as a string representation.
				var type: Bool = value is Bool || value is Float || value is Int || value is String;

				if (!inputs[3].get() || (type ? ar.indexOf(value) : array.indexOf(Std.string(value))) == -1) {
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
