package armory.logicnode;

class ConcatenateStringNode extends LogicNode {

	public var value: String;

	public function new(tree: LogicTree, value = "") {
		super(tree);
		this.value = value;
	}

	override function get(from: Int): Dynamic {
		value = "";
		for (inp in inputs) value += inp.get();
		return value;
	}
}
