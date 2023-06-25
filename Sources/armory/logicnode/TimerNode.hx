package armory.logicnode;

class TimerNode extends LogicNode {

	var time = 0.0;
	var duration = 0.0;
	var repeat = 0;
	var running = false;
	var repetitions = 0;

	public function new(tree: LogicTree) {
		super(tree);
	}

	function update() {
		time += iron.system.Time.delta;
		if (time >= duration) {
			repeat--;
			runOutput(0);
			if (repeat != 0) {
				time = 0;
				repetitions++;
			}
			else {
				removeUpdate();
				runOutput(1);
				time = 0;
				repetitions = 0;
			}
		}
	}

	override function run(from: Int) {
		if (from == 0) { // Start
			duration = inputs[3].get();
			repeat = inputs[4].get();
			if (!running) {
				running = true;
				tree.notifyOnUpdate(update);
			}
		}
		else if (from == 1) { // Pause
			removeUpdate();
		}
		else { // Stop
			removeUpdate();
			time = 0;
			repetitions = 0;
		}
	}

	inline function removeUpdate() {
		if (running) {
			running = false;
			tree.removeUpdate(update);
		}
	}

	override function get(from: Int): Dynamic {
		if (from == 2) return running;
		else if (from == 3) return time;
		else if (from == 4) return duration - time;
		else if (from == 5) return time / duration;
		else return repetitions;
	}
}
