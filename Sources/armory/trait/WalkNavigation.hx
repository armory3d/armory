package armory.trait;

import kha.Key;
import iron.Trait;
import iron.system.Input;
import iron.system.Time;
import iron.object.CameraObject;
import iron.math.Vec4;
import iron.math.Quat;

class WalkNavigation extends Trait {

    static inline var speed = 5.0;

    var camera:CameraObject;

    var moveForward = false;
    var moveBackward = false;
    var strafeLeft = false;
    var strafeRight = false;
    var strafeUp = false;
    var strafeDown = false;
    var shift = 1.0;
    var alt = 1.0;

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
        camera = cast(object, CameraObject);
    }

    function update() {
		if (Input.occupied) return;

        var d = Time.delta * speed * shift * alt;

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
		if (strafeUp) {
            var dir = new Vec4(0, 0, 1);
            camera.move(dir, -d);
        }
        else if (strafeDown) {
            var dir = new Vec4(0, 0, 1);
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
        else if (char == 'q') strafeUp = true;
        else if (char == 'e') strafeDown = true;
        else if (key == Key.SHIFT) shift = 2.0;
        else if (key == Key.ALT) alt = 0.5;
    }

    function onKeyUp(key:kha.Key, char:String) {
        if (/*key == Key.UP ||*/ char == 'w') moveForward = false;
        else if (/*key == Key.DOWN ||*/ char == 's') moveBackward = false;
        else if (/*key == Key.LEFT ||*/ char == 'a') strafeLeft = false;
        else if (/*key == Key.RIGHT ||*/ char == 'd') strafeRight = false;
        else if (char == 'q') strafeUp = false;
        else if (char == 'e') strafeDown = false;
        else if (key == Key.SHIFT) shift = 1.0;
        else if (key == Key.ALT) alt = 1.0;
    }
}
