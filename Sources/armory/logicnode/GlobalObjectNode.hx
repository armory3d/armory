package armory.logicnode;

class GlobalObjectNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic { 
		return iron.Scene.global;
	}
}
