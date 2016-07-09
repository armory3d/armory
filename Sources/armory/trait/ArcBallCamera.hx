package armory.trait;

import iron.Trait;
import iron.sys.Input;
import iron.node.CameraNode;
import iron.node.RootNode;
import iron.math.Vec4;
import iron.math.Quat;

class ArcBallCamera extends Trait {

    var camera:CameraNode;
    var origin:Vec4;

    var pitchRad:Float;

    public function new() {
        super();

        origin = new Vec4();

        notifyOnInit(init);
        notifyOnUpdate(update);
    }

    function init() {
        camera = RootNode.cameras[0];

        var r = camera.transform.rot;
        var q = new Quat(r.x, r.y, r.z, r.w);
        q.inverse(q);

        var e = q.getEuler();
        pitchRad = iron.math.Math.degToRad(90) - e.x;
    }

    function update() {

        if (Input.touch) {
            var dist = iron.math.Math.distance3d(camera.transform.pos, origin);

            camera.move(camera.look(), dist);
            camera.rotate(camera.right(), pitchRad);

            camera.rotate(camera.look(), -Input.deltaX / 200);

            camera.rotate(camera.right(), -pitchRad);
            camera.move(camera.look(), -dist);

            camera.move(camera.look(), Input.deltaY / 50);
        }
    }
}
