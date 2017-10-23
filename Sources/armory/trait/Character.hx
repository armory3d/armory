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

	var speed = 0.0;
	var loc:Vec4 = new Vec4();
	var lastLoc:Vec4 = null;
	var state = 0; // Idle, walking

	public function new(actionIdle:String, actionMove:String) {
		super();

		if(actionIdle != null && actionMove != null){
			this.actionIdle = actionIdle;
			this.actionMove = actionMove;
		}
		
		notifyOnInit(init);
		notifyOnUpdate(update);
	}

	function init() {
		animation = object.animation;

		// Try first child if we are running from armature
		if (animation == null){
			if(object.children.length > 0) {
				animation = object.children[0].animation;
			}
		}

		// null check animation
		if(animation != null) {
			animation.pause();
		}
	}

	function update() {
		// get current position
		var tr = object.transform;
		loc.set(tr.worldx(), tr.worldy(), tr.worldz());

		// set previous position to current position if there is no previous position
		if (lastLoc == null) lastLoc = new Vec4(loc.x, loc.y, loc.z);

		// check if character moved compared from last position
		speed = Vec4.distance3d(loc, lastLoc);

		// update previous position to current position
		// in preparation for next check
		lastLoc.setFrom(loc);

		// if state is zero (idle) and speed is greater than zero, play move walk animation
		if (state == 0 && speed > 0) {
			state = 1;

			// null check animation and actionMove
			if(animation != null && actionMove != null){
				animation.play(actionMove);
			}
		}

		// otherwise if state is one (walking) and speed equals zero, pause the walk animation
		else if (state == 1 && speed == 0) {
			state = 0;

			// null check animation
			if(animation != null){
				animation.pause();
			}
		}
	}
}
