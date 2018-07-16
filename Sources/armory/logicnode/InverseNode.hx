package armory.logicnode;

class InverseNode extends LogicNode {

	var c = false;

	public function new(tree:LogicTree) {
		super(tree);
		tree.notifyOnUpdate(update);
	}

	override function run(node:LogicNode) {
		c = true;
	}

	function update() {
		if (!c) super.run(this);
		c = false;
	}
}
