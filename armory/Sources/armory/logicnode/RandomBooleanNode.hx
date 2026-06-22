package armory.logicnode;

class RandomBooleanNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		return Std.random(2) == 0;
	}
}
