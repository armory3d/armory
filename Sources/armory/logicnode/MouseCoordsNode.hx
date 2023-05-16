package armory.logicnode;

import iron.math.Vec4;

class MouseCoordsNode extends LogicNode {

	var coords = new Vec4();

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var mouse = iron.system.Input.getMouse();
		if (from == 0) {
			coords.x = mouse.x;
			coords.y = mouse.y;
			return coords;
		}
		else if (from == 1) {
			coords.x = mouse.movementX;
			coords.y = mouse.movementY;
			return coords;
		}
		else {
			return mouse.wheelDelta;
		}
	}
}
