package armory.logicnode;

import armory.system.Input;
import armory.trait.internal.NodeExecutor;

class InputCoordsNode extends VectorNode {

	public var x:Float;
	public var y:Float;

	public function new() {
		super();
	}

	public override function start(executor:NodeExecutor, parent:Node = null) {
		super.start(executor, parent);
	}

	public override function fetch() {
		x = Input.x;
		y = Input.y;
	}

	public static function create(value:Float) {
		var n = new InputCoordsNode();
		return n;
	}
}
