package armory.logicnode;

class AlternateNode extends LogicNode {

	var b = true;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		b ? runOutputs(0) : runOutputs(1);
		b = !b;
	}
}
