package armory.logicnode;

class SubStringNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
        var string: String = inputs[0].get();
		var start: Int = inputs[1].get();
		var end: Int = inputs[2].get();
		if (string == null) return null;

        return string.substring(start, end);
	}
}
