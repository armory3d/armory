package armory.logicnode;

class OnUpdateNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);

		tree.notifyOnUpdate(update);
	}

	function update() {
		runOutput(0);
	}
}
