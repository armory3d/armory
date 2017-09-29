package armory.trait.internal;

import iron.Trait;
import iron.system.Input;
import iron.object.Transform;
import iron.object.CameraObject;
import armory.trait.physics.RigidBody;

class CameraController extends Trait {

#if (!arm_physics)
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

		Scene.active.notifyOnInit(function() {
			transform = object.transform;
			body = object.getTrait(RigidBody);
			camera = cast(object.getChildOfType(CameraObject), CameraObject);
		});

		notifyOnUpdate(function() {
			var keyboard = Input.getKeyboard();
			moveForward = keyboard.down("w");
			moveRight = keyboard.down("d");
			moveBackward = keyboard.down("s");
			moveLeft = keyboard.down("a");
			jump = keyboard.down("space");
		});
	}
#end
}
