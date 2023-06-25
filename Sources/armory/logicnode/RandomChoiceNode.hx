package armory.logicnode;

class RandomChoiceNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var array: Array<Dynamic> = inputs[0].get();

		return array[Std.random(array.length)];
	}
}
