package armory.logicnode;

class ArrayLoopNode extends LogicNode {

	var value: Dynamic;
	var index: Int;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var ar: Array<Dynamic> = inputs[1].get();
		if (ar == null) return;

		index = -1;
		for (val in ar) {
			value = val;
			index++;
			runOutput(0);

			if (tree.loopBreak) {
				tree.loopBreak = false;
				break;
			}
			
			if (tree.loopContinue) {
				tree.loopContinue = false;
				continue;
			}
		}
		runOutput(3);
	}

	override function get(from: Int): Dynamic {
		if (from == 1)
			return value;
		return index;
	}
}
