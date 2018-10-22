package armory.logicnode;

class PrintNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		var value:Dynamic = inputs[1].get();
	
		trace(value);

		runOutput(0);
	}
}
