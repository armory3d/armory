package armory.logicnode;

class WindowInfoNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		if (from == 0) return kha.System.windowWidth();
		else return kha.System.windowHeight();
	}
}
