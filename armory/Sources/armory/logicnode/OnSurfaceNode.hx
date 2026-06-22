package armory.logicnode;

class OnSurfaceNode extends LogicNode {

	public var property0: String;

	@:deprecated("The 'On Surface' node is deprecated and will be removed in future SDK versions. Please use 'Surface' instead.")
	public function new(tree: LogicTree) {
		super(tree);

		tree.notifyOnUpdate(update);
	}

	function update() {
		var surface = iron.system.Input.getSurface();
		var b = false;
		switch (property0) {
		case "Touched":
			b = surface.down();
		case "Started":
			b = surface.started();
		case "Released":
			b = surface.released();
		case "Moved":
			b = surface.moved;
		}
		if (b) runOutput(0);
	}
}
