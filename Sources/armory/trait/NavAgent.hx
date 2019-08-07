package armory.trait;

import iron.Trait;
import iron.math.Vec4;
import iron.math.Quat;
import iron.system.Tween;

class NavAgent extends Trait {

	@prop
	var speed:Float = 5;

	var path:Array<Vec4> = null;
	var index = 0;

	var rotAnim:TAnim = null;
	var locAnim:TAnim = null;

	public function new() {
		super();
	}

	public function setPath(path:Array<Vec4>) {
		stopTween();

		this.path = path;
		index = 1;
		notifyOnUpdate(update);

		go();
	}

	function stopTween() {
		if (rotAnim != null) Tween.stop(rotAnim);
		if (locAnim != null) Tween.stop(locAnim);
	}

	public function stop() {
		stopTween();
		path = null;
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
		var dist = Vec4.distance(object.transform.loc, p);

		orient.subvecs(p, object.transform.loc).normalize;
		var targetAngle = Math.atan2(orient.y, orient.x) + Math.PI / 2;
		locAnim = Tween.to({ target: object.transform.loc, props: { x: p.x, y: p.y , z: p.z }, duration: dist / speed, done: function() {
			index++;
			if (index < path.length) go();
			else removeUpdate(update);
		}});

		var q = new Quat();
		rotAnim = Tween.to({ target: object.transform, props: { rot: q.fromEuler(0, 0, targetAngle) }, duration: 0.4});
	}

	function update() {
		object.transform.buildMatrix();
	}
}
