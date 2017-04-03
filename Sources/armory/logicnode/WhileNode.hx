package armory.logicnode;

class WhileNode extends Node {

	public function new(trait:armory.Trait) {
		super(trait);
	}

	override function run() {
		var b = inputs[1].get();
		while (b) {
			runOutputs(0);
			b = inputs[1].get();
		}
		runOutputs(1);
	}
}
