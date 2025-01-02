package armory.logicnode;

class IsTrueNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var v1: Bool = inputs[1].get();
		if (v1) runOutput(0);
	}
}
