package armory.logicnode;

class ArrayPopNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var ar: Array<Dynamic> = inputs[0].get();
		if (ar == null) return null;

		return ar.pop();
	}
}
