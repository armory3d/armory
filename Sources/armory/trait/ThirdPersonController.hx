package armory.trait;

import iron.math.Vec4;
import iron.system.Input;
import iron.object.Object;
import armory.trait.physics.PhysicsWorld;
import armory.trait.internal.CameraController;

class ThirdPersonController extends CameraController {

#if (!arm_bullet)
	public function new() { super(); }
#else

	static inline var rotationSpeed = 1.0; 

	var animObject:String;
	var idleAction:String;
	var runAction:String;
	var state = 0; // Idle, run
	var arm:Object;

	public function new(animObject = "", idle = "idle", run = "run") {
		super();

		this.animObject = animObject;
		this.idleAction = idle;
		this.runAction = run;

		iron.Scene.active.notifyOnInit(init);
	}

	function findAnimation(o:Object):Object {
		if (o.animation != null) return o;
		for (c in o.children) {
			var co = findAnimation(c);
			if (co != null) return co;
		}
		return null;
	}
	
	function init() {
		if (animObject == "") arm = findAnimation(object);
		else arm = object.getChild(animObject);

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

		if (jump) body.applyImpulse(new Vec4(0, 0, 20));

		// Move
		dir.set(0, 0, 0);
		if (moveForward) dir.add(transform.look());
		if (moveBackward) dir.add(transform.look().mult(-1));
		if (moveLeft) dir.add(transform.right().mult(-1));
		if (moveRight) dir.add(transform.right());

		// Push down
		var btvec = body.getLinearVelocity();
		body.setLinearVelocity(0.0, 0.0, btvec.z() - 1.0);

		if (moveForward || moveBackward || moveLeft || moveRight) {
			if (state != 1) {
				arm.animation.play(runAction, null, 0.2);
				state = 1;		
			}
			arm.animation.paused = false;
			dir.mult(-4 * 0.7);
			body.activate();
			body.setLinearVelocity(dir.x, dir.y, btvec.z() - 1.0);
		}
		else {
			if (state != 0) {
				arm.animation.play(idleAction, null, 0.2);
				state = 0;
			}
		}

		// Keep vertical
		body.setAngularFactor(0, 0, 0);
		camera.buildMatrix();
	}
#end
}
