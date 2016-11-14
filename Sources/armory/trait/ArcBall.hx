package armory.trait;

import iron.object.Object;
import iron.Trait;
import iron.system.Input;
import iron.math.Vec4;
import iron.math.Quat;

@:keep
class ArcBall extends Trait {

	public function new() {
		super();

		notifyOnUpdate(update);
	}

	function update() {
		if (Input.occupied) return;

		if (Input.down) {
			object.transform.rotate(new Vec4(0, 0, 1), -Input.deltaX / 100);
			object.transform.buildMatrix();
			object.transform.rotate(object.transform.matrix.right(), -Input.deltaY / 100);
			object.transform.buildMatrix();
		}
	}
}
