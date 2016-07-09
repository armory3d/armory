package armory.node;

class IntNode extends Node {

	public var i:Int;

	public function new() {
		super();
	}

	public static function create(_i:Int) {
		var n = new IntNode();
		n.i = _i;
		return n;
	}
}
