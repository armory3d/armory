package cycles.node;

class StringNode extends Node {

	public var s:String;

	public function new() {
		super();
	}

	public static function create(_s:String) {
		var n = new StringNode();
		n.s = _s;
		return n;
	}
}
