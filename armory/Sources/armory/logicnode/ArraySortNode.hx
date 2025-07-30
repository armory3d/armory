package armory.logicnode;

class ArraySortNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var ar: Array<Dynamic> = inputs[0].get();
		var desc: Bool = inputs[1].get();
		
		var arr = ar.copy(); 
		
		arr.sort(Reflect.compare);
		
		if (desc) arr.reverse();

		return arr;
		
	}
}
