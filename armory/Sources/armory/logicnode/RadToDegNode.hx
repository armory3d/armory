package armory.logicnode;

class RadToDegNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var rad: Float = inputs[0].get();
		return rad * 57.29578;
	}
}
