package armory.trait;

import iron.object.Object;
import iron.object.Animation;
import iron.Trait;
import iron.system.Input;
import iron.math.Vec4;
import iron.math.Quat;

class Character extends Trait {

	var actionIdle:String;
	var actionMove:String;
	var animation:Animation;

	var delta = 0.0;
	var loc:Vec4 = new Vec4();
	var lastLoc:Vec4 = null;
	var state = 0; // Idle, walking

	public function new(actionIdle:String, actionMove:String) {
		super();

		this.actionIdle = actionIdle;
		this.actionMove = actionMove;

		notifyOnInit(init);
		notifyOnUpdate(update);
	}

	function init() {
		animation = object.animation;

		// Try first child if we are running from armature
		if (animation == null) animation = object.children[0].animation;

		animation.pause();
	}

	function update() {
		var tr = object.transform;
		loc.set(tr.worldx(), tr.worldy(), tr.worldz());

		if (lastLoc == null) lastLoc = new Vec4(loc.x, loc.y, loc.z);

		delta = Vec4.distance3d(loc, lastLoc);
		lastLoc.setFrom(loc);

		// Character started to move
		if (state == 0 && delta > 0) {
			state = 1;
			animation.play(actionMove);
		}
		// Character just stopped moving
		else if (state == 1 && delta == 0) {
			state = 0;
			animation.pause();
		}
	}
}
