package armory.trait;

import iron.Trait;
import iron.system.Input;
import iron.object.CameraObject;
import iron.math.Vec4;
import iron.math.Quat;

class ArcBallCamera extends Trait {

    var camera:CameraObject;
    var origin:Vec4;

    var pitchRad:Float;

    public function new() {
        super();

        origin = new Vec4();

        notifyOnInit(init);
        notifyOnUpdate(update);
    }

    function init() {
        camera = cast(object, CameraObject);

        var r = camera.transform.rot;
        var q = new Quat(r.x, r.y, r.z, r.w);
        q.inverse(q);

        var e = q.getEuler();
        pitchRad = 90 * (std.Math.PI / 180) - e.x;
    }

    function update() {

        if (Input.touch) {
            var dist = Vec4.distance3d(camera.transform.loc, origin);

            camera.move(camera.look(), dist);
            camera.rotate(camera.right(), pitchRad);

            camera.rotate(camera.look(), -Input.deltaX / 200);

            camera.rotate(camera.right(), -pitchRad);
            camera.move(camera.look(), -dist);

            camera.move(camera.look(), Input.deltaY / 50);
        }
    }
}
