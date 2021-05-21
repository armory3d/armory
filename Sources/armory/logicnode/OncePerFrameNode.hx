package armory.logicnode;

class OncePerFrameNode extends LogicNode {

	var c = false;

	public function new(tree: LogicTree) {
		super(tree);
		tree.notifyOnUpdate(update);
	}

	override function run(from: Int) {
		if(c) runOutput(0);
		c = false;
	}

	function update() {
		c = true;
	}
}
