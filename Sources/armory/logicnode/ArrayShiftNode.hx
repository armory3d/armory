package armory.logicnode;

class ArrayShiftNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var ar: Array<Dynamic> = inputs[0].get();
		if (ar == null) return null;

		return ar.shift();
	}
}
