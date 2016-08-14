package armory.trait;

import kha.Key;
import iron.Trait;
import iron.Root;
import iron.sys.Input;
import iron.sys.Time;
import iron.node.CameraNode;
import iron.math.Vec4;
import iron.math.Quat;

class WalkNavigation extends Trait {

    var camera:CameraNode;

    var moveForward = false;
    var moveBackward = false;
    var strafeLeft = false;
    var strafeRight = false;
    var strafeForward = false;
    var strafeBackward = false;

    static inline var speed = 2.5;

    public function new() {
        super();

        kha.input.Keyboard.get().notify(onKeyDown, onKeyUp);

        notifyOnInit(init);
        notifyOnUpdate(update);
		notifyOnRemove(removed);
    }
	
	function removed() {
		kha.input.Keyboard.get().remove(onKeyDown, onKeyUp);
	}

    function init() {
        camera = Root.cameras[0];
    }

    function update() {
		if (Input.occupied) return;

        var d = Time.delta * speed;

        if (moveForward) {
            camera.move(camera.look(), d);
        }
        else if (moveBackward) {
            camera.move(camera.look(), -d);
        }
        if (strafeRight) {
            camera.move(camera.right(), d);
        }
        else if (strafeLeft) {
            camera.move(camera.right(), -d);
        }
		if (strafeForward) {
            var dir = new Vec4(0, 1, 0);
            camera.move(dir, -d);
        }
        else if (strafeBackward) {
            var dir = new Vec4(0, 1, 0);
            camera.move(dir, d);
        }

        if (Input.touch) {
            camera.rotate(Vec4.zAxis(), -Input.deltaX / 200);
            camera.rotate(camera.right(), -Input.deltaY / 200);
        }
    }

    function onKeyDown(key:Key, char:String) {
        if (char == 'w') moveForward = true;
        else if (char == 's') moveBackward = true;
        else if (char == 'a') strafeLeft = true;
        else if (char == 'd') strafeRight = true;
        else if (char == 'q') strafeForward = true;
        else if (char == 'e') strafeBackward = true;
    }

    function onKeyUp(key:kha.Key, char:String) {
        if (/*key == Key.UP ||*/ char == 'w') moveForward = false;
        else if (/*key == Key.DOWN ||*/ char == 's') moveBackward = false;
        else if (/*key == Key.LEFT ||*/ char == 'a') strafeLeft = false;
        else if (/*key == Key.RIGHT ||*/ char == 'd') strafeRight = false;
        else if (char == 'q') strafeForward = false;
        else if (char == 'e') strafeBackward = false;
    }
}
