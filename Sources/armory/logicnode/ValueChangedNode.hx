package armory.logicnode;

class ValueChangedNode extends LogicNode {

	var initial: Dynamic;
	var value: Dynamic;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		if (initial == null) {
			initial = inputs[1].get();
			value = initial;
		}

		else if (value != inputs[1].get()) {
			value = inputs[1].get();
			value != initial ? runOutput(0) : runOutput(1);
		}

	}

}
