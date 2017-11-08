package armory.trait;

import iron.math.Vec4;
import armory.trait.internal.CameraController;

class SidescrollerController extends CameraController {

#if (!arm_bullet)
	public function new() { super(); }
#else

	public function new() {
		super();

		iron.Scene.active.notifyOnInit(init);
	}
	
	function init() {
		notifyOnUpdate(update);
	}

	var dir = new Vec4();
	function update() {
		if (!body.ready) return;

		if (jump) {
			body.applyImpulse(new Vec4(0, 0, 20));
			jump = false;
		}

		// Move
		dir.set(0, 0, 0);
		if (moveLeft) dir.add(transform.look().mult(-1));
		if (moveRight) dir.add(transform.look());

		// Push down
		var btvec = body.getLinearVelocity();
		body.setLinearVelocity(0.0, 0.0, btvec.z() - 1.0);

		var arm = object.getChild("Ballie");
		arm.animation.pause();

		if (moveLeft || moveRight) {
			arm.animation.resume();
			dir.mult(-4 * 0.7);
			body.activate();
			body.setLinearVelocity(dir.x, dir.y, btvec.z() - 1.0);
		}

		// Keep vertical
		body.setAngularFactor(0, 0, 0);
		camera.buildMatrix();
	}
#end
}
