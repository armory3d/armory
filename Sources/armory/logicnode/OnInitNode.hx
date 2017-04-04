package armory.logicnode;

class OnInitNode extends Node {

	public function new(tree:LogicTree) {
		super(tree);

		tree.notifyOnInit(init);
	}

	function init() {
		run();
	}
}
