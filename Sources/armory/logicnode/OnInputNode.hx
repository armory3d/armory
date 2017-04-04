package armory.logicnode;

class OnInputNode extends Node {

	public var property0:String;

	public function new(tree:LogicTree) {
		super(tree);

		tree.notifyOnUpdate(update);
	}

	function update() {
		var b = false;
		switch (property0) {
		case "Down":
			b = armory.system.Input.down;
		case "Started":
			b = armory.system.Input.started;
		case "Released":
			b = armory.system.Input.released;
		case "Moved":
			b = armory.system.Input.moved;
		}
		if (b) run();
	}
}
