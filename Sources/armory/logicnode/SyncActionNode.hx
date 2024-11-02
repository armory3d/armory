package armory.logicnode;

import kha.FastFloat;
import iron.object.Object;

class SyncActionNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var action1: String = inputs[2].get();
		var frame1A: Int = inputs[3].get();
		var frame1B: Int = inputs[4].get();
		var resetSpeed: Bool = inputs[5].get();
		var action2: String = inputs[6].get();
		var frame2A: Int = inputs[7].get();
		var frame2B: Int = inputs[8].get();

		assert(Error, object != null, "Object input cannot be null");

		var animation = object.animation;

		if(animation == null) animation = object.getBoneAnimation(object.uid);
		if(animation.activeActions == null) return;
		final act1 = animation.activeActions.get(action1);
		final act2 = animation.activeActions.get(action2);
		if(act1 == null || act2 == null) return;

		if(resetSpeed) act2.speed = 1.0;

		if(frame1A < 0) frame1A = 0;
		if(frame1B < 0) frame1B = act1.totalFrames;

		if(frame2A < 0) frame2A = 0;
		if(frame2B < 0) frame2B = act2.totalFrames;

		var slope = (frame2B - frame2A) / (frame1B - frame1A);
		var frameAct2 = Math.round(frame2A + slope * (act1.offset - frame1A));
		act1.speed = act2.speed / slope;
		act2.setFrameOffset(frameAct2);

		runOutput(0);
	}
}
