package armory.logicnode;

class ShutdownNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		kha.System.stop();
	}
}
