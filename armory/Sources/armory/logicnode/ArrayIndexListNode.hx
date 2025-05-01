package armory.logicnode;

class ArrayIndexListNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var array: Array<Dynamic> = inputs[0].get();
		array = array.map(item -> Std.string(item));
		var value: Dynamic = inputs[1].get();
		var from: Int = 0;

		var arrayList: Array<Int> = [];

		var index: Int = array.indexOf(Std.string(value), from);

		while(index != -1){
			arrayList.push(index);
			index = array.indexOf(Std.string(value), index+1);
		}

		return arrayList;
	}
}
