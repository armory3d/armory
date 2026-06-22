package armory.logicnode;

class ArrayCountNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var ar: Array<Dynamic> = inputs[0].get();

		var values: Array<Dynamic> = [];
		var values_list: Array<Dynamic> = [];
		var count: Array<Int> = [];
		var val_count: Array<Dynamic> = [];
		
		for(item in ar){
			if(values.indexOf(Std.string(item)) == -1){
				values_list.push(item);
				values.push(Std.string(item));
				count.push(1);
			}
			else {
				count[values.indexOf(Std.string(item))] += 1;
			}
		}

		for(i in 0...values_list.length)
			val_count.push([values_list[i], count[i]]);

		return val_count;
	}
}