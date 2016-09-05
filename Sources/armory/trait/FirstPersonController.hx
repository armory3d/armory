package armory.trait;

import iron.math.Mat4;
import iron.math.Vec4;
import iron.Trait;
import iron.sys.Input;
import iron.sys.Time;
import iron.object.Transform;
import iron.object.CameraObject;
import armory.trait.internal.RigidBody;

class FirstPersonController extends Trait {

#if (!WITH_PHYSICS)
	public function new() { super(); }
#else

    var transform:Transform;
    var body:RigidBody;
    var camera:CameraObject;

    var moveForward = false;
    var moveBackward = false;
    var moveLeft = false;
    var moveRight = false;
    var jump = false;

    public function new() {
        super();

		notifyOnInit(init);
		notifyOnUpdate(update);
        kha.input.Keyboard.get().notify(onDown, onUp);
    }
	
	function init() {
		transform = object.transform;
		body = object.getTrait(RigidBody);
        for (o in object.children) {
            if (Std.is(o, CameraObject)) {
                camera = cast(o, CameraObject);
                break;
            }
        }
	}

    function onDown(key: kha.Key, char: String) {
        if (char == "w") moveForward = true;
        else if (char == "d") moveRight = true;
        else if (char == "s") moveBackward = true;
        else if (char == "a") moveLeft = true;
        else if (char == "x") jump = true;
    }

    function onUp(key: kha.Key, char: String) {
        if (char == "w") moveForward = false;
        else if (char == "d") moveRight = false;
        else if (char == "s") moveBackward = false;
        else if (char == "a") moveLeft = false;
        else if (char == "x") jump = false;
    }

    var locked = true;
    public function update() {
		if (Input.occupied || !body.bodyCreated) return;
		
        // Unlock
        // if (locked &&
        //     Input.x > iron.App.w / 2 - 20 && Input.x < iron.App.w / 2 + 20 &&
        //     Input.y > iron.App.h / 2 - 20 && Input.y < iron.App.h / 2 +20) {
        //     locked = false;
        // }

        // Look
        // if (!locked) {
        if (Input.touch) {
			camera.rotate(new Vec4(1, 0, 0), -Input.deltaY / 350);
			transform.rotate(new Vec4(0, 0, 1), -Input.deltaX / 350);
        	body.syncTransform();
        }

        // Move
		var dir = new Vec4();
        if (moveForward) {
            var mat = Mat4.identity();
            transform.rot.saveToMatrix(mat);

            var force = new Vec4(0, 1, 0);
            force.applyProjection(mat);
            dir.add(force);
        }
        if (moveBackward) {
            var mat = Mat4.identity();
            transform.rot.saveToMatrix(mat);

            var force = new Vec4(0, -1, 0);
            force.applyProjection(mat);
            dir.add(force);
        }
        if (moveLeft) {
            var mat = Mat4.identity();
            transform.rot.saveToMatrix(mat);

            var force = new Vec4(-1, 0, 0);
            force.applyProjection(mat);
            dir.add(force);
        }
        if (moveRight) {
            var mat = Mat4.identity();
            transform.rot.saveToMatrix(mat);

            var force = new Vec4(1, 0, 0);
            force.applyProjection(mat);
            dir.add(force);
        }

        if (jump) {
            var mat = Mat4.identity();
            transform.rot.saveToMatrix(mat);

            var force = new Vec4(0, 0, 1);
            force.applyProjection(mat);
            force = force.mult(Time.delta * 70);

            body.applyImpulse(force);
        }

        if (!moveForward && !moveBackward && !moveLeft && !moveRight && !jump) {
            var mat = Mat4.identity();
            transform.rot.saveToMatrix(mat);

            var force = new Vec4(0, 0, -1);
            force.applyProjection(mat);
            force = force.mult(Time.delta * 3000 / 2);
            // body.applyImpulse(force);
			
			var btvec = body.getLinearVelocity();
			body.setLinearVelocity(0.0, 0.0, btvec.z() - 1.0);
        }
		else {
			body.activate();
			dir = dir.mult(Time.delta * 250);
			body.setLinearVelocity(dir.x, dir.y, dir.z);
		}

		body.setAngularFactor(0, 0, 0);

        camera.updateMatrix();
    }
#end
}
