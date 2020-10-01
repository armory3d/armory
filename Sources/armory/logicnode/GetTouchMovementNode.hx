package armory.logicnode;

import iron.math.Vec4;

class GetTouchMovementNode extends LogicNode {

	var coords = new Vec4();

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var touch = iron.system.Input.getSurface();
		var multX: Float = inputs[0].get();
		var multY: Float = inputs[1].get();

		return switch (from) {
			case 0: touch.movementX;
			case 1: touch.movementY;
			case 2: touch.movementX * multX;
			case 3: touch.movementY * multY;
			default: null;
		}
	}
}
