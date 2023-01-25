package armory.logicnode;

class LoopContinueNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		tree.loopContinue = true;
	}
}