package armory.logicnode;

class LoopNode extends Node {

	var index:Int;

	public function new(trait:armory.Trait) {
		super(trait);
	}

	override function run() {
		index = 0;
		var from = inputs[1].get();
		var to = inputs[2].get();
		for (i in from...to) {
			index = i;
			runOutputs(0);
		}
		runOutputs(2);
	}

	override function get(from:Int):Dynamic {
		return index;
	}
}
