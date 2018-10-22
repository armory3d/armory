package armory.logicnode;

class AlternateNode extends LogicNode {

	var b = true;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		b ? runOutput(0) : runOutput(1);
		b = !b;
	}
}
