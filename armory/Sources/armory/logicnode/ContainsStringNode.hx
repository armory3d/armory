package armory.logicnode;

class ContainsStringNode extends LogicNode {

	public var property0: String;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var s1: String = inputs[0].get();
		var s2: String = inputs[1].get();
		if (s1 == null || s2 == null) return null;

		switch (property0) {
		case "Contains":
			return s1.indexOf(s2) >= 0;
		case "Starts With":
			return StringTools.startsWith(s1, s2);
		case "Ends With":
			return StringTools.endsWith(s1, s2);
		}

		return false;
	}
}
