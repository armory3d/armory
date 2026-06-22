package armory.logicnode;

class ArrayLengthNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var ar: Array<Dynamic> = inputs[0].get();
		return ar != null ? ar.length : 0;
	}
}
