package armory.logicnode;

class ArrayGetPreviousNextNode extends LogicNode {

	var i = 0;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var ar: Array<Dynamic> = inputs[0].get();
		var direction: Bool = inputs[1].get();

		if (ar == null) return null;
		
		if(direction)
			if (i < ar.length - 1)
				i++;
			else 
				i = 0;
		else
			if (i <= 0)
				i = ar.length-1;
			else 
				i--;

		var value = ar[i];
		
		return value;
		
	}
}
