package armory.logicnode;

import iron.system.Time;

class PulseNode extends LogicNode {

	var running = false;
	var interval: Float;
	var lastTick: Null<Float>;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		if (from == 0) {
			// Start
			interval = inputs[2].get();

			if (!running) {
				tree.notifyOnUpdate(update);
				running = true;
			}
		}
		else if (from == 1) {
			// Stop
			if (running) {
				tree.removeUpdate(update);
				running = false;
			}
		}
	}

	function update() {
		var tick = Time.time();

		if (lastTick == null || tick - lastTick > interval) {
			runOutput(0);
			lastTick = tick;
		}
	}
}
