package armory.logicnode;

class ArrayGetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var ar:Array<Dynamic> = inputs[0].get();
		var i:Int = inputs[1].get();
		if (i < 0) i = ar.length + i;
		if (i < 0 || i > ar.length - 1) {
			trace("Error: Array Get - index out of range");
			return null;
		}
		return ar[i];
	}
}
