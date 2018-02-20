package armory.logicnode;

class InverseNode extends LogicNode {

	var c = false;

	public function new(tree:LogicTree) {
		super(tree);
		tree.notifyOnUpdate(update);
	}

	override function run() {
		c = true;
	}

	function update() {
		if (!c) super.run();
		c = false;
	}
}
