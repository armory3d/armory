package armory.logicnode;

class OnUpdateNode extends Node {

	public function new(tree:LogicTree) {
		super(tree);

		tree.notifyOnUpdate(update);
	}

	function update() {
		run();
	}
}
