package armory.logicnode;

import iron.system.Time;

class PulseNode extends LogicNode {

	var lastTick: Null<Float>;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var tick = Time.time();
		var interval: Float = inputs[2].get();

		if (from == 0) {
			// In
			if (lastTick != null && tick - lastTick < interval) {
				// Failed
				runOutput(1);

			}
			else {
				// Out
				lastTick = tick;
				runOutput(0);
			}
		}
		else if (from == 1) {
			// Reset
			lastTick = tick;
		}
	}
}
