package armory.logicnode;

class TimerNode extends LogicNode {

	var duration = 0.0;
	var initialDuration = 0.0;
	var repeat = 0;
	var running = false;
	var repetitions = 0;

	public function new(tree:LogicTree) {
		super(tree);
	}

	function update() {
		duration -= iron.system.Time.delta;
		if (duration <= 0.0) {
			repeat--;
			if (repeat != 0) {
				duration = initialDuration;
				repetitions++;
			}
			else {
				running = false;
				tree.removeUpdate(update);
			}
			super.runOutputs(0);
		}
	}
	
	override function run() {
		initialDuration = inputs[3].get();
		repeat = inputs[4].get();
		
		running = true;
		duration = initialDuration;
		repetitions = 0;
		tree.notifyOnUpdate(update);
	}

	override function get(from:Int):Dynamic {
		if (from == 1) return running;
		else if (from == 2) return initialDuration - duration;
		else if (from == 3) return duration;
		else if (from == 4) return (1.0 - (duration / initialDuration));
		else return repetitions;
	}
}
