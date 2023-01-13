package armory.logicnode;

class ArrayReverseNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var ar: Array<Dynamic> = inputs[0].get();
		
		var arr = ar.copy();
		
		arr.reverse();

		return arr;
		
	}
}
