package armory.logicnode;

import armory.math.Vec4;

class SensorCoordsNode extends LogicNode {

	var coords = new Vec4();

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var sensor = armory.system.Input.getSensor();
		coords.x = sensor.x;
		coords.y = sensor.y;
		coords.z = sensor.z;
		return coords;
	}
}
