package cycles.trait;

import kha.Key;
import lue.Trait;
import lue.sys.Input;
import lue.sys.Time;
import lue.node.CameraNode;
import lue.node.RootNode;
import lue.math.Vec4;
import lue.math.Quat;

class FlyCamera extends Trait {

    var camera:CameraNode;

    var pitchRad:Float;

    var moveForward = false;
    var moveBackward = false;
    var strafeLeft = false;
    var strafeRight = false;
    var strafeForward = false;
    var strafeBackward = false;

    public function new() {
        super();

        kha.input.Keyboard.get().notify(onKeyDown, onKeyUp);

        requestInit(init);
        requestUpdate(update);
		requestRemove(removed);
    }
	
	function removed() {
		kha.input.Keyboard.get().remove(onKeyDown, onKeyUp);
	}

    function init() {
        camera = RootNode.cameras[0];

        var r = camera.transform.rot;
        var q = new Quat(r.x, r.y, r.z, r.w);
        q.inverse(q);

        var e = q.getEuler();
        pitchRad = lue.math.Math.degToRad(90) - e.x;
    }

    function update() {
		if (Input.occupied) return;

        var d = Time.delta * 5 / 2;

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

		// if (char == 'r') {lue.node.ModelNode._u1 += 0.01;trace("u1:", lue.node.ModelNode._u1);}
		// else if (char == 'f') {lue.node.ModelNode._u1 -= 0.01;trace("u1:", lue.node.ModelNode._u1);}
		// else if (char == 't') {lue.node.ModelNode._u2 += 0.01;trace("u2:", lue.node.ModelNode._u2);}
		// else if (char == 'g') {lue.node.ModelNode._u2 -= 0.01;trace("u2:", lue.node.ModelNode._u2);}
		// else if (char == 'y') {lue.node.ModelNode._u3 += 0.1;trace("u3:", lue.node.ModelNode._u3);}
		// else if (char == 'h') {lue.node.ModelNode._u3 -= 0.1;trace("u3:", lue.node.ModelNode._u3);}
		// else if (char == 'u') {lue.node.ModelNode._u4 += 0.1;trace("u4:", lue.node.ModelNode._u4);}
		// else if (char == 'j') {lue.node.ModelNode._u4 -= 0.1;trace("u4:", lue.node.ModelNode._u4);}
		// else if (char == 'i') {lue.node.ModelNode._u5 += 0.1;trace("u5:", lue.node.ModelNode._u5);}
		// else if (char == 'k') {lue.node.ModelNode._u5 -= 0.1;trace("u5:", lue.node.ModelNode._u5);}
		// else if (char == 'o') {lue.node.ModelNode._u6 += 0.005;trace("u6:", lue.node.ModelNode._u6);}
		// else if (char == 'l') {lue.node.ModelNode._u6 -= 0.005;trace("u6:", lue.node.ModelNode._u6);}
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
