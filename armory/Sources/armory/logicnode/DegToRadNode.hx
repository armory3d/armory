package armory.logicnode;

class DegToRadNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var deg: Float = inputs[0].get();
		return deg * 0.0174532924;
	}
}
