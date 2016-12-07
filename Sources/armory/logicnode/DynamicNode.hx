package armory.logicnode;

class DynamicNode extends Node {

	public var val:Dynamic;

	public function new() {
		super();
	}

	public static function create(d:Dynamic) {
		var n = new DynamicNode();
		n.val = d;
		return n;
	}
}
