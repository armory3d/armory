package armory.logicnode;

import iron.math.Vec4;

class GetMouseMovementNode extends LogicNode {

	var coords = new Vec4();

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var mouse = iron.system.Input.getMouse();
		var multX: Float = inputs[0].get();
		var multY: Float = inputs[1].get();
		var multDelta: Float = inputs[2].get();

		return switch (from) {
			case 0: mouse.movementX;
			case 1: mouse.movementY;
			case 2: mouse.wheelDelta;
			case 3: mouse.movementX * multX;
			case 4: mouse.movementY * multY;
			case 5: mouse.wheelDelta * multDelta;
			default: null;
		}
	}
}
