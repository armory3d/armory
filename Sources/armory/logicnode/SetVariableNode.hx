package armory.logicnode;

class SetVariableNode extends Node {

	public function new(trait:armory.Trait) {
		super(trait);
	}

	override function run() {
		var variable = inputs[1];
		var value = inputs[2].get();

		variable.set(value);

		super.run();
	}
}
