package armory.logicnode;

class InverseNode extends LogicNode {

	var c = false;

	public function new(tree: LogicTree) {
		super(tree);
		tree.notifyOnUpdate(update);
	}

	override function run(from: Int) {
		c = true;
	}

	function update() {
		if (!c) runOutput(0);
		c = false;
	}
}
