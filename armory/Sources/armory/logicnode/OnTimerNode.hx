package armory.logicnode;

class OnTimerNode extends LogicNode {

	var duration = 0.0;
	var repeat = false;

	public function new(tree: LogicTree) {
		super(tree);

		tree.notifyOnUpdate(update);
	}

	function reactivate() {
		if (inputs[1].get() == true){
			tree.notifyOnUpdate(update);
			tree.removeUpdate(reactivate);
		}
	}

	function update() {

		if (duration <= 0.0) {
			duration = inputs[0].get();
			repeat = inputs[1].get();
		}

		duration -= iron.system.Time.delta;
		if (duration <= 0.0) {
			if (!repeat) { tree.removeUpdate(update); tree.notifyOnUpdate(reactivate); }
			runOutput(0);
		}
	}
}
