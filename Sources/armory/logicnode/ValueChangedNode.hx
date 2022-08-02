package armory.logicnode;

class ValueChangedNode extends LogicNode {

	var initialized = false;
	var initialValue: Dynamic;
	var lastValue: Dynamic;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var currentValue = inputs[1].get();

		if (!initialized) {
			initialValue = currentValue;
			lastValue = initialValue;
			initialized = true;
			runOutput(0);
			runOutput(2);
			return;
		}

		if (currentValue == lastValue) {
			runOutput(1);
		}
		else {
			lastValue = currentValue;
			runOutput(0);
		}

		if (currentValue == initialValue) {
			runOutput(2);
		}
	}
}
