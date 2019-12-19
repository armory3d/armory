package armory.trait;

import iron.object.Object;
import iron.object.Animation;
import iron.Trait;
import iron.system.Input;
import iron.math.Vec4;
import iron.math.Quat;

class Character extends Trait {

	var currentAction: String;
	var animation: Animation;

	var speed = 0.0;
	var loc: Vec4 = new Vec4();
	var lastLoc: Vec4 = null;
	var framesIdle = 0; // Number of frames character did not move

	@:prop
	var actionIdle: String = "idle";

	@:prop
	var actionMove: String = "run";

	public function new() {
		super();

		currentAction = actionIdle;
		notifyOnInit(init);
	}

	function init() {
		animation = object.animation;

		// Try first child if we are running from armature
		if (animation == null) {
			if (object.children.length > 0) {
				animation = object.children[0].animation;
			}
		}

		if (animation == null) return;
		notifyOnUpdate(update);
	}

	function update() {
		// Get current position
		var tr = object.transform;
		loc.set(tr.worldx(), tr.worldy(), tr.worldz());

		// Set previous position to current position if there is no previous position
		if (lastLoc == null) lastLoc = new Vec4(loc.x, loc.y, loc.z);

		// Check if character moved compared from last position
		speed = Vec4.distance(loc, lastLoc);

		// Update previous position to current position
		// in preparation for next check
		lastLoc.setFrom(loc);

		if (speed == 0) framesIdle++;
		else framesIdle = 0;

		// If state is idle and character is in movement, play move walk animation
		if (currentAction == actionIdle && framesIdle == 0) {
			currentAction = actionMove;

			if (actionMove != null) animation.play(actionMove);
		}
		else if (currentAction == actionMove && framesIdle > 2) { // Otherwise if state is walking and character is idle, play idle animation
			currentAction = actionIdle;

			if (actionIdle != null) animation.play(actionIdle);
		}
	}
}
