package armory.trait;

import iron.math.Vec4;
import iron.system.Input;
import armory.trait.internal.PhysicsWorld;
import armory.trait.internal.CameraController;

class ThirdPersonController extends CameraController {

#if (!arm_physics)
	public function new() { super(); }
#else

	static inline var rotationSpeed = 1.0; 

	public function new() {
		super();

		iron.Scene.active.notifyOnInit(init);
	}
	
	function init() {
		PhysicsWorld.active.notifyOnPreUpdate(preUpdate);
		notifyOnUpdate(update);
		notifyOnRemove(removed);
	}

	var xVec = Vec4.xAxis();
	var zVec = Vec4.zAxis();
	function preUpdate() {
		if (Input.occupied || !body.ready) return;
		
		var mouse = Input.getMouse();
		if (mouse.down()) {
			// kha.SystemImpl.lockMouse();
			camera.transform.rotate(xVec, mouse.movementY / 250 * rotationSpeed);
			transform.rotate(zVec, -mouse.movementX / 250 * rotationSpeed);
			camera.buildMatrix();
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
			body.applyImpulse(new Vec4(0, 0, 20));
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
		body.setLinearVelocity(0.0, 0.0, btvec.z() - 1.0);

		var arm = object.getChild("Ballie");
		arm.animation.paused = true;

		if (moveForward || moveBackward || moveLeft || moveRight) {			
			arm.animation.paused = false;
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
