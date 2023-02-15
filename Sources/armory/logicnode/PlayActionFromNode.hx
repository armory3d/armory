package armory.logicnode;

import iron.object.Animation;
import iron.object.Object;
import iron.Scene;

class PlayActionFromNode extends LogicNode {

	var animation: Animation;
	var startFrame: Int;
	var endFrame: Int = -1;
	var loop: Bool;

	public function new(tree: LogicTree) {
		super(tree);
		tree.notifyOnUpdate(update);
	}
	
	function update() {
		if (animation != null) {
			if (animation.currentFrame() == endFrame) {
				if (loop) animation.setFrame(startFrame);
				else {
					if (!animation.paused) {
						animation.pause();
						runOutput(1);
					}
				}
			}
		}
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var action: String = inputs[2].get();
		startFrame = inputs[3].get();
		endFrame = inputs[4].get();
		var blendTime: Float = inputs[5].get();
		var speed: Float = inputs[6].get();
		loop = inputs[7].get();
		
		if (object == null) return;
		animation = object.animation;
		if (animation == null) animation = object.getParentArmature(object.name);

		animation.play(action, function() {
			runOutput(1);
		}, blendTime, speed, loop);
		animation.update(startFrame * Scene.active.raw.frame_time);

		runOutput(0);
	}
}
