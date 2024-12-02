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
		case "started":
			b = surface.started();
		case "down":
			b = surface.down();
		case "released":
			b = surface.released();
		case "moved":
			b = surface.moved;
		}
		if (b) runOutput(0);
	}

	override function get(from: Int): Dynamic {
		var surface = iron.system.Input.getSurface();
		switch (property0) {
		case "started":
			return surface.started();
		case "down":
			return surface.down();
		case "released":
			return surface.released();
		case "moved":
			return surface.moved;
		}
		return false;
	}
}
