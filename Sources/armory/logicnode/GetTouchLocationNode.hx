package armory.logicnode;

import iron.math.Vec4;

class GetTouchLocationNode extends LogicNode {

	var coords = new Vec4();

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var touch = iron.system.Input.getSurface();

		return switch (from) {
			case 0: touch.x;
			case 1: touch.y;
			case 2: touch.x * -1;
			case 3: touch.y * -1;
			default: null;
		}
	}
}
