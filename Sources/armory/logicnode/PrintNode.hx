package armory.logicnode;

class PrintNode extends Node {

	public function new(trait:armory.Trait) {
		super(trait);
	}

	override function run() {
		var value = inputs[1].get();
	
		trace(value);

		super.run();
	}
}
