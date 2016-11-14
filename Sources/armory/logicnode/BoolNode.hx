package armory.logicnode;

class BoolNode extends Node {

	public var val:Bool;

	public function new() {
		super();
	}

	public static function create(b:Bool) {
		var n = new BoolNode();
		n.val = b;
		return n;
	}
}
