package armory.logicnode;

class FunctionOutputNode extends LogicNode {

	@:allow(armory.logicnode.LogicTree)
	var result: Dynamic;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		this.result = inputs[1].get();
		runOutput(0);
	}
}
