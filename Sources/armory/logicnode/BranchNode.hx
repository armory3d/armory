package armory.logicnode;

class BranchNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var b: Bool = inputs[1].get();
		b ? runOutput(0) : runOutput(1);
	}
}
