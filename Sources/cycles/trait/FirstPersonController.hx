package cycles.trait;

import lue.math.Mat4;
import lue.math.Vec4;
import lue.trait.Trait;
import lue.sys.Input;
import lue.sys.Time;
import lue.node.Transform;
import lue.node.CameraNode;
import cycles.trait.RigidBody;

class FirstPersonController extends Trait {

#if (!WITH_PHYSICS)
	public function new() { super(); }
#else

    var transform:Transform;
    var body:RigidBody;
    var camera:CameraNode;

    var moveForward = false;
    var moveBackward = false;
    var moveLeft = false;
    var moveRight = false;
    var jump = false;

    public function new() {
        super();

		requestInit(init);
		requestUpdate(update);
        kha.input.Keyboard.get().notify(onDown, onUp);
    }
	
	function init() {
		transform = node.transform;
		body = node.getTrait(RigidBody);
		camera = lue.node.RootNode.cameras[0];
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
		if (Input.occupied) return;
		
        // Unlock
        // if (locked &&
        //     Input.x > lue.App.w / 2 - 20 && Input.x < lue.App.w / 2 + 20 &&
        //     Input.y > lue.App.h / 2 - 20 && Input.y < lue.App.h / 2 +20) {
        //     locked = false;
        // }

        // Look
        // if (!locked) {
        if (Input.touch) {
			camera.rotate(new Vec4(1, 0, 0), Input.deltaY / 200);
			transform.rotate(new Vec4(0, 0, 1), -Input.deltaX / 200);
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
            force = force.mult(Time.delta * 3000);

            body.applyImpulse(force);
        }
		else {
			body.activate();
			dir = dir.mult(Time.delta * 250);
			body.setLinearVelocity(dir.x, dir.y, dir.z);
		}


        // if (Input.touch) {
        //     // Look			
		// 	camera.rotate(camera.right(), Input.deltaY / 100);
		// 	transform.rotate(new Vec4(0, 0, 1), -Input.deltaX / 100);
        //     body.syncTransform();

        //     // Move
        //     var mat = Mat4.identity();
        //     transform.rot.saveToMatrix(mat);

        //     var force = new Vec4(0, 1, 0);
        //     force.applyProjection(mat);
        //     force = force.mult(Time.delta * 200);

        //     body.applyImpulse(force);
        // }

		body.setAngularFactor(0, 0, 0);

        camera.updateMatrix();
    }
#end
}
