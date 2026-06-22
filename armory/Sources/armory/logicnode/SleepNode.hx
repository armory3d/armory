package armory.logicnode;

import iron.system.Tween;

class SleepNode extends LogicNode {

	var sleepArray: Array<TAnim>;

	public function new(tree: LogicTree) {
		super(tree);

		sleepArray = new Array<TAnim>();
		tree.notifyOnRemove(stop);
	}

	override function run(from: Int) {
		var time: Float = inputs[1].get();
		var sleep = Tween.timer(time, done);
		sleepArray.push(sleep);
	}

	function done() {
		runOutput(0);
	}

	function stop() {
		for(sleep in sleepArray) {
			Tween.stop(sleep);
		}
	}
}
