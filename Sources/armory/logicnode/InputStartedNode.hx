package armory.logicnode;

import armory.system.Input;
import armory.trait.internal.NodeExecutor;

class InputStartedNode extends BoolNode {

	public function new() {
		super();
	}

	public override function start(executor:NodeExecutor, parent:Node = null) {
		super.start(executor, parent);
		executor.notifyOnNodeUpdate(update);
	}

	function update() {
		if (Input.started) {
			val = Input.started;
			inputChanged();
		}
		else if (val) {
			val = false;
			inputChanged();
		}
	}

	public static function create(value:Float) {
		var n = new InputStartedNode();
		return n;
	}
}
