package armory.logicnode;

class ArrayDistinctNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var ar: Array<Dynamic> = inputs[0].get();

		var ar_list: Array<Dynamic> = [];
		var distinct: Array<Dynamic> = [];
		var duplicated: Array<Dynamic> = [];
		
		for(item in ar)
			if(ar_list.indexOf(Std.string(item)) == -1){
				ar_list.push(Std.string(item));
				distinct.push(item);
			}
			else
				duplicated.push(item);		

		return from == 0 ? distinct: duplicated;
	
	}
}
