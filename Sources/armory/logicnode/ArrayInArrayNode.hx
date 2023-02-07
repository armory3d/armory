package armory.logicnode;

class ArrayInArrayNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var array: Array<Dynamic> = inputs[0].get();
		array = array.map(item -> Std.string(item));
		var value: Dynamic = inputs[1].get();

		return array.indexOf(Std.string(value)) != -1;
	}
}
