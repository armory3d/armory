package cycles.trait;

import lue.trait.Trait;
#if WITH_PHYSICS
import haxebullet.Bullet;
#end

class VehicleWheel extends Trait {

#if (!WITH_PHYSICS)
	public function new() { super(); }
#else

	public var connectionPointCS0:BtVector3Pointer;
	public var isFrontWheel:Bool;
	public var wheelRadius = 0.75;
	public var wheelWidth = 0.53;
	var id:Int;

	public function new(id:Int) {
		super();

		this.id = id;

		var VEHICLE_FRONT_X = 3.5 / 2; // Distance to wheel from vehicle center
		var VEHICLE_BACK_X = 4.1 / 2;
		var VEHICLE_FRONT_Y = 3.6;
		var VEHICLE_BACK_Y = 3.5;
		var CONNECTION_HEIGHT_FRONT = 0.3;
		var CONNECTION_HEIGHT_BACK = 0.4;

		if (id == 0) {
			isFrontWheel = true;

			connectionPointCS0 = BtVector3.create(
				VEHICLE_FRONT_X - (0.3 * wheelWidth),
				VEHICLE_FRONT_Y - wheelRadius,
				CONNECTION_HEIGHT_FRONT
			);
		}
		else if (id == 1) {
			isFrontWheel = true;

			connectionPointCS0 = BtVector3.create(
				-VEHICLE_FRONT_X + (0.3 * wheelWidth),
				VEHICLE_FRONT_Y - wheelRadius,
				CONNECTION_HEIGHT_FRONT
			);
		}
		else if (id == 2) {
			isFrontWheel = false;

			connectionPointCS0 = BtVector3.create(
				-VEHICLE_BACK_X + (0.3 * wheelWidth),
				-VEHICLE_BACK_Y + wheelRadius,
				CONNECTION_HEIGHT_BACK
			);
		}
		else if (id == 3) {
			isFrontWheel = false;

			connectionPointCS0 = BtVector3.create(
				VEHICLE_BACK_X - (0.3 * wheelWidth),
				-VEHICLE_BACK_Y + wheelRadius,
				CONNECTION_HEIGHT_BACK
			);
		}
	}

	/*public var trans:BtTransform;
	public function syncTransform() {
		var p = trans.getOrigin();
		var q = trans.getRotation();
		node.transform.pos.set(p.x(), p.y(), p.z());
		node.transform.rot.set(q.x(), q.y(), q.z(), q.w());
		node.transform.dirty = true;
	}*/
#end
}
