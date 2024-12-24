package armory.logicnode;

class SelfTraitNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		return tree;
	}
}
