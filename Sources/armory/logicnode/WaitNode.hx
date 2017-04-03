package armory.logicnode;

class WaitNode extends Node {

	public function new(trait:armory.Trait) {
		super(trait);
	}

	override function run() {
		var time = inputs[1].get();
		armory.system.Tween.timer(time, done);
	}

	function done() {
		super.run();
	}
}
