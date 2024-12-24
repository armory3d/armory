package armory.logicnode;

class WhileNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var b: Bool = inputs[1].get();
		while (b) {
			runOutput(0);
			b = inputs[1].get();

			if (tree.loopBreak) {
				tree.loopBreak = false;
				break;
			}
			
			if (tree.loopContinue) {
				tree.loopContinue = false;
				continue;
			}
			
		}
		runOutput(1);
	}
}
