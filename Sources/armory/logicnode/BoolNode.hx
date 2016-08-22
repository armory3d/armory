package armory.logicnode;

class BoolNode extends Node {

	public var b:Bool;

	public function new() {
		super();
	}

	public static function create(_b:Bool) {
		var n = new BoolNode();
		n.b = _b;
		return n;
	}
}
