package armory.logicnode;

class GroupOutputNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		trace("output called");
		runOutput(from);
	}

	override function get(from: Int): Dynamic {
		return inputs[from].get();
	}
}
