package armory.logicnode;

class DefaultIfNullNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var v1 = inputs[0].get();
		var v2 = inputs[1].get();

		v1 != null ? return v1 : return v2;
	}

}
