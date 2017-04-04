package armory.logicnode;

import armory.math.Vec4;

class InputCoordsNode extends Node {

	var coords = new Vec4();

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		if (from == 0) {
			coords.x = armory.system.Input.x;
			coords.y = armory.system.Input.y;
		}
		else if (from == 1) {
			coords.x = armory.system.Input.movementX;
			coords.y = armory.system.Input.movementY;
		}
		return coords;
	}
}
