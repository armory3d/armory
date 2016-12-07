package armory.trait;

import iron.Trait;
import iron.math.Vec4;
import iron.math.Quat;
import iron.system.Tween;

@:keep
class NavAgent extends Trait {

	var path:Array<Vec4> = null;
	var index = 0;
	var angle:Float;

	public function new() {
		super();
	}

	public function setPath(path:Array<Vec4>) {
		Tween.stop(object.transform.loc);

		this.path = path;
		index = 1;
		notifyOnUpdate(update);

		go();
	}

	function shortAngle(from:Float, to:Float) {
		if (from < 0) from += Math.PI * 2;
		if (to < 0) to += Math.PI * 2;
		var delta = Math.abs(from - to);
		if (delta > Math.PI) to = Math.PI * 2 - delta;
		return to;
	}

	var orient = new Vec4();
	function go() {
		if (path == null || index >= path.length) return;

		var p = path[index];
		var dist = Vec4.distance3d(object.transform.loc, p);
		var speed = 0.2;

		orient.subvecs(p, object.transform.loc).normalize;
		var targetAngle = Math.atan2(orient.y, orient.x) + Math.PI / 2;
		var currentAngle = object.transform.rot.toAxisAngle(Vec4.zAxis());
		angle = currentAngle;
		Tween.to(this, 0.4, { angle: targetAngle }, null, 0, 0);

		Tween.to(object.transform.loc, dist * speed, { x: p.x, y: p.y /*, z: p.z*/ }, function() {
			index++;
			if (index < path.length) go();
			else removeUpdate(update);
		}, 0, 0);
	}

	function update() {
		// object.transform.dirty = true;
		object.transform.rot.fromAxisAngle(Vec4.zAxis(), angle);
		object.transform.buildMatrix();
	}
}
