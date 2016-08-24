package armory.trait;

import iron.math.Mat4;
import iron.math.Vec4;
import iron.Trait;
import iron.sys.Input;
import iron.sys.Time;
import iron.object.Transform;
import iron.object.CameraObject;
import armory.trait.internal.RigidBody;

class GunController extends Trait {

#if (!WITH_PHYSICS)
	public function new() { super(); }
#else

	var transform:Transform;

	public function new(projectileObject:String, spawnObject:String) {
		super();

		notifyOnInit(init);
		//notifyOnUpdate(update);
	}
	
	function init() {
		transform = object.transform;
	}
#end
}
