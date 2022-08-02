package armory.logicnode;

import iron.math.Vec4;

class GetCursorLocationNode extends LogicNode {

	var coords = new Vec4();

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var mouse = iron.system.Input.getMouse();

		return switch (from) {
			case 0: mouse.x;
			case 1: mouse.y;
			case 2: mouse.x * -1;
			case 3: mouse.y * -1;
			default: null;
		}
	}
}
