package armory.trait;

import iron.object.Object;
import iron.Trait;
import iron.system.Input;
import iron.math.Vec4;
import iron.math.Quat;

class ArcBall extends Trait {

	public function new() {
		super();

		notifyOnUpdate(update);
	}

	function update() {
		if (Input.occupied) return;

		var mouse = Input.getMouse();
		if (mouse.down()) {
			object.transform.rotate(new Vec4(0, 0, 1), -mouse.movementX / 100);
			object.transform.buildMatrix();
			object.transform.rotate(object.transform.world.right(), -mouse.movementY / 100);
			object.transform.buildMatrix();
		}
	}
}
