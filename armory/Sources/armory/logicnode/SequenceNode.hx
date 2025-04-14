package armory.logicnode;

class SequenceNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		for (i in 0...outputs.length) runOutput(i);
	}
}
