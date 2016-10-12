package armory.trait.internal;

import iron.Trait;
import iron.system.Input;
import iron.object.Transform;
import iron.object.CameraObject;
import armory.system.Keymap;

@:keep
class CameraController extends Trait {

#if (!arm_physics)
	public function new() { super(); }
#else

	var transform:Transform;
	var body:RigidBody;
	var camera:CameraObject;

	public function new() {
		super();

		Scene.active.notifyOnInit(initInternal);
	}
	
	function initInternal() {
		transform = object.transform;
		body = object.getTrait(RigidBody);
		camera = cast(object.getChildOfType(CameraObject), CameraObject);

		kha.input.Keyboard.get().notify(onDown, onUp);
	}

	var moveForward = false;
	var moveBackward = false;
	var moveLeft = false;
	var moveRight = false;
	var jump = false;
	function onDown(key: kha.Key, char: String) {
		if (char == Keymap.forward) moveForward = true;
		else if (char == Keymap.right) moveRight = true;
		else if (char == Keymap.backward) moveBackward = true;
		else if (char == Keymap.left) moveLeft = true;
		else if (char == Keymap.jump) jump = true;
	}

	function onUp(key: kha.Key, char: String) {
		if (char == Keymap.forward) moveForward = false;
		else if (char == Keymap.right) moveRight = false;
		else if (char == Keymap.backward) moveBackward = false;
		else if (char == Keymap.left) moveLeft = false;
	}
#end
}
