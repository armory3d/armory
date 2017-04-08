package armory.logicnode;

class OnInitNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);

		tree.notifyOnInit(init);
	}

	function init() {
		run();
	}
}
