package armory.trait;

import iron.Trait;
import iron.system.Input;
import iron.math.Vec4;

class ArcBall extends Trait {

	@prop
	public var axis = new Vec4(0, 0, 1);
	
	public function new() {
		super();

		notifyOnUpdate(update);
	}

	function update() {
		if (Input.occupied) return;

		var mouse = Input.getMouse();
		if (mouse.down()) {
			object.transform.rotate(axis, -mouse.movementX / 100);
			object.transform.rotate(object.transform.world.right(), -mouse.movementY / 100);
		}
	}
}
