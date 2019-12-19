package armory.logicnode;

class LengthStringNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var s: String = inputs[0].get();
		if (s == null) return null;

        return s.length;
	}
}
