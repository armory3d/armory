package armory.logicnode;

class OnTimerNode extends Node {

	var duration = 0.0;
	var repeat = false;

	public function new(tree:LogicTree) {
		super(tree);

		tree.notifyOnUpdate(update);
	}

	function update() {

		if (duration <= 0.0) {
			duration = inputs[0].get();
			repeat = inputs[1].get();
		}

		duration -= armory.system.Time.delta;
		if (duration <= 0.0) {
			if (!repeat) tree.removeUpdate(update);
			run();
		}
	}
}
