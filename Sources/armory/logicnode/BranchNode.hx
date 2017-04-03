package armory.logicnode;

class BranchNode extends Node {

	public function new(trait:armory.Trait) {
		super(trait);
	}

	override function run() {

		var b = inputs[1].get();
		b ? runOutputs(0) : runOutputs(1);
	}
}
