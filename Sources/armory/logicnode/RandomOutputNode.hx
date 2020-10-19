package armory.logicnode;

class RandomOutputNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		runOutput(Std.random(outputs.length));
	}
}
