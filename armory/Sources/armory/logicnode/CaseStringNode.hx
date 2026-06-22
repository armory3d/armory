package armory.logicnode;

class CaseStringNode extends LogicNode {

	public var property0: String;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var s: String = inputs[0].get();
		if (s == null) return null;

		switch (property0) {
		case "Upper Case":
			return s.toUpperCase();
		case "Lower Case":
			return s.toLowerCase();
		}

		return false;
	}
}
