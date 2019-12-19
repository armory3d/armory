package armory.logicnode;

import iron.math.Vec4;

class SurfaceCoordsNode extends LogicNode {

	var coords = new Vec4();

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var surface = iron.system.Input.getSurface();
		if (from == 0) {
			coords.x = surface.x;
			coords.y = surface.y;
			return coords;
		}
		else if (from == 1) {
			coords.x = surface.movementX;
			coords.y = surface.movementY;
			return coords;
		}
		else {
			return surface.wheelDelta;
		}
	}
}
