package armory.logicnode;

class MergeNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		runOutput(0);
	}
}
