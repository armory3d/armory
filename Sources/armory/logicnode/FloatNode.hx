package armory.logicnode;

class FloatNode extends Node {

	public var val:Float = 0.0;

	public function new() {
		super();
	}

	public static function create(f:Float) {
		var n = new FloatNode();
		n.val = f;
		return n;
	}
}
