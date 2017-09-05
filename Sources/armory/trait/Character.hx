package armory.trait;

import iron.object.Object;
import iron.Trait;
import iron.system.Input;
import iron.math.Vec4;
import iron.math.Quat;

class Character extends Trait {

	var speed = 0.0;
	var actionIdle:String;
	var actionMove:String;

	var loc:Vec4 = new Vec4();
	var lastLoc:Vec4 = null;
	var state = 0;

	public function new(actionIdle:String, actionMove:String) {
		super();

		this.actionIdle = actionIdle;
		this.actionMove = actionMove;

		notifyOnInit(init);
		notifyOnUpdate(update);
	}

	function init() {
		object.animation.pause();
	}

	function update() {
		var tr = object.transform;
		loc.set(tr.worldx(), tr.worldy(), tr.worldz());

		if (lastLoc == null) lastLoc = new Vec4(loc.x, loc.y, loc.z);

		speed = Vec4.distance3d(loc, lastLoc);
		lastLoc.setFrom(loc);

		if (state == 0 && speed > 0) {
			state = 1;
			object.animation.play(actionMove);
		}
		else if (state == 1 && speed == 0) {
			state = 0;
			object.animation.pause();
			// object.animation.play(actionIdle);
		}
	}
}
