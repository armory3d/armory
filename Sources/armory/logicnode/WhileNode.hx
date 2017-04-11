package armory.logicnode;

class WhileNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var b:Bool = inputs[1].get();
		while (b) {
			runOutputs(0);
			b = inputs[1].get();

			if (tree.loopBreak) {
				tree.loopBreak = false;
				break;
			}
		}
		runOutputs(1);
	}
}
