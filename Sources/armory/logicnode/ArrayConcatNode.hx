package armory.logicnode;

class ArrayConcatNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var ar1: Array<Dynamic> = inputs[0].get();
		var ar2: Array<Dynamic> = inputs[1].get();

		return ar1.concat(ar2);
		
	}
}
