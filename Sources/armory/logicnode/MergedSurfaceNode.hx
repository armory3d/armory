package armory.logicnode;

class MergedSurfaceNode extends LogicNode {

	public var property0:String;

	public function new(tree:LogicTree) {
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
			b = surface.moved();
		}
		if (b) runOutput(0);
	}

	override function get(from:Int):Dynamic {
		var surface = iron.system.Input.getSurface();
		switch (property0) {
		case "Touched":
			return surface.down();
		case "Started":
			return surface.started();
		case "Released":
			return surface.released();
		case "Moved":
			return surface.moved();
		}
		return false;
	}
}
