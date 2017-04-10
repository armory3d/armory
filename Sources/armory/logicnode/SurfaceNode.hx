package armory.logicnode;

class SurfaceNode extends LogicNode {

	public var property0:String;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var surface = armory.system.Input.getSurface();
		switch (property0) {
		case "Touched":
			return surface.down;
		case "Started":
			return surface.started;
		case "Released":
			return surface.released;
		case "Moved":
			return surface.moved;
		}
		return false;
	}
}
