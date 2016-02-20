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
	public var wheelRadius = 0.715;
	public var wheelWidth = 0.35;
	var id:Int;

	public function new(id:Int) {
		super();

		this.id = id;

		var CUBE_HALF_EXTENTS = 1;
		var connectionHeight = 0.9; //1.2;

		if (id == 0) {
			isFrontWheel = true;

			connectionPointCS0 = BtVector3.create(
				CUBE_HALF_EXTENTS - (0.3 * wheelWidth),
				2 * CUBE_HALF_EXTENTS - wheelRadius,
				connectionHeight
			);
		}
		else if (id == 1) {
			isFrontWheel = true;

			connectionPointCS0 = BtVector3.create(
				-CUBE_HALF_EXTENTS + (0.3 * wheelWidth),
				2 * CUBE_HALF_EXTENTS - wheelRadius,
				connectionHeight
			);
		}
		else if (id == 2) {
			isFrontWheel = false;

			connectionPointCS0 = BtVector3.create(
				-CUBE_HALF_EXTENTS + (0.3 * wheelWidth),
				-2 * CUBE_HALF_EXTENTS + wheelRadius,
				connectionHeight
			);
		}
		else if (id == 3) {
			isFrontWheel = false;

			connectionPointCS0 = BtVector3.create(
				CUBE_HALF_EXTENTS - (0.3 * wheelWidth),
				-2 * CUBE_HALF_EXTENTS + wheelRadius,
				connectionHeight
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
