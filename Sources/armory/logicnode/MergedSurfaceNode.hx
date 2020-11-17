package armory.logicnode;

class MergedSurfaceNode extends LogicNode {

	public var property0: String;

	public function new(tree: LogicTree) {
		super(tree);

		tree.notifyOnUpdate(update);
	}

	function update() {
		var surface = iron.system.Input.getSurface();
		var b = false;
		switch (property0) {
		case "Started":
			b = surface.started();
		case "Down":
			b = surface.down();
		case "Released":
			b = surface.released();
		case "Moved":
			b = surface.moved;
		}
		if (b) runOutput(0);
	}

	override function get(from: Int): Dynamic {
		var surface = iron.system.Input.getSurface();
		switch (property0) {
		case "Started":
			return surface.started();
		case "Down":
			return surface.down();
		case "Released":
			return surface.released();
		case "Moved":
			return surface.moved;
		}
		return false;
	}
}
