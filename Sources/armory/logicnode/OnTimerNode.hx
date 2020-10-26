package armory.logicnode;

class OnTimerNode extends LogicNode {

	var duration = 0.0;
	var repeat = false;

	public function new(tree: LogicTree) {
		super(tree);

		tree.notifyOnUpdate(update);
	}

	function update() {

		if (duration <= 0.0) {
			duration = inputs[0].get();
			repeat = inputs[1].get();
		}

		duration -= iron.system.Time.delta;

		if (duration <= 0.0) {
			repeat ? runOutput(0): tree.removeUpdate(update);
		}
	}

	override function get(from: Int): Dynamic {
		return 1 - duration / inputs[0].get();
	}
}
