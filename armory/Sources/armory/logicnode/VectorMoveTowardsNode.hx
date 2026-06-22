package armory.logicnode;

import kha.FastFloat;
import iron.math.Vec4;
import iron.system.Time;
import armory.math.Helper;

class VectorMoveTowardsNode extends LogicNode {

	var reference = new Vec4();
	var current = new Vec4();
	var target = new Vec4();

	var endFrame = false;

	public function new(tree: LogicTree) {
		super(tree);

		tree.notifyOnUpdate(function() {
			endFrame = false;
		});
	}

	override function get(from: Int): Dynamic {
		if (!endFrame) { // Update once per frame
			var v1: Vec4 = inputs[0].get();
			var v2: Vec4 = inputs[1].get();
			var delta: FastFloat = inputs[2].get();
	
			if (v1 == null || v2 == null || delta == null) return null;
	
			if (!reference.equals(v1)) {
				// Current vector changed
				reference.setFrom(v1);
				current.setFrom(v1);
			}
	
			target.setFrom(v2);
			current = Helper.moveTowards(current, target, delta);

			endFrame = true;
		}

		return current;
	}
}
