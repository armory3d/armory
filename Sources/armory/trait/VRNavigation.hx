package armory.trait;

import iron.Trait;
import iron.system.Input;
import iron.system.Time;
import iron.object.CameraObject;
import iron.math.Vec4;

class VRNavigation extends Trait {

#if arm_vr

	static inline var speed = 5.0;

	var camera:CameraObject;
	var mouse:Mouse;

	public function new() {
		super();

		notifyOnInit(init);
		notifyOnUpdate(update);
	}

	function init() {
		mouse = Input.getMouse();
		camera = cast(object, CameraObject);
	}

	var look = new Vec4();
	function update() {
		// Testing..
		if (mouse.down()) {
			var vr = kha.vr.VrInterface.instance;
			var V = (vr != null && vr.IsPresenting()) ? camera.leftV : camera.V;
			look.set(-V._02, -V._12, -V._22);
			camera.transform.move(look, Time.delta * speed);
		}
	}

#end
}
