package armory.logicnode;

class GroupOutputNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {

		runOutput(0);
	}
}
