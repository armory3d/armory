package armory.logicnode;

class ArrayLoopNode extends LogicNode {

	var value:Dynamic;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		var ar:Array<Dynamic> = inputs[1].get();
		if (ar == null) return;

		for (val in ar) {
			value = val;
			runOutput(0);

			if (tree.loopBreak) {
				tree.loopBreak = false;
				break;
			}
		}
		runOutput(2);
	}

	override function get(from:Int):Dynamic {
		return value;
	}
}
