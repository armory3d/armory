package armory.logicnode;

class OnRemoveNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
		tree.notifyOnRemove(onRemove);
	}

	function onRemove() {
		runOutput(0);
	}
}
