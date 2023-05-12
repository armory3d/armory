package armory.logicnode;

class ActionNameNode extends LogicNode {

	public var value: String;

	public function new(tree: LogicTree, value = "") {
		super(tree);
		this.value = value;
	}

	override function get(from: Int): Dynamic {
		if (inputs.length > 0) return inputs[0].get();
		return value;
	}
}
