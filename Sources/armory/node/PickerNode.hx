package armory.node;

import armory.trait.internal.NodeExecutor;

class PickerNode extends Node {

	public var target:iron.node.Node;
	public var property0:String;

	public function new() {
		super();
	}

	public override function start(executor:NodeExecutor, parent:Node = null) {
		super.start(executor, parent);
		executor.notifyOnNodeInit(init);
	}

	function init() {
		target = iron.Root.root.getChild(property0);
	}

	public static function create(_property0:String):PickerNode {
		var n = new PickerNode();
		n.property0 = _property0;
		return n;
	}
}
