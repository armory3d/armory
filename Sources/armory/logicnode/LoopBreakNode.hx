package armory.logicnode;

class LoopBreakNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(node:LogicNode) {
		tree.loopBreak = true;
	}
}
