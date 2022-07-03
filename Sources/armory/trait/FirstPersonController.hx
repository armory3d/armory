package arm;

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

	var head : Object;
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
	var add1 = new Vec4();
	var add2 = new Vec4();
	var add = new Vec4();
	var sin = 0.0;
	var cos = 0.0;
	function update() {
		if (!body.ready) return;

		if (jump) {
			body.applyImpulse(new Vec4(0, 0, 16));
			jump = false;
		}

		// Move
		dir.set(0, 0, 0);

        var pi = 355/113;
        var z = transform.rot.z;
        var zToRad = z * pi / 180;

        if (z >= 0 && z <= 90) {
            cos = Math.cos(zToRad);
            sin = Math.sin(zToRad);
        }
        else if (z > 90 && z <= 180) {
            cos = -Math.cos(zToRad);
            sin = Math.sin(zToRad);
        }
        else if (z > 180 && z <= 270) {
            cos = -Math.cos(zToRad);
            sin = -Math.sin(zToRad);
        }
        else if (z > 280 && z <= 360) {
            cos = Math.cos(zToRad);
            sin = -Math.sin(zToRad);
        }

        if (moveForward && moveLeft) {
            add1.set(transform.look().x * cos, transform.look().y * cos, 0, 0);
            add2.set(transform.right().mult(-1).x * sin, transform.right().mult(-1).y * sin, 0, 0);
            add.add(add1.normalize());
            add.add(add2.normalize());
        }
        else if (moveForward && moveRight) {
            add1.set(transform.look().x * cos, transform.look().y * cos, 0, 0);
            add2.set(transform.right().x * sin, transform.right().y * sin, 0, 0);
            add.add(add1.normalize());
            add.add(add2.normalize());
        }
        else if (moveBackward && moveLeft) {
            add1.set(transform.look().mult(-1).x * cos, transform.look().mult(-1).y * cos, 0, 0);
            add2.set(transform.right().mult(-1).x * sin, transform.right().mult(-1).y * sin, 0, 0);
            add.add(add1.normalize());
            add.add(add2.normalize());
        }
        else if (moveBackward && moveRight) {
            add1.set(transform.look().mult(-1).x * cos, transform.look().mult(-1).y * cos, 0, 0);
            add2.set(transform.right().x * sin, transform.right().y * sin, 0, 0);
            add.add(add1.normalize());
            add.add(add2.normalize());
        }
        else if (moveForward)
            add.set(transform.look().x, transform.look().y, 0, 0);
        else if (moveBackward)
            add.set(transform.look().mult(-1).x, transform.look().mult(-1).y, 0, 0);
        else if (moveLeft)
            add.set(transform.right().mult(-1).x, transform.right().mult(-1).y, 0, 0);
        else if (moveRight)
            add.set(transform.right().x, transform.right().y, 0, 0);

        dir.add(add.normalize());

		// Push down
		var btvec = body.getLinearVelocity();
		body.setLinearVelocity(0.0, 0.0, btvec.z - 1.0);

		if (moveForward || moveBackward || moveLeft || moveRight) {
			dir.mult(5);
			body.activate();
			body.setLinearVelocity(dir.x, dir.y, btvec.z - 1.0);
		}
		// Keep vertical
		body.setAngularFactor(0, 0, 0);
		camera.buildMatrix();
	}
#end
}
