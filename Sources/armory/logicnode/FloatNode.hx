package armory.logicnode;

class FloatNode extends Node {

	public var f:Float;

	public function new() {
		super();
	}

	public static function create(_f:Float) {
		var n = new FloatNode();
		n.f = _f;
		return n;
	}
}
