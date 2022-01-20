package armory.logicnode;

class ArraySampleNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var ar: Array<Dynamic> = inputs[0].get();
		var sample = inputs[1].get();
		var remove = inputs[2].get();
		
		if (ar == null || sample == 0) return null;

		var n = Std.int(Math.min(sample, ar.length));
		var copy = remove ? ar : ar.copy(), result = [];
		for (i in 0...n)
			result.push(copy.splice(Std.random(copy.length), 1)[0]);
		
		return result;
	}
}
