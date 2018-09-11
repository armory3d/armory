package armory.trait;

import iron.object.Object;
import iron.math.Vec4;
import armory.trait.internal.CameraController;

class SidescrollerController extends CameraController {

#if (!arm_physics)
	public function new() { super(); }
#else

	var animObject:String;
	var idleAction:String;
	var runAction:String;
	var currentAction:String;
	var arm:Object;

	public function new(animObject = "", idle = "idle", run = "run") {
		super();

		this.animObject = animObject;
		this.idleAction = idle;
		this.runAction = run;
		currentAction = idleAction;

		iron.Scene.active.notifyOnInit(init);
	}
	
	function init() {
		if (animObject == "") arm = findAnimation(object);
		else arm = object.getChild(animObject);

		notifyOnUpdate(update);
	}

	function findAnimation(o:Object):Object {
		if (o.animation != null) return o;
		for (c in o.children) {
			var co = findAnimation(c);
			if (co != null) return co;
		}
		return null;
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
		body.setLinearVelocity(0.0, 0.0, btvec.z - 1.0);

		if (moveLeft || moveRight) {
			if (currentAction != runAction) {
				arm.animation.play(runAction, null, 0.2);
				currentAction = runAction;	
			}
			dir.mult(-4 * 0.7);
			body.activate();
			body.setLinearVelocity(dir.x, dir.y, btvec.z - 1.0);
		}
		else {
			if (currentAction != idleAction) {
				arm.animation.play(idleAction, null, 0.2);
				currentAction = idleAction;
			}
		}

		// Keep vertical
		body.setAngularFactor(0, 0, 0);
		camera.buildMatrix();
	}
#end
}
