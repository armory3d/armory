package armory.logicnode;

class ArrayGetNextNode extends LogicNode {

	var i = 0;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var ar: Array<Dynamic> = inputs[0].get();

		if (ar == null) return null;
		
		var value = ar[i];
		
		if (i < ar.length - 1)
			i++;
		else 
			i = 0;
		
		return value;
		
	}
}
