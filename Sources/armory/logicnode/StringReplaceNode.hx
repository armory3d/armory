package armory.logicnode;

class StringReplaceNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
        var string: String = inputs[0].get();
		var find: String = inputs[1].get();
		var replace: String = inputs[2].get();
		if (find == null || replace == null || string == null) return null;

        return StringTools.replace(string, find, replace);
	}
}
