package armory.trait;

import iron.Trait;
#if WITH_PHYSICS
import haxebullet.Bullet;
#end

class VehicleWheel extends Trait {

#if (!WITH_PHYSICS)
	public function new() { super(); }
#else

	static inline var VEHICLE_FRONT_X = 3.5 / 2; // Distance to wheel from vehicle center
	static inline var VEHICLE_BACK_X = 4.1 / 2;
	static inline var VEHICLE_FRONT_Y = 3.6;
	static inline var VEHICLE_BACK_Y = 3.5;
	static inline var CONNECTION_HEIGHT_FRONT = 0.3;
	static inline var CONNECTION_HEIGHT_BACK = 0.4;

	public var isFrontWheel:Bool;
	public var wheelRadius = 0.75;
	public var wheelWidth = 0.53;
	var id:Int;

	public function new(id:Int) {
		super();
		this.id = id;
	}

	public function getConnectionPoint():BtVector3 {
		var connectionPoint:BtVector3;
		
		if (id == 0) {
			isFrontWheel = true;

			connectionPoint = BtVector3.create(
				VEHICLE_FRONT_X - (0.3 * wheelWidth),
				VEHICLE_FRONT_Y - wheelRadius,
				CONNECTION_HEIGHT_FRONT
			).value;
		}
		else if (id == 1) {
			isFrontWheel = true;

			connectionPoint = BtVector3.create(
				-VEHICLE_FRONT_X + (0.3 * wheelWidth),
				VEHICLE_FRONT_Y - wheelRadius,
				CONNECTION_HEIGHT_FRONT
			).value;
		}
		else if (id == 2) {
			isFrontWheel = false;

			connectionPoint = BtVector3.create(
				-VEHICLE_BACK_X + (0.3 * wheelWidth),
				-VEHICLE_BACK_Y + wheelRadius,
				CONNECTION_HEIGHT_BACK
			).value;
		}
		else { //if (id == 3) {
			isFrontWheel = false;

			connectionPoint = BtVector3.create(
				VEHICLE_BACK_X - (0.3 * wheelWidth),
				-VEHICLE_BACK_Y + wheelRadius,
				CONNECTION_HEIGHT_BACK
			).value;
		}

		return connectionPoint;
	}
#end
}
