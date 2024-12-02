package armory.trait;

import iron.Trait;
import iron.math.Vec4;
import iron.math.Quat;
import iron.system.Tween;

class NavAgent extends Trait {

	@prop
	public var speed: Float = 5;
	@prop
	public var turnDuration: Float = 0.4;
	@prop
	public var heightOffset: Float = 0.0;

	var path: Array<Vec4> = null;
	var index = 0;

	var rotAnim: TAnim = null;
	var locAnim: TAnim = null;

	public var tickPos: Null<Void -> Void>;
	public var tickRot: Null<Void -> Void>;

	public function new() {
		super();
		notifyOnRemove(stopTween);
	}

	public function setPath(path: Array<Vec4>) {
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

	function shortAngle(from: Float, to: Float): Float {
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
		locAnim = Tween.to({ target: object.transform.loc, props: { x: p.x, y: p.y, z: p.z + heightOffset }, duration: dist / speed, tick: tickPos, done: function() {
			index++;
			if (index < path.length) go();
			else removeUpdate(update);
		}});

		var q = new Quat();
		rotAnim = Tween.to({ target: object.transform, props: { rot: q.fromEuler(0, 0, targetAngle) }, tick: tickRot, duration: turnDuration});
	}

	function update() {
		object.transform.buildMatrix();
	}
}
