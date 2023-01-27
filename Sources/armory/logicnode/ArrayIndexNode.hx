package armory.logicnode;

class ArrayIndexNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var array: Array<Dynamic> = inputs[0].get();
		var value: Dynamic = inputs[1].get();

		return array.indexOf(value);
	}
}
