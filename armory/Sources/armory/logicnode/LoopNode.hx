package armory.logicnode;

class LoopNode extends LogicNode {

	var index: Int;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		index = 0;
		var from: Int = inputs[1].get();
		var to: Int = inputs[2].get();
		for (i in from...to) {
			index = i;
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
		runOutput(2);
	}

	override function get(from: Int): Dynamic {
		return index;
	}
}
