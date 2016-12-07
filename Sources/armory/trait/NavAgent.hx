package armory.trait;

import iron.Trait;
import iron.math.Vec4;
import iron.system.Tween;

@:keep
class NavAgent extends Trait {

	var path:Array<Vec4> = null;
	var index = 0;

	public function new() {
		super();
	}

	public function setPath(path:Array<Vec4>) {
		this.path = path;
		index = 1;
		notifyOnUpdate(update);

		go();
	}

	function go() {
		if (path == null || index >= path.length) return;
		var p = path[index];
		var dist = Vec4.distance3d(object.transform.loc, p);
		var speed = 0.2;
		Tween.to(object.transform.loc, dist * speed, { x: p.x, y: p.y /*, z: p.z*/ }, function() {
			index++;
			if (index < path.length) go();
		}, 0, 0);
	}

	function update() {
		object.transform.dirty = true;
	}
}
