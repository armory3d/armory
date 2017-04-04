package armory.logicnode;

class ArraySetNode extends Node {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var ar:Array<Dynamic> = inputs[1].get();
		var i:Int = inputs[2].get();
		var value:Dynamic = inputs[3].get();
		ar[i] = value;

		super.run();
	}
}
