package armory.trait;

import iron.math.Mat4;
import iron.math.Vec4;
import iron.Trait;
import iron.system.Input;
import iron.system.Time;
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

    static inline var rotationSpeed = 1.0; 

    public function new() {
        super();

		Scene.active.notifyOnInit(init);
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
        
        notifyOnUpdate(update);
        kha.input.Keyboard.get().notify(onDown, onUp);
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

    var dir = new Vec4();
    var force = new Vec4();
    var xVec = new Vec4(1, 0, 0);
    var zVec = new Vec4(1, 0, 0);
    var mat = Mat4.identity();
    function update() {
		if (Input.occupied || !body.bodyCreated) return;
		
        if (Input.touch) {
			camera.rotate(xVec, -Input.deltaY / 250 * rotationSpeed);
			transform.rotate(zVec, -Input.deltaX / 250 * rotationSpeed);
        	body.syncTransform();
        }

        // Move
		dir.set(0, 0, 0);
        if (moveForward) {
            transform.rot.saveToMatrix(mat);
            force.set(0, 1, 0);
            force.applyProjection(mat);
            dir.add(force);
        }
        if (moveBackward) {
            transform.rot.saveToMatrix(mat);
            force.set(0, -1, 0);
            force.applyProjection(mat);
            dir.add(force);
        }
        if (moveLeft) {
            transform.rot.saveToMatrix(mat);
            force.set(-1, 0, 0);
            force.applyProjection(mat);
            dir.add(force);
        }
        if (moveRight) {
            transform.rot.saveToMatrix(mat);
            force.set(1, 0, 0);
            force.applyProjection(mat);
            dir.add(force);
        }

        if (jump) {
            transform.rot.saveToMatrix(mat);
            force.set(0, 0, 1);
            force.applyProjection(mat);
            force = force.mult(Time.delta * 70);
            body.applyImpulse(force);
        }

        if (!moveForward && !moveBackward && !moveLeft && !moveRight && !jump) {
            transform.rot.saveToMatrix(mat);
            force.set(0, 0, -1);
            force.applyProjection(mat);
            force = force.mult(Time.delta * 3000 / 2);
			
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
