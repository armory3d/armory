package armory.logicnode;

import armory.system.Input;
import armory.trait.internal.NodeExecutor;

class InputDownNode extends BoolNode {

	var lastVal = false;

	public function new() {
		super();
	}

	public override function start(executor:NodeExecutor, parent:Node = null) {
		super.start(executor, parent);
		executor.notifyOnNodeUpdate(update);
	}

	function update() {
		if (lastVal != Input.down) {
			lastVal = val;
			val = Input.down;
			inputChanged();
		}
	}

	public static function create(value:Float) {
		var n = new InputDownNode();
		return n;
	}
}
