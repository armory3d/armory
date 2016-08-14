package armory.node;

import armory.trait.internal.NodeExecutor;

class ThisNode extends Node {

	public var target:iron.node.Node;

	public function new() {
		super();
	}

	public override function start(executor:NodeExecutor, parent:Node = null) {
		super.start(executor, parent);

		target = executor.node;
	}

	public static function create():ThisNode {
		var n = new ThisNode();
		return n;
	}
}
