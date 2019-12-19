package armory.logicnode;

class SplitStringNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var s1: String = inputs[0].get();
		var s2: String = inputs[1].get();
		if (s1 == null || s2 == null) return null;

        return s1.split(s2);
	}
}
