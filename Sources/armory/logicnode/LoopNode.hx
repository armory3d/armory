package armory.logicnode;

class LoopNode extends LogicNode {

	var index:Int;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		index = 0;
		var from:Int = inputs[1].get();
		var to:Int = inputs[2].get();
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
