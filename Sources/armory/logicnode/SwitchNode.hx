package armory.logicnode;

class SwitchNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var v1:Dynamic = inputs[1].get();
		if (inputs.length > 2) {
			for(i in 2...inputs.length) {
				if (inputs[i].get() == v1) {
					runOutputs(i - 1);
					return;
				}
			}
		}

		runOutputs(0);
	}
}
