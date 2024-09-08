package armory.logicnode;

class AnimTreeNode extends LogicNode {

	public var value: Dynamic;

	public function new(tree: LogicTree, value: Dynamic = null) {
		super(tree);
		this.value = value == null ? {} : value;
	}

	override function get(from: Int): Dynamic {
		return value;
	}

	override function set(value: Dynamic) {
		this.value = value;
	}
}
