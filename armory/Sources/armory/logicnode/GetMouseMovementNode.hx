package armory.logicnode;

import kha.FastFloat;

class GetMouseMovementNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var mouse = iron.system.Input.getMouse();

		var multX: FastFloat = inputs[0].get();
		var multY: FastFloat = inputs[1].get();
		var multWheelDelta: FastFloat = inputs[2].get();

		return switch (from) {
			case 0: mouse.movementX;
			case 1: mouse.movementY;
			case 2: mouse.movementX * multX;
			case 3: mouse.movementY * multY;
			case 4: mouse.wheelDelta;
			case 5: mouse.wheelDelta * multWheelDelta;
			default: 0;
		}
	}
}
