package armory.logicnode;

class ArrayLoopNode extends LogicNode {

	var value:Dynamic;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var ar:Array<Dynamic> = inputs[1].get();
		if (ar == null) return;

		for (val in ar) {
			value = val;
			runOutputs(0);
		}
		runOutputs(2);
	}

	override function get(from:Int):Dynamic {
		return value;
	}
}
