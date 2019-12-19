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

	var transform: Transform;
	var body: RigidBody;
	var camera: CameraObject;

	var moveForward = false;
	var moveBackward = false;
	var moveLeft = false;
	var moveRight = false;
	var jump = false;

	public function new() {
		super();

		iron.Scene.active.notifyOnInit(function() {
			transform = object.transform;
			body = object.getTrait(RigidBody);
			camera = cast(object.getChildOfType(CameraObject), CameraObject);
		});

		notifyOnUpdate(function() {
			var keyboard = Input.getKeyboard();
			moveForward = keyboard.down(keyUp);
			moveRight = keyboard.down(keyRight);
			moveBackward = keyboard.down(keyDown);
			moveLeft = keyboard.down(keyLeft);
			jump = keyboard.started("space");
		});
	}

	#if arm_azerty
	static inline var keyUp = "z";
	static inline var keyDown = "s";
	static inline var keyLeft = "q";
	static inline var keyRight = "d";
	static inline var keyStrafeUp = "e";
	static inline var keyStrafeDown = "a";
	#else
	static inline var keyUp = "w";
	static inline var keyDown = "s";
	static inline var keyLeft = "a";
	static inline var keyRight = "d";
	static inline var keyStrafeUp = "e";
	static inline var keyStrafeDown = "q";
	#end
#end
}
