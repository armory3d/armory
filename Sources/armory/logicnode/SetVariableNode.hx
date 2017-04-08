package armory.logicnode;

class SetVariableNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var variable = inputs[1];
		var value:Dynamic = inputs[2].get();

		variable.set(value);

		super.run();
	}
}
