package armory.logicnode;

class SelectNode extends LogicNode {

	/** Execution mode. **/
	public var property0: String;

	var value: Dynamic = null;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		// Get value according to the activated input (run() can only be called
		// if the execution mode is from_input).
		value = inputs[from + Std.int(inputs.length / 2)].get();

		runOutput(0);
	}

	override function get(from: Int): Dynamic {
		if (property0 == "from_index") {
			var index = inputs[0].get() == null ? -1 : inputs[0].get() + 2;

			// Return default value for invalid index
			if (index < 2 || index >= inputs.length) {
				return inputs[1].get();
			}

			return inputs[index].get();
		}

		// from_input
		return value;
	}
}
