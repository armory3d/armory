package armory.logicnode;

class ArrayGetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var ar:Array<Dynamic> = inputs[0].get();
		var i:Int = inputs[1].get();
		return ar[i];
	}
}
