package armory.logicnode;

class IntFromBooleanNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {

		var bool = inputs[0].get();
		
		return bool ? 1 : 0;
		
	}
}
