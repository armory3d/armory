package armory.trait;

import iron.math.Vec4;
import iron.system.Input;
import iron.object.Object;
import iron.object.CameraObject;
import armory.trait.physics.PhysicsWorld;
import armory.trait.internal.CameraController;

class FirstPersonController extends CameraController {

#if (!arm_physics)
	public function new() { super(); }
#else

	var head: Object;
	static inline var rotationSpeed = 2.0;

	public function new() {
		super();

		iron.Scene.active.notifyOnInit(init);
	}

	function init() {
		head = object.getChildOfType(CameraObject);

		PhysicsWorld.active.notifyOnPreUpdate(preUpdate);
		notifyOnUpdate(update);
		notifyOnRemove(removed);
	}

	var xVec = Vec4.xAxis();
	var zVec = Vec4.zAxis();
	function preUpdate() {
		if (Input.occupied || !body.ready) return;

		var mouse = Input.getMouse();
		var kb = Input.getKeyboard();

		if (mouse.started() && !mouse.locked) mouse.lock();
		else if (kb.started("escape") && mouse.locked) mouse.unlock();

		if (mouse.locked || mouse.down()) {
			head.transform.rotate(xVec, -mouse.movementY / 250 * rotationSpeed);
			transform.rotate(zVec, -mouse.movementX / 250 * rotationSpeed);
			body.syncTransform();
		}
	}

	function removed() {
		PhysicsWorld.active.removePreUpdate(preUpdate);
	}

	var dir = new Vec4();
	function update() {
		if (!body.ready) return;

		if (jump) {
			body.applyImpulse(new Vec4(0, 0, 16));
			jump = false;
		}

		// Move
		dir.set(0, 0, 0);
		if (moveForward) dir.add(transform.look());
		if (moveBackward) dir.add(transform.look().mult(-1));
		if (moveLeft) dir.add(transform.right().mult(-1));
		if (moveRight) dir.add(transform.right());

		// Push down
		var btvec = body.getLinearVelocity();
		body.setLinearVelocity(0.0, 0.0, btvec.z - 1.0);

		if (moveForward || moveBackward || moveLeft || moveRight) {
			var dirN = dir.normalize();
			dirN.mult(6);
			body.activate();
			body.setLinearVelocity(dirN.x, dirN.y, btvec.z - 1.0);
		}

		// Keep vertical
		body.setAngularFactor(0, 0, 0);
		camera.buildMatrix();
	}
#end
}
