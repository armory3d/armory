package armory.logicnode;

class OnMouseNode extends LogicNode {

	public var property0: String;
	public var property1: String;

	@:deprecated("The 'On Mouse' node is deprecated and will be removed in future SDK versions. Please use 'Mouse' instead.")
	public function new(tree: LogicTree) {
		super(tree);

		tree.notifyOnUpdate(update);
	}

	function update() {
		var mouse = iron.system.Input.getMouse();
		var b = false;
		switch (property0) {
		case "Down":
			b = mouse.down(property1);
		case "Started":
			b = mouse.started(property1);
		case "Released":
			b = mouse.released(property1);
		case "Moved":
			b = mouse.moved;
		}
		if (b) runOutput(0);
	}
}
