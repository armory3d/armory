package armory.logicnode;

import iron.math.Vec4;

class SensorCoordsNode extends LogicNode {

	var coords = new Vec4();

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		#if kha_html5
		switch(from){
			case 0:
				var sensor = iron.system.Input.getSensor();
					coords.x = sensor.x;
					coords.y = sensor.y;
					coords.z = sensor.z;
				return coords;
			case 1:
				var gyro = kha.input.Sensor.get(kha.input.SensorType.Gyroscope);
					gyro.notify(function listener(x: Float, y: Float, z: Float) {
						coords.x = x;
						coords.y = y;
						coords.z = z;
					});
				return coords;
			case 2:
				return js.Browser.window.orientation;
			default: return null;
		}
		#end
		return null;
	}
}
